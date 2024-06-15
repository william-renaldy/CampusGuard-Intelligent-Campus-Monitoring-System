## Campus Guard: A YOLOv8-based Object Detection System for Campus Safety

The Campus Guard initiative aims to leverage advanced computer vision to promote a safer and more inclusive campus environment. This repository contains a YOLOv8 model trained to detect a variety of campus safety and behavioral concerns, including:

* Violence
* Overcrowded biking
* Helmet-less riding
* Mobile phone usage in class
* Sleeping in class

The system also includes an anonymous reporting portal that allows members of the campus community to report these issues.

###  Data Collection and Annotation

We gathered a diverse dataset of images depicting various campus-related issues. This dataset was then annotated using Roboflow to label and categorize the objects and behaviors of interest for training the YOLOv8 model.

###  Model Training and Evaluation

The YOLOv8 model was trained on the annotated dataset using a train/validation split. The model's performance was evaluated using metrics such as precision, recall, and mean average precision (mAP) to assess its accuracy and effectiveness in detecting the target objects and behaviors.

###  Anonymous Reporting Portal

An anonymous reporting portal was developed to enable members of the campus community to submit observations and concerns regarding the identified issues. The portal allows users to upload images, provide descriptions, and report incidents anonymously.

###  Integration with Campus Monitoring Systems

Future work will explore the possibility of integrating the system with existing campus monitoring systems, such as surveillance cameras and access control systems. This integration would augment the coverage and effectiveness of the detection efforts.

**Note:** Due to data privacy concerns, only a partial files are included in this repository.
