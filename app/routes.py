from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
import uuid, os, json
from . import model as model_module
from . import auth

router = APIRouter()
bearer = HTTPBearer()

# ✅ Auth verification helper
def get_current_user(token: str = Depends(bearer)):
    return auth.verify_token(token.credentials)

# ✅ Schemas
class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)

class RegisterRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)
    name: str = Field(max_length=100)

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

class ReportRequest(BaseModel):
    name: str
    prediction: dict
    createdAt: str


# ✅ Routes
@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = model_module.predict_image_bytes(contents, filename=file.filename)
        return {"filename": file.filename, "prediction": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to analyze this image") from e


@router.post("/login")
async def login(request: LoginRequest):
    try:
        return auth.login(request.email, request.password)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected login error: {str(e)}")


@router.post("/register")
async def register(request: RegisterRequest):
    try:
        return auth.register(request.email, request.password, request.name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    return auth.forgot_password(request.email)


@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    return auth.verify_otp(request.email, request.otp)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    return auth.reset_password(request.email, request.new_password)


@router.get("/reports")
async def get_reports(user=Depends(get_current_user)):
    email = user["sub"]
    reports_file = os.path.join(os.path.dirname(__file__), "user_reports.json")
    try:
        with open(reports_file, "r") as f:
            reports = json.load(f)
        return reports.get(email, [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


@router.post("/reports")
async def add_report(report: ReportRequest, user=Depends(get_current_user)):
    email = user["sub"]
    reports_file = os.path.join(os.path.dirname(__file__), "user_reports.json")
    try:
        with open(reports_file, "r") as f:
            reports = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        reports = {}

    if email not in reports:
        reports[email] = []

    report_data = report.dict()
    report_data["id"] = str(uuid.uuid4())
    reports[email].append(report_data)

    with open(reports_file, "w") as f:
        json.dump(reports, f)

    return {"message": "Report added"}


@router.delete("/reports/{report_id}")
async def delete_report(report_id: str, user=Depends(get_current_user)):
    email = user["sub"]
    reports_file = os.path.join(os.path.dirname(__file__), "user_reports.json")

    try:
        with open(reports_file, "r+") as f:
            reports = json.load(f)
            if email in reports:
                reports[email] = [r for r in reports[email] if r["id"] != report_id]
                f.seek(0)
                json.dump(reports, f)
                f.truncate()
        return {"message": "Report deleted"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report not found")
