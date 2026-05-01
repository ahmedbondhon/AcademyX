from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from database.connection import Base, engine

# ── ADD THIS ──
from api.routes_auth import router as auth_router
from api.routes_obe import router as obe_router
from api.routes_alerts import router as alerts_router
from api.routes_upload  import router as upload_router  
from api.routes_reports import router as reports_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── ADD THIS ──
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(obe_router,  prefix="/api/obe",  tags=["OBE"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(upload_router,  prefix="/api/upload",  tags=["Upload"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}