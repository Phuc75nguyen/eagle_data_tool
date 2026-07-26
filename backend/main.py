import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.api.routes_data import router as data_router
from app.api.routes_config import router as config_router
from app.services.scheduler_service import start_scheduler, stop_scheduler

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Tạo schema CSDL (chạy lần đầu sẽ tạo file sqlite / bảng)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Eagle Data Tool Enterprise App", version="2.0")

# Cấu hình CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối các Routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(data_router)
app.include_router(config_router)

@app.on_event("startup")
def on_startup():
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()

@app.get("/")
def read_root():
    return {"message": "Eagle Data Tool FastAPI Backend is running!"}
