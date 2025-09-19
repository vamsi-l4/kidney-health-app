from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as api_router
import os
import logging
from fastapi import Request

app = FastAPI(title="Kidney Stone Predictor API")

# Set up logger
logger = logging.getLogger("uvicorn.access")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routers
app.include_router(api_router, prefix="/api")

# Add welcome endpoint with logging
@app.get("/welcome")
async def welcome(request: Request):
    logger.info(f"Request received: {request.method} {request.url.path}")
    return {"message": "Welcome to the Kidney Stone Predictor API!"}
