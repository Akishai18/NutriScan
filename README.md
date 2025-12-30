# 🍎 NutriScan

**Smart Food Recognition for Healthier Choices**

NutriScan enables users to make informed dietary decisions instantly by combining computer vision with real-time nutrition data. Simply scan your meal, and get detailed nutritional insights right when you need them.

![Built with Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=flat&logo=raspberry-pi&logoColor=white)

---

## 🌟 Inspiration

Every day, people struggle with making healthy food choices—not because they don't want to eat better, but because they don't have accessible information at the right time. NutriScan was created to bridge that gap, helping users make smarter dietary decisions instantly by combining computer vision with real-time nutrition data.

---

## 🚀 What It Does

NutriScan is a smart food recognition app that allows users to scan their meals using a camera. The app:

- **Detects food items** using computer vision
- **Retrieves real-time nutritional information** including calories, macronutrients, and more
- **Provides intelligent, personalized responses** using Retrieval-Augmented Generation (RAG)
- **Empowers users** with quick and accessible dietary insights, so people know what they're eating when they're eating

---

## 🏗️ How We Built It

### Backend
- **Python & Flask** for the web server and API endpoints
- **OpenCV** to process camera images in real-time
- **YOLOv8** machine learning model for food classification
- **Weaviate vector database** to store embeddings of nutrition data, enabling semantic search
- **RAG pipeline** to retrieve relevant nutrition data and generate personalized responses via a language model
- **External nutrition APIs** for real-time calorie and macro data

### Frontend
- **React** for a dynamic, responsive interface
- **Tailwind CSS** for clean, modern styling
- **Node.js** for build tooling and development

### Hardware
- **Raspberry Pi 4** with camera module for edge deployment and real-time scanning

---

## 🧩 Tech Stack

**Languages & Frameworks:**
- Python
- FastAPI/Flask
- React
- Node.js

**Computer Vision & ML:**
- YOLOv8
- OpenCV

**Data & AI:**
- Weaviate (Vector Database)
- Google Vertex AI
- Gemini
- RAG (Retrieval-Augmented Generation)

**Styling:**
- Tailwind CSS

**Hardware:**
- Raspberry Pi 4

---

## 💪 Challenges We Ran Into

Initially, we wanted to incorporate hardware into this project using a **Raspberry Pi 4 with a camera module**. None of us had experience working with Raspberry Pi before, so it was a gamble.

At first, we didn't know we could use **VNC Viewer** to access the Pi's desktop, so we were trying to do everything through the terminal on a MacBook (this was hell). After a lot of trial, error, and Googling, we finally discovered that we could launch VNC Viewer, open a script right on the Pi's desktop, and run OpenCV directly from there. Turns out, using a visual interface makes things a lot easier.

---

## 🏆 Accomplishments That We're Proud Of

- Built a **full pipeline** combining computer vision, Flask, and real-time nutrition data in a clean, functional UI
- Successfully implemented **vector databases, RAG, and semantic search** for the first time
- Created something that's **actually useful** and has the potential to help people make better food choices

---

## 📚 What We Learned

- **Computer Vision & OpenCV:** How to process images, build real-time scan functionality, and integrate it smoothly into a Flask app
- **Vector Databases & RAG:** How semantic search and embeddings make data retrieval way more intelligent than basic keyword matching
- **Balancing UX with Backend Complexity:** Small interface decisions (like when and where a camera activates) make a huge difference for usability
- **Hardware Integration:** Working with Raspberry Pi and learning how to deploy computer vision on edge devices

---

## 🔮 What's Next for NutriScan

- **Expand dietary filters:** Add support for keto, halal, vegan, and allergen-specific recommendations
- **Meal history tracker:** Log meals over time and get insights (like a fitness tracker, but for food)
- **Voice-based interaction:** Ask questions like "Is this healthy for someone with high blood pressure?" and get smart, contextual answers
- **Performance optimization:** Make camera scanning faster and lighter for real-time use

---

## 🛠️ Setup & Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download YOLO weights:
   - Create a `yolo-Weights` folder in the backend directory
   - Download `yolov8n.pt` from the [Ultralytics repository](https://github.com/ultralytics/ultralytics) and place it in the `yolo-Weights` folder

4. Run the Flask API:
   ```bash
   python main.py
   ```

   The API will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/start-detection` | Start food detection |
| `POST` | `/api/stop-detection` | Stop food detection |
| `GET` | `/api/detection-status` | Get current detection status |
| `GET` | `/api/detection-results` | Get detection results |
| `POST` | `/api/clear-results` | Clear detection results |

---

## 📂 Project Structure

```
NutriScan/
├── backend/
│   ├── Import_Scripts/
│   ├── data/
│   ├── detection/
│   ├── search_scripts/
│   ├── main.py
│   ├── weaviate_client.py
│   ├── food_logs.json
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   └── (React application files)
└── README.md
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) for object detection
- [Weaviate](https://weaviate.io/) for vector database technology
- [OpenCV](https://opencv.org/) for computer vision capabilities

---
