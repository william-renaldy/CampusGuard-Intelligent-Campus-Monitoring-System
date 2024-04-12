print("Importing")

from queue import Queue
import shutil
import threading
from streamlit_webrtc import webrtc_streamer
from ultralytics import YOLO
import cv2
import logging
import os
import time
import streamlit as st
import av
from moviepy.editor import ImageSequenceClip

from processor import Processor
from NumberPlateDetection.detector import NumberPlateDetector


from utility import CLASSES, COLORS



class Demo():

    def __init__(self) -> None:
        st.title("Campus Guard Demo")
        
        self.__detector = NumberPlateDetector()
        self.__processor = Processor()
        
        self.__model = YOLO(r"best1.pt")
        self.__output_folder = "CapturedFrames"
        self.__temp_dir = "temp"
        self.__thread_queue = Queue()
        self.__max_threads = 5
        self.__cropped_frame_dir = "CroppedFrames"
        self.__done = False

        os.makedirs(self.__output_folder, exist_ok=True)
        os.makedirs(self.__temp_dir, exist_ok=True)
        os.makedirs(self.__cropped_frame_dir, exist_ok=True)

        print("done")

    def __process_frame(self, frame, box):

        x1, y1, x2, y2 = box.boxes.xyxy[0].cpu().numpy()

        class_id = box.boxes.cls[0].cpu().numpy().item()
        label = CLASSES[class_id]  # Map ID to label
        conf = box.boxes.conf[0].cpu().numpy().item()
        color = COLORS[class_id]

        # Draw bounding box
        timestamp = time.strftime("%Y%m%d%H%M%S")
        cropped_frame = frame[:, int(x1):int(x2)]

        # Save the cropped frame
        cropped_path = os.path.join(self.__cropped_frame_dir, f"Cropped_frame_{timestamp}.jpg")
        cv2.imwrite(cropped_path, cropped_frame)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

        # Add label with optional confidence score
        text = f"{label}: {conf:.2f}"  # Format confidence score

        # Calculate label placement (adjust as needed)
        offset = 5  # Adjust offset based on text size and box size
        text_width, text_height = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        x_text = int(x1 + offset)
        y_text = int(y1 + offset + text_height)

        cv2.putText(frame, text, (x_text, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        return conf, label, cropped_path
    
    def __process_queue(self):
        while True:
            orig_frame_path, image_filename, label = self.__thread_queue.get()
            self.__processor.process(orig_frame_path, image_filename, label)
            self.__thread_queue.task_done()

            if self.__thread_queue.empty() and self.__done:
                break


    def __process_video(self, video_path: str):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("Error opening video:")
            return

        count = 1
        detection_start_time = None
        continuous_detection_threshold = 2
        thread = None

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            original_log_level = logging.getLogger().getEffectiveLevel()
            logging.disable(logging.CRITICAL)

            timestamp = time.strftime("%Y%m%d%H%M%S")

            orig_frame_path = os.path.join(self.__temp_dir, f"original_image_{timestamp}.jpg")
            cv2.imwrite(orig_frame_path, frame)

            results = self.__model(frame)[0]

            logging.disable(original_log_level)

            for box in results:
                conf, label, cropped_path = self.__process_frame(frame, box)

                if conf > 0.3:
                    if detection_start_time is None:
                        detection_start_time = time.time()
                    else:
                        elapsed_time = time.time() - detection_start_time
                        if elapsed_time >= continuous_detection_threshold:
                            print(f"Continuous detection for {continuous_detection_threshold} seconds!")
                            detection_start_time = None

                            image_filename = os.path.join(self.__output_folder, f"detected_image_{timestamp}_{count}.jpg")
                            cv2.imwrite(image_filename, frame)
                            count += 1

                            self.__thread_queue.put((orig_frame_path, image_filename, label))

            # cv2.imshow("YOLOv8 Video", frame)
            yield frame

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        self.__done = True



    def __process_image(self, image_path: str):
        
        frame = cv2.imread(image_path)

        original_log_level = logging.getLogger().getEffectiveLevel()
        logging.disable(logging.CRITICAL)

        results = self.__model(frame)[0]

        logging.disable(original_log_level)
        
        for box in results:
            conf = self.__process_frame(frame, box)

        timestamp = time.strftime("%Y%m%d%H%M%S")
        image_filename = os.path.join(self.__output_folder, f"detected_image_{timestamp}.jpg")
        
        cv2.imwrite(image_filename, frame)
        self.__detector.detect(image_path, image_filename)
 

    def detect(self):

        queue_thread = threading.Thread(target=self.__process_queue)
        queue_thread.daemon = True
        queue_thread.start()

        image_container = st.empty()

        count = 1
        detection_start_time = None
        continuous_detection_threshold = 2


        
        st.sidebar.title("Capture or Upload video")
        file_type = st.sidebar.radio("Select file type:", ("Upload", "Live Camera"))

        if file_type == "Upload":
            uploaded_file = st.file_uploader("Upload file", type=["mp4", "avi"])

            if uploaded_file:
                os.makedirs("test", exist_ok = True)
                file_name = os.path.join("test", "video.mp4")

                with open(file_name, "wb") as f:
                    f.write(uploaded_file.read())

                is_video = file_name.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))
                is_image = file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))

                if is_image:
                    self.__process_image(file_name)


                if is_video:
                    # video_thread = threading.Thread(target=self.__process_video, args=(file_name,))
                    # video_thread.start()

                    x = self.__process_video(file_name)
                    

                    try:
                        while True:
                            rgb_frame = cv2.cvtColor(next(x), cv2.COLOR_BGR2RGB)
                            # rgb_frame = cv2.resize(rgb_frame, (240, 240))
                            image_container.image(rgb_frame, channels="RGB", use_column_width=True)
                            
                    except StopIteration:
                        pass
                    
        if file_type == "Live Camera":
            video_frames = []

            def video_frame_callback(frame):
                frame = frame.to_ndarray(format="bgr24")


                original_log_level = logging.getLogger().getEffectiveLevel()
                logging.disable(logging.CRITICAL)

                timestamp = time.strftime("%Y%m%d%H%M%S")

                orig_frame_path = os.path.join(self.__temp_dir, f"original_image_{timestamp}.jpg")
                cv2.imwrite(orig_frame_path, frame)

                results = self.__model(frame)[0]

                logging.disable(original_log_level)

                for box in results:
                    conf, label, cropped_path = self.__process_frame(frame, box)

                    if conf > 0.3:
                        if detection_start_time is None:
                            detection_start_time = time.time()
                        else:
                            elapsed_time = time.time() - detection_start_time
                            if elapsed_time >= continuous_detection_threshold:
                                print(f"Continuous detection for {continuous_detection_threshold} seconds!")
                                detection_start_time = None

                                image_filename = os.path.join(self.__output_folder, f"detected_image_{timestamp}_{count}.jpg")
                                cv2.imwrite(image_filename, frame)
                                count += 1

                                self.__thread_queue.put((orig_frame_path, image_filename, label))

                # cv2.imshow("YOLOv8 Video", frame)
                video_frames.append(frame)
                return av.VideoFrame.from_ndarray(frame, format="bgr24")

            def save_video(frames, output_path=r"UploadedFile\video.mp4", fps=30):
                
                os.makedirs("UploadedFile", exist_ok=True)

                # Convert frames from BGR to RGB
                frames_rgb = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in frames]
                
                # Create a clip from the list of frames
                clip = ImageSequenceClip(frames_rgb, fps=fps)
                
                # Write the clip to a video file
                clip.write_videofile(output_path, fps=fps)
                
                return output_path

            def on_stop_callback():
                saved_video_path = save_video(video_frames)
                print("Video saved to:", saved_video_path)
                del video_frames[:]

            webrtc_streamer(
                key="example",
                video_frame_callback=video_frame_callback,
                on_video_ended=on_stop_callback
            )

            

            queue_thread.join()
            print("Completed")

            shutil.rmtree(self.__temp_dir)
            print(f"Folder '{self.__temp_dir}' deleted.")
            
            shutil.rmtree(self.__cropped_frame_dir)
            print(f"Folder '{self.__cropped_frame_dir}' deleted.")



        

if __name__ == "__main__":
    # file_name = r"SampleVideos\WhatsApp Video 2024-03-08 at 14.52.35_b301fe9b.mp4"
    # file_name = r"SampleVideos\WhatsApp Video 2024-03-08 at 21.18.26_be95da27.mp4"
    d = Demo()
    
    d.detect()