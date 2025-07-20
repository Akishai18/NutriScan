from ultralytics import YOLO
import cv2
import math 
import json
from datetime import datetime
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

# Initialize Flask app
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Global variables for detection state
detection_active = False
detection_thread = None

# Food objects to track
foods = ["banana"]

# Food logs path
food_log = 'backend/detection/food_logs.json' 

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

def run_detection():
    """Run the detection process"""
    global detection_active

    # Initialize webcam *inside* the function, so it's re-initialized each time detection starts
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        detection_active = False # Ensure detection stops if camera can't be opened
        return
    
    cap.set(3, 640)
    cap.set(4, 480)
    
    last_detected = ""
    # cooldown_seconds = 10 # This variable is not used, consider removing or implementing
    last_detection_time = datetime.min

    while detection_active:
        success, img = cap.read()
        if not success:
            print("Warning: Could not read frame from webcam. Attempting to continue...")
            # If camera disconnects, stop detection gracefully
            if not cap.isOpened():
                print("Error: Webcam disconnected. Stopping detection.")
                detection_active = False
            continue
            
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
                    # Added a check for cooldown_seconds if you decide to implement it
                    if last_detected != classNames[cls] or (current_time - last_detection_time).total_seconds() > 10: 
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
                        last_detection_time = current_time # Update last detection time

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

    # Cleanup: Release camera and destroy windows when detection stops
    cap.release()
    cv2.destroyAllWindows()

@app.route('/api/start-detection', methods=['POST'])
def start_detection():
    """Start the detection process"""
    global detection_active, detection_thread
    
    if detection_active:
        return jsonify({"status": "error", "message": "Detection already active"}), 400
    
    detection_active = True
    detection_thread = threading.Thread(target=run_detection)
    detection_thread.start()
    
    return jsonify({"status": "success", "message": "Detection started"})

@app.route('/api/stop-detection', methods=['POST'])
def stop_detection():
    """Stop the detection process"""
    global detection_active
    
    if not detection_active:
        return jsonify({"status": "error", "message": "Detection not active"}), 400
    
    detection_active = False
    
    # It's good practice to wait for the thread to finish, though not strictly necessary for this issue
    # if detection_thread and detection_thread.is_alive():
    #     detection_thread.join()
    
    return jsonify({"status": "success", "message": "Detection stopped"})

@app.route('/api/detection-status', methods=['GET'])
def get_detection_status():
    """Get current detection status"""
    global detection_active
    
    return jsonify({
        "active": detection_active,
        "message": "Detection active" if detection_active else "Detection inactive"
    })

@app.route('/api/detection-results', methods=['GET'])
def get_detection_results():
    """Get detection results from the food log"""
    try:
        if os.path.exists(food_log):
            with open(food_log, 'r') as f:
                data = json.load(f)
            return jsonify({"status": "success", "results": data})
        else:
            return jsonify({"status": "success", "results": []})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/clear-results', methods=['POST'])
def clear_results():
    """Clear detection results"""
    try:
        with open(food_log, 'w') as f:
            json.dump([], f)
        return jsonify({"status": "success", "message": "Results cleared"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Ensure food log exists
    if not os.path.exists(food_log):
        with open(food_log, "w") as f:
            json.dump([], f)
    
    print("Flask API starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
