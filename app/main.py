import time
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import settings, get_db
from app.schemas import DelegateCreate
from app.services import get_all_committees, get_committee_by_id, register_delegate
from app.exceptions import AppException
from app.constants import RATE_LIMIT

DOCS_URL = "/docs" if settings.ENVIRONMENT == "development" else None
REDOC_URL = "/redoc" if settings.ENVIRONMENT == "development" else None

app = FastAPI(title="LGU MUN 2026", docs_url=DOCS_URL, redoc_url=REDOC_URL)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def success_envelope(data: dict, status: int = 200):
    return JSONResponse({"success": True, "data": data, "timestamp": now_iso()}, status_code=status)

def error_envelope(code: str, message: str, field=None, status: int = 400):
    return JSONResponse(
        {"success": False, "error": {"code": code, "message": message, "field": field}, "timestamp": now_iso()},
        status_code=status
    )

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return error_envelope(exc.code, exc.message, exc.field, exc.status_code)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "timestamp": time.time()}

@app.post("/api/v1/delegates", status_code=201)
@limiter.limit(RATE_LIMIT)
def create_delegate(request: Request, body: DelegateCreate, db: Session = Depends(get_db)):
    ip = request.client.host
    result = register_delegate(db, body, ip)
    return success_envelope(result, status=201)

@app.get("/api/v1/committees")
def list_committees(db: Session = Depends(get_db)):
    committees = get_all_committees(db)
    return success_envelope({"committees": committees})

@app.get("/api/v1/committees/{committee_id}")
def get_committee(committee_id: int, db: Session = Depends(get_db)):
    committee = get_committee_by_id(db, committee_id)
    if not committee:
        return error_envelope("COMMITTEE_NOT_FOUND", "Committee not found", status=404)
    return success_envelope(committee)

# Static files — mount LAST so API routes take priority
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
