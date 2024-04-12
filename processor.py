from NumberPlateDetection.detector import NumberPlateDetector
from face_fin import ImageProcessor
from telegram_sender import send_msg


class Processor():
    def __init__(self) -> None:
        self.__image_processor = ImageProcessor()
        self.__number_plate_detector = NumberPlateDetector()


    def process(self, orig_image_path: str, bounding_box_filename:str, label):

        print(label)
        if label == "Mobile Phone":
            collage_path, face_records = self.__image_processor.process_image(orig_image_path, bounding_box_filename)
            send_msg(bounding_box_filename, collage_path, label, None, face_records)
        
        elif label == "Sleeping":
            collage_path, face_records = self.__image_processor.process_image(orig_image_path, bounding_box_filename)
            send_msg(bounding_box_filename, collage_path, label, None, face_records)
        
        elif label == "Violence":
            collage_path, face_records = self.__image_processor.process_image(orig_image_path, bounding_box_filename)
            send_msg(bounding_box_filename, collage_path, label, None, face_records)

        elif label == "No Helmet":
            number_plate_record, _ , coordinates = self.__number_plate_detector.detect(orig_image_path, bounding_box_filename)
            collage_path, face_records = self.__image_processor.process_image(orig_image_path, None, coordinates)
            send_msg(bounding_box_filename, collage_path, label, number_plate_record, face_records)

        elif label == "Triples":
            number_plate_record, _, coordinates = self.__number_plate_detector.detect(orig_image_path, bounding_box_filename)
            collage_path, face_records = self.__image_processor.process_image(orig_image_path, bounding_box_filename, coordinates)
            send_msg(bounding_box_filename, collage_path, label, number_plate_record, face_records)
