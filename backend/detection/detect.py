from ultralytics import YOLO
import cv2
import math 
import json
from datetime import datetime
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time 

# Initialize Flask app
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Global variables for detection state
detection_active = False
detection_thread = None
camera_open_success = None 

# Food objects to track
foods = ["banana"]

# Food logs path
food_log = os.path.abspath(os.path.join(os.path.dirname(__file__), 'food_logs.json'))

# Ensure the directory for food_log exists
os.makedirs(os.path.dirname(food_log), exist_ok=True)

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
    global detection_active, camera_open_success

    print("[run_detection] Thread started.")
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[run_detection] Error: Could not open webcam.")
        camera_open_success = False # Set flag to indicate failure
        detection_active = False # Ensure detection stops if camera can't be opened
        print("[run_detection] Exiting thread due to camera open failure.")
        return
    
    camera_open_success = True # Set flag to indicate success
    print("[run_detection] Webcam opened successfully.")
    
    cap.set(3, 640)
    cap.set(4, 480)
    
    last_detected = ""
    last_detection_time = datetime.min

    try:
        frame_count = 0
        while detection_active:
            frame_count += 1
            success, img = cap.read()
            if not success:
                print(f"[run_detection] Warning: Could not read frame {frame_count} from webcam.")
                # If camera disconnects, stop detection 
                if not cap.isOpened():
                    print("[run_detection] Error: Webcam disconnected during read. Stopping detection.")
                    detection_active = False
                    break # Exit loop if camera truly disconnected
                continue # Try reading next frame if not successful but camera still open
                
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
            key = cv2.waitKey(1)
            if key == ord('q'):
                print("[run_detection] 'q' pressed. Stopping detection.")
                detection_active = False # User pressed 'q' to quit
                break # Exit the while loop

    except Exception as e:
        print(f"[run_detection] An unexpected error occurred: {e}")
        detection_active = False # Ensure detection stops on unexpected errors
    finally:
        print("[run_detection] Detection loop ended. Cleaning up resources.")
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("[run_detection] Resources released. Thread exiting.")

@app.route('/api/start-detection', methods=['POST'])
def start_detection():
    """Start the detection process"""
    global detection_active, detection_thread, camera_open_success
    
    if detection_active:
        return jsonify({"status": "error", "message": "Detection already active"}), 400
    
    detection_active = True
    camera_open_success = None # Reset status before starting the thread
    detection_thread = threading.Thread(target=run_detection)
    detection_thread.start()
    
    # Wait a short while for the camera to initialize in the thread
    timeout = 5 # seconds
    start_time = datetime.now()
    while camera_open_success is None and (datetime.now() - start_time).total_seconds() < timeout:
        time.sleep(0.1) # Check every 100ms

    if camera_open_success is False:
        # Camera failed to open
        detection_active = False # Ensure the main state reflects failure
        return jsonify({"status": "error", "message": "Failed to open webcam. It might be in use, disconnected, or permissions are not granted."}), 500
    elif camera_open_success is None:
        # Timeout occurred, camera status still unknown (e.g., thread didn't even start or got stuck)
        detection_active = False # Assume failure or issue
        return jsonify({"status": "error", "message": "Timed out waiting for webcam to initialize. Check camera connection and permissions."}), 500
    else:
        # Camera opened successfully
        return jsonify({"status": "success", "message": "Detection started"})

@app.route('/api/stop-detection', methods=['POST'])
def stop_detection():
    """Stop the detection process"""
    global detection_active
    
    if not detection_active:
        return jsonify({"status": "error", "message": "Detection not active"}), 400
    
    detection_active = False
    
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

@app.route('/api/get-nutrition', methods=['POST'])
def nutrition_info_endpoint():
 
    data = request.get_json()
    food_item = data.get('food_item')

    if not food_item:
        return jsonify({"status": "error", "message": "No food_item provided"}), 400

    print(f"Received request for nutrition info for: {food_item}")

    from backend.search_scripts.nutrition_search import get_nutrition_info
    nutrition_data = get_nutrition_info(food_item)
    print(f"Nutrition search result: {nutrition_data}")

    return jsonify({"status": "success", "nutrition_info": nutrition_data})

if __name__ == '__main__':

    if not os.path.exists(food_log):
        with open(food_log, "w") as f:
            json.dump([], f)
    
    print("Flask API starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
