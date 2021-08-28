import ast
import os
import pandas as pd
import cv2
import numpy as np
import albumentations as Alb
from tqdm import tqdm

"""Paths of images and labels for augmented data"""
augmented_images = "augmented/images"
augmented_labels = "augmented/labels"
os.makedirs(augmented_images, exist_ok=True)
os.makedirs(augmented_labels, exist_ok=True)

"""Albumnetations image and bounding box augmentation transforms"""
transformations = [
    Alb.RandomSizedBBoxSafeCrop(
        width=1024, height=1024, 
        erosion_rate=0.2,
        p=0.48
    ),
    Alb.Rotate(limit=6,p=0.66),
    Alb.RGBShift(p=0.75),
    Alb.RandomGamma(gamma_limit=(250, 340),p=0.25),
    Alb.RandomBrightnessContrast(p=0.32),
    Alb.GaussNoise(
        var_limit=(50, 180),
        mean=20,
        p = 0.32,
    ),
    Alb.CLAHE(p=0.23),
    Alb.Perspective(
        p=0.32,
        scale=(0.03, 0.05),
        interpolation=1
    ),
]

def augmenter(df):
    count = 0
    for ind, row in tqdm(df.iterrows()):
        class_id = []
        bboxes = []
        img_path = row["file_path"]
        print(img_path )
        file_name, _ = os.path.splitext(img_path.split("/")[-1])
        print(file_name)
        data = row["bbox_data"]
        for i in range(len(data)):
        #    print(dt)
            class_no = data[i][0]
            class_id.append(class_no)
            bbox = data[i][1]
            bboxes.append(bbox)
            print(class_no, "&", bbox[0], bbox[1], bbox[2], bbox[3])
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        bboxParams = Alb.BboxParams(
            format='yolo', 
            label_fields=['class_id']
        )
        transform = Alb.Compose(
            transformations,
            bbox_params = bboxParams
        )
        for i in tqdm(range(11)):
            transformed = transform(
                    image=image, 
                    bboxes=bboxes, 
                    class_id=class_id
            )
            savlst = list()
            for j,tup in enumerate(transformed["bboxes"]):
                savlst.append([
                    int(transformed["class_id"][j]),
                    tup[0], tup[1], tup[2], tup[3]
                ])
            print(savlst)
            sav_arr = np.array(savlst)
            #print(sav_arr)
            np.savetxt(
            os.path.join(augmented_labels,f"{file_name}_{i}.txt"),
            sav_arr,
            fmt = ["%d","%f","%f","%f","%f"],
            )
            new_image = transformed["image"]
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(os.path.join(augmented_images,f"{file_name}_{i}.jpg"),new_image)
        #break
        count +=1
    print(count)


if __name__ == "__main__":

    """Data munging"""
    img_df = pd.read_csv("yolo_object_detection.csv")
    #img_df = img_df.head(7)
    img_df.bbox_data = img_df.bbox_data.apply(ast.literal_eval)
    print(img_df)
    augmenter(img_df)
