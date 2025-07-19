from ultralytics import YOLO
import cv2
import math 
import json
from datetime import datetime
import os

# start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Food objects to track
foods = ["banana"]

# Food logs path
food_log = 'detection/food_logs.json'

if not os.path.exists(food_log):
    with open(food_log, "w") as f:
        json.dump([], f)


# model
model = YOLO("yolo-Weights/yolov8n.pt")

# object classes
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

last_detected = ""
cooldown_seconds = 10
last_detection_time = datetime.min

while True:
    success, img = cap.read()
    results = model(img, stream=True)

    # coordinates
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

            # put box in cam
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # confidence
            confidence = math.ceil((box.conf[0]*100))/100
            # class name
            cls = int(box.cls[0])
            
            # Only track items in 'foods' list
            if classNames[cls] in foods:
                
                current_time = datetime.now()
                
                # Don't track duplicates of the same object
                if last_detected != classNames[cls] : # *At time cooldown if needed*
                
                    print("Confidence --->",confidence)
                    print("Class name -->", classNames[cls])
                    print(last_detected)

                    # Log to JSON
                    new_entry = {
                        "food": classNames[cls],
                        "timestamp": current_time.isoformat()
                    }

                    # Read → Append → Write
                    with open(food_log, "r+") as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            data = []

                        data.append(new_entry)

                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()

                    last_detected = classNames[cls]

            # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2

            cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()