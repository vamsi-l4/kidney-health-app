# KidneyAI Backend Server

This backend server is built with FastAPI to support the KidneyAI frontend React app. It provides endpoints for authentication, image prediction, report submission, and report retrieval.

## Features

- User authentication with JWT tokens
- Image upload and AI prediction (supports DICOM, PNG, JPG)
- Report submission and ZIP report generation
- Static file serving for uploaded images and reports
- Model loading with PyTorch (supports TorchScript and state_dict)
- Grad-CAM heatmap generation for explainability

## Setup Instructions

1. Create virtual environment and install dependencies:

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Prepare directories:

```bash
mkdir -p app/uploads app/reports
```

3. Place your trained model file (`kidney_model_ts.pt` or `kidney_model.pt`) in `server/app/`.

4. Run the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. The API base URL is `http://localhost:8000/api`.

## API Endpoints

- `POST /api/auth/token` - Obtain JWT token (demo credentials: admin/password)
- `POST /api/predict` - Upload image for prediction
- `POST /api/submit-report` - Submit patient report with images
- `GET /api/reports/{name}` - Download report ZIP
- `GET /api/health` - Health check

## Model Training

See `model/train.py` for training a classifier using transfer learning on your dataset.

## Notes

- Replace demo authentication with real user management for production.
- Use HTTPS and secure storage for sensitive data.
- Adjust CORS origins in production.
- For heavy inference, consider GPU or ONNX Runtime.

## Connecting Frontend

Set your React app `.env`:

```
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

Your frontend can then call the backend API for authentication, prediction, and reports.

---

This backend is designed to work seamlessly with your existing React frontend for a real-world kidney stone detection web app.
