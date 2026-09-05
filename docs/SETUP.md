# ORCA Setup & Deployment Guide

**System**: ORCA Marine Intelligence Platform  
**Version**: 6.0.0

---

## 1. Prerequisites

- **Python**: 3.11, 3.12, or 3.13
- **Node.js**: 18+ or 20+ (LTS recommended)
- **Git**

---

## 2. One-Command Quick Start

### Windows
Run:
```cmd
start.bat
```

### Linux / macOS
Run:
```bash
chmod +x start.sh
./start.sh
```

---

## 3. Manual Step-by-Step Installation

### 3.1 Backend Setup (FastAPI)
```bash
# Navigate to backend folder
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Activate on Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python run.py
```
Backend will start on `http://127.0.0.1:8000`.  
- Interactive API Docs: `http://127.0.0.1:8000/docs`  
- Health Probe: `http://127.0.0.1:8000/health`  
- Readiness Probe: `http://127.0.0.1:8000/health/ready`

### 3.2 Frontend Setup (Next.js 14)
```bash
# In the repository root
npm install

# Run development server
npm run dev
```
Frontend will be accessible at `http://localhost:3000`.

---

## 4. Docker Deployment

To spin up the complete containerized stack:
```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

---

## 5. Verification & Testing

Run full backend test suite:
```bash
cd backend
pytest -v
```

Run frontend build check:
```bash
npm run build
```
