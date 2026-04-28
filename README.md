# AutoML Full Stack Project

A full-stack AutoML system using **FastAPI (Backend)** and **React + Vite (Frontend)** for end-to-end machine learning automation.

---

# Backend Structure (FastAPI)

```

backend/
│
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── routes/                  # API endpoints
│   │   ├── upload.py
│   │   ├── train.py
│   │   ├── predict.py
│   │   ├── file_preview.py
│   │   ├── target_column.py
│   │   ├── download_model.py
│   │   ├── delete_model.py
│   │   ├── health.py
│   │   └── all_saved_models.py
│   │
│   ├── services/               # ML logic
│   │   ├── preprocessing.py
│   │   ├── training.py
│   │   ├── evaluation.py
│   │   └── model_io.py
│   │
│   ├── schemas/                # Pydantic models
│   ├── utils/                  # File handling & helpers
│   └── core/                   # Config & settings
│
├── models/                     # Saved ML models
└── requirements.txt

```

---

# Frontend Structure (React + Vite)

```

frontend/
│
├── src/
│   ├── api/                   # API calls (Axios)
│   ├── components/            # Reusable UI components
│   │   ├── FileUpload.jsx
│   │   ├── DataPreview.jsx
│   │   ├── TaskSelector.jsx
│   │   ├── TargetSelector.jsx
│   │   ├── TrainButton.jsx
│   │   ├── MetricsDisplay.jsx
│   │   └── ModelDownload.jsx
│   │
│   ├── pages/
│   │   ├── Home.jsx
│   │   └── Dashboard.jsx
│   │
│   ├── hooks/                # Custom hooks
│   ├── utils/                # Helpers
│   ├── styles/               # Global CSS
│   ├── App.jsx
│   └── main.jsx
│
├── index.html
└── vite.config.js

````

---

# Backend API Endpoints

- `POST /api/upload` → Upload dataset
- `GET /api/preview/{file_id}` → Preview dataset
- `POST /api/validate` → Validate dataset + task
- `GET /api/target-columns` → Suggest target columns
- `POST /api/train` → Train ML model
- `POST /api/predict` → Make predictions
- `GET /api/models` → List saved models
- `GET /api/model/{model_id}/download` → Download model
- `DELETE /api/delete/{id}` → Delete model
- `GET /api/health` → Health check

---

# Installation & Run

## 1. Clone repository
```bash
git clone <repo-url>
cd AutoML
````

---

## 2. Run Backend (FastAPI)

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs on:

```
http://127.0.0.1:8000
```

---

## 3. Run Frontend (React + Vite)

Open a new terminal:

```bash
cd frontend
```

### Check Node & npm:

```bash
node --version
npm --version
```

Make sure Node.js is installed.

---

### Install dependencies:

```bash
npm install
```

---

### Start frontend:

```bash
npm run dev
```

Frontend runs on:

```
http://localhost:5173
```

---

# Notes

* Make sure backend is running before using frontend
* CORS is enabled for local development
* Models are saved locally in `/models`
* Supports classification, regression, clustering

---