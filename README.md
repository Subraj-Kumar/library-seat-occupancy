# 📚 Real-Time Library Seat Occupancy Detection System

## Overview
University libraries often face a mismatch between the number of students and available seating. Students typically have no way of knowing seat availability before physically visiting the library, leading to overcrowding and wasted time.

This project solves that problem by providing a **real-time seat availability dashboard** using **computer vision and web technologies**. The system processes CCTV footage to detect occupied and empty seats and displays live availability to students through a web application.

---

## ✨ Key Features
- 🎥 Real-time processing of CCTV video feeds
- 🧠 Person detection using YOLOv8
- 🪑 Seat occupancy detection using spatial overlap logic
- 🔄 Temporal smoothing to reduce flickering and false detections
- 🌐 Live web dashboard with WebSocket-based updates
- 🔐 Privacy-aware design (no face recognition, no video storage)
- 🚀 Deployed backend and frontend

---

## 🏗️ System Architecture

     CCTV / Video Feed
     ↓
     Computer Vision Engine (YOLO + OpenCV)
     ↓
     FastAPI Backend (REST + WebSocket)
     ↓
     React Frontend Dashboard

- **Computer Vision Layer**: Detects people and determines seat occupancy
- **Backend Layer**: Maintains real-time seat state and broadcasts updates
- **Frontend Layer**: Displays live seat availability to users

---

## 🧠 Technical Approach

### 1. Person Detection
- Uses a pretrained YOLOv8 model to detect people in video frames.
- Inference is performed at fixed intervals for efficiency.

### 2. Seat Localization
- Seat positions are manually annotated once using a fixed reference frame.
- Seat coordinates remain constant due to a fixed camera angle.

### 3. Seat Occupancy Logic
- Intersection-over-Union (IoU) is used to determine overlap between people and seats.
- Center-point validation prevents false detection from background or rear seats.

### 4. Temporal Smoothing
- Seat state changes are confirmed only after multiple consecutive detections.
- This reduces flickering caused by posture changes or missed detections.

### 5. Real-Time Updates
- Backend exposes REST APIs and WebSocket endpoints.
- Frontend receives instant updates without polling.

---

## 🛠️ Tech Stack

### Computer Vision
- OpenCV
- YOLOv8 (Ultralytics)

### Backend
- FastAPI
- WebSockets
- Python

### Frontend
- React
- HTML / CSS
- WebSocket client

### Deployment
- Backend: Cloud-hosted FastAPI service
- Frontend: Deployed web dashboard
- CV Inference: Runs locally near the video source

---

## 🔐 Privacy & Ethics
- No facial recognition is performed
- No video footage is stored
- Only anonymized seat counts are shared
- Designed with student privacy in mind

---

## 🚀 Deployment Model
- CV inference runs locally where CCTV access is available
- Backend and frontend are deployed on the cloud
- Students access the dashboard via a public URL

This hybrid deployment ensures low latency and privacy compliance.

---

## 📊 Use Cases
- Students checking seat availability before visiting the library
- Library administrators monitoring occupancy
- Peak-hour usage analysis (future extension)

---

## 🔮 Future Enhancements
- Floor-wise and section-wise seat availability
- Multi-camera support
- Seat heatmaps and usage analytics
- Mobile application
- Admin dashboard for camera health monitoring

---

## 🧾 Project Status
✅ Deployed  
✅ Functional end-to-end  
🚧 Actively extensible

---

## 👤 Author
Developed by **Subraj Kumar**  
Computer Science & Engineering

---

## 📄 License
This project is intended for academic and educational purposes.