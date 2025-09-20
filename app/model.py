import os, io, numpy as np, torch
from PIL import Image
from torchvision import transforms, models
import torch.nn as nn
import torch.nn.functional as F
import uuid
from fastapi import HTTPException

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../model/kidney_model.pt")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Preprocess
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])

# ✅ Load EfficientNet model
_model = None
def get_model():
    global _model
    if _model is None:
        try:
            # Check if model file exists
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

            model = models.efficientnet_b0(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_features, 2)

            # Load model with error handling
            model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
            model.eval()
            _model = model
            print(f"✅ Model loaded successfully from {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")
    return _model

def predict_image_bytes(data: bytes, filename: str = None):
    image = Image.open(io.BytesIO(data)).convert("RGB")
    x = transform(image).unsqueeze(0).to(device)
    model = get_model()
    with torch.no_grad():
        outs = model(x)
        probs = F.softmax(outs, dim=1)[0]
        idx = int(probs.argmax().item())
        label = "stone" if idx == 1 else "non-stone"
        confidence = float(probs[idx].item())
    return {"label": label, "confidence": confidence}
