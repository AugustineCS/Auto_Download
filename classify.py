from ultralytics import YOLO   # type: ignore
import os
import shutil
model = YOLO("yolov8n.pt")

"""
Using a pre-trained classification yolov8 model
Classifing the downloaded images into good/bad images
good_folder = images which passes the yolov8 prediction
bad_folder = images which dont passes the yolov8 prediction
"""
source_folder = r"C:\ubuntu\pro\PlayWright_Python\images\cat"
good_folder = r"C:\ubuntu\pro\PlayWright_Python\classify\good"
bad_folder = r"C:\ubuntu\pro\PlayWright_Python\classify\bad"

os.makedirs(good_folder, exist_ok=True)
os.makedirs(bad_folder, exist_ok=True)

for filename in os.listdir(source_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        img_path = os.path.join(source_folder, filename)
        results = model.predict(img_path, verbose=False)

        cat_found = False
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    cls = model.names[int(box.cls)]
                    conf = box.conf.item()
                    if cls == "cat":
                        cat_found = True
                        print(
                            f"{filename}: cat detected "
                            f"(confidence {conf:.2f})"
                        )

        if cat_found:
            shutil.copy(img_path, os.path.join(good_folder, filename))
        else:
            print(f"{filename}: No cat detected")
            shutil.copy(img_path, os.path.join(bad_folder, filename))
