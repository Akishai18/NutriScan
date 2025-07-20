# NutriScan Backend API

This is the Flask backend API for the NutriScan application that handles food detection using computer vision.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download YOLO weights:**
   - Create a `yolo-Weights` folder in the backend directory
   - Download `yolov8n.pt` from the Ultralytics repository and place it in the `yolo-Weights` folder

3. **Run the Flask API:**
   ```bash
   python app.py
   ```

   The API will start on `http://localhost:5000`

## API Endpoints

- `POST /api/start-detection` - Start food detection
- `POST /api/stop-detection` - Stop food detection  
- `GET /api/detection-status` - Get current detection status
- `GET /api/detection-results` - Get detection results
- `POST /api/clear-results` - Clear detection results