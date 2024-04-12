import datetime
import time
import requests
import os
from dotenv import load_dotenv
import geocoder

from data_uploader import upload

load_dotenv()



def get_location(class_name: str):

    if class_name in ["Triples", "No Helmet"]:
        return "E-Gate"
    elif class_name == "Mobile Phone":
        return "AD Department round table"
    else:
        return "AD Classroom"




def send_msg(bounding_img_path, collage_img_path, class_name, number_plate_details = None, face_details = None):
    token = os.getenv("TELEGRAM_TOKEN")
    location = get_location(class_name)
    text = f"Warning! {class_name} Detected. Location: {location}"

    if bounding_img_path is None:
        Bounding_img = None
    else:
        with open(bounding_img_path, "rb") as bounding_image_file:
            Bounding_img = bounding_image_file.read()
    
    if collage_img_path is None:
        Collage_img = None
    else:
        with open(collage_img_path, "rb") as collage_image_file:
            Collage_img = collage_image_file.read()

    values=[]

    timestamp = datetime.datetime.now().strftime("%b %d, %Y %I:%M:%S %p")
    if class_name in ["Triples", "No Helmet"]:
        if number_plate_details:
            text += f"""\n
            Details from Number Plate:
            Vehicle Number: {number_plate_details["Vehicle Number"]}
            Student Roll Number: {number_plate_details["Roll Number"]}
            Student Name: {number_plate_details["Matching Name"]}
            Student Department: {number_plate_details["Department"]}
            """
            value=["Number Plate", number_plate_details["Matching Name"], number_plate_details["Roll Number"], 
                    number_plate_details["Department"], number_plate_details["Vehicle Number"], class_name, 
                    location, Bounding_img, Collage_img, timestamp]
            
            values.append(value)

    if face_details:
        if any(face_details):
            text += "\nDetails from Face Matching\n"

        for i in range(len(face_details)):

            details = face_details[i]

            if details is None:
                continue

            text += f"""
            Student {i + 1}
            Student Roll Number: {details["Roll Number"]}
            Student Name: {details["Matching Name"]}
            Student Department: {details["Department"]}
            """

            value=["Face Matching", details["Matching Name"], details["Roll Number"], 
                    details["Department"], None, class_name, location, Bounding_img, Collage_img, timestamp]
            
            values.append(value)

    if len(values) == 0:
        values.append([None, None, None, None, None, class_name, location, Bounding_img, Collage_img, timestamp])
    upload(values)
    
    # print (values)

    # 1214661913 - Vishal
    # 1800886125 - William
    # 2087668156 - Iniyan
    # 1346063520 - Suresh
    # 1868149513 - Tharun
            
    # ids = ["1346063520", "1800886125", "1214661913", "1868149513", "2087668156"]
    # ids = [ "1800886125", "1346063520", "1214661913"]
    ids = [ "1214661913"]

    for id in ids:
        try:
            files = {}
            
            # Read and add bounding image
            if Bounding_img:
                files["photo"] = Bounding_img
                
                response1 = requests.post(
                    f"https://api.telegram.org/bot{token}/sendPhoto", files=files, data={"chat_id": id}
                )
            else:
                response1 = None

            # Read and add collage image
            if Collage_img:
                files["photo"] = Collage_img

                response2 = requests.post(
                    f"https://api.telegram.org/bot{token}/sendPhoto", files=files, data={"chat_id": id}
                )
            else:
                response2 = None

            data = {"chat_id": id, "text": text}
            response3 = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage", params=data
            )

            print(f"Alert sent successfully to {id}!", response1, response2, response3)
        except Exception as e:
            print(f"Error sending message to {id}: {e}")
    

def listToString(s): 
    float_string = ""
    for num in s:
        float_string = float_string + str(num) + " "

    return float_string

if __name__ == "__main__":

    details = {
        "Roll Number": "21AD058",
        "Vehicle Number": "TN 39 CJ 0579",
        "Matching Name": "Vijay Akash V",
        "Department": "AD"

    }
    send_msg(r"WhatsApp Image 2024-03-22 at 10.49.45_c74ef7e6.jpg", r"WhatsApp Image 2024-03-22 at 17.33.32_bb32ca1c.jpg", "No Helmet", number_plate_details = details, face_details=[details])