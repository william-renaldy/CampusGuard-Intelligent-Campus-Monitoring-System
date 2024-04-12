import datetime
import threading
import time
import cv2
import requests
from fuzzywuzzy import fuzz
import os
from dotenv import load_dotenv
from face_fin import ImageProcessor


load_dotenv()

from .utility import get_df

token = os.getenv("TOKEN")

class NumberPlateDetector():
    def __init__(self) -> None:
        
        self.regions = ["in"]

        self.orig_df = get_df()
        self.__image_processor = ImageProcessor()

        self.original_plate = self.orig_df['vehicle_number'].astype(str).tolist()



    def __get_response(self, image_path: str) -> dict:

        with open(image_path, 'rb') as fp:
            response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                data=dict(regions = self.regions),
                files=dict(upload=fp),
                headers={'Authorization': token})


        return response.json()

    def __get_best(self, candidates: list[dict[str, float]]) -> str | None:
         
        best_match = None
        best_score = 0

        # Iterate over each original plate and find the best fuzzy match
        for original_plate in self.original_plate:
            for candidate in candidates:
                similarity_score = fuzz.ratio(original_plate, candidate['plate'])
                if similarity_score > best_score:
                    best_score = similarity_score
                    best_match = original_plate

        return best_match       
    

    def __draw_box(self, original_image_path:str, model_image_path, response: dict) -> str:
        
        org_img = cv2.imread(original_image_path)
        model_img = cv2.imread(original_image_path)

        coordinates = []
        
        for result in response['results']:
            box = result['box']
            print(box)
            coordinates.append(box)
            
            
            cv2.rectangle(org_img, (int(box['xmin']), int(box['ymin'])), (int(box['xmax']), int(box['ymax'])), (0, 0, 255), 2)
            cv2.rectangle(model_img, (int(box['xmin']), int(box['ymin'])), (int(box['xmax']), int(box['ymax'])), (0, 0, 255), 2)

        timestamp = time.strftime("%Y%m%d%H%M%S")

        result_name = f"img_{timestamp}.jpg"

        os.makedirs("NumberPlateImages/Original", exist_ok = True)
        os.makedirs("NumberPlateImages/Model", exist_ok = True)
        
        org_res_path = os.path.join("NumberPlateImages/Original", result_name)
        model_res_path = os.path.join("NumberPlateImages/Model", result_name)


        cv2.imwrite(org_res_path, org_img)
        cv2.imwrite(model_res_path, model_img)

        if coordinates != []:
            print("At detector", coordinates)
            # self.__image_processor.process_image(original_image_path, model_res_path, coordinates)
            # threading.Thread(target = lambda:post_process_image(original_image_path, model_res_path, coordinates)).start()
        # print(result_path)

        return model_res_path, coordinates


    def detect(self, original_image_path:str, model_image_path: str):

        # print("ii")
        response = self.__get_response(original_image_path)
        # print(response)

        if 'results' not in response:
            return 

        candidates = [{'plate': candidate['plate'], 'score': candidate['score']} for result in response['results'] for candidate in result['candidates']]

        record = {}
        best_candidate = self.__get_best(candidates)

        matching_row = self.orig_df[self.orig_df['vehicle_number'].astype(str) == best_candidate]

        if not matching_row.empty:
            record = {
                "Vehicle Number": matching_row['vehicle_number'].values[0],
                "Roll Number": matching_row['roll_number'].values[0],
                "Matching Name": matching_row['name'].values[0],
                "Department": matching_row['Department'].values[0]
            }

        model_res_path, coordinates = self.__draw_box(original_image_path, model_image_path, response)

        print(record)
        return record, model_res_path, coordinates