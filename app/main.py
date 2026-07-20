import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as api_router
import logging

app = FastAPI(title="Kidney Stone Predictor API")

# ✅ Logging setup
logger = logging.getLogger("uvicorn.access")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

# ✅ CORS (Vercel + Localhost + Render-safe)
default_origins = "http://localhost:5173,https://kidneystone-blond.vercel.app"
allowed_origins = [origin.strip().rstrip("/") for origin in os.getenv("CORS_ORIGINS", default_origins).split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include routers
app.include_router(api_router, prefix="/api")

# ✅ Test endpoint
@app.get("/welcome")
async def welcome(request: Request):
    logger.info(f"Request received: {request.method} {request.url.path}")
    return {"message": "Welcome to the Kidney Stone Predictor API!"}
