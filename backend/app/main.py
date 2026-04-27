from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.routes import upload, data_validation, health, file_preview, target_column

app = FastAPI(
    title="ML Auto-Pipeline API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["File Upload"])
app.include_router(data_validation.router, tags=["Data Validation"])
app.include_router(health.router, tags=["Health"])
app.include_router(file_preview.router, tags=["Data Preview"])
app.include_router(target_column.router, tags=["Target Column"])