from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from . import model as model_module
from . import auth
import uuid, os, json, logging
from pydantic import BaseModel

bearer = HTTPBearer()

def get_current_user(token: str = Depends(bearer)):
    return auth.verify_token(token.credentials)

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = model_module.predict_image_bytes(contents, filename=file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"filename": file.filename, "prediction": result}

@router.post("/login")
async def login(request: LoginRequest):
    return auth.login(request.email, request.password)

@router.post("/register")
async def register(request: RegisterRequest):
    return auth.register(request.email, request.password, request.name)

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    return auth.forgot_password(request.email)

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    return auth.verify_otp(request.email, request.otp)

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    return auth.reset_password(request.email, request.new_password)

class ReportRequest(BaseModel):
    name: str
    prediction: dict
    createdAt: str

@router.get("/reports")
async def get_reports(user = Depends(get_current_user)):
    email = user['sub']
    reports_file = os.path.join(os.path.dirname(__file__), 'user_reports.json')
    try:
        with open(reports_file, 'r') as f:
            reports = json.load(f)
        return reports.get(email, [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@router.post("/reports")
async def add_report(report: ReportRequest, user = Depends(get_current_user)):
    email = user['sub']
    reports_file = os.path.join(os.path.dirname(__file__), 'user_reports.json')
    try:
        with open(reports_file, 'r') as f:
            reports = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        reports = {}
    if email not in reports:
        reports[email] = []
    report_data = report.dict()
    report_data['id'] = str(uuid.uuid4())
    reports[email].append(report_data)
    with open(reports_file, 'w') as f:
        json.dump(reports, f)
    return {"message": "Report added"}

@router.delete("/reports/{report_id}")
async def delete_report(report_id: str, user = Depends(get_current_user)):
    email = user['sub']
    reports_file = os.path.join(os.path.dirname(__file__), 'user_reports.json')
    try:
        with open(reports_file, 'r+') as f:
            reports = json.load(f)
            if email in reports:
                reports[email] = [r for r in reports[email] if r['id'] != report_id]
                f.seek(0)
                json.dump(reports, f)
                f.truncate()
        return {"message": "Report deleted"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report not found")
