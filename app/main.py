import time
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Depends, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import settings, get_db
from app.schemas import DelegateCreate, TransferRequest, AdminQueryCreate, QueryReply, QueryStatusUpdate
from app.services import (
    get_all_committees, get_committee_by_id, register_delegate,
    get_delegates_count, transfer_delegate,
    get_admin_stats, get_all_delegates_admin, get_delegate_by_id_admin,
    get_committees_for_admin, update_committee,
    create_query, get_queries, reply_to_query, update_query_status,
    get_settings, update_setting, export_delegates_csv
)
from app.exceptions import AppException
from app.constants import RATE_LIMIT, ADMIN_API_KEY_HEADER

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

async def verify_admin_key(x_admin_api_key: str = Header(None)):
    if not settings.ADMIN_API_KEY:
        # If no key set in .env, block all admin access as a safety measure
        raise HTTPException(status_code=500, detail="Admin access not configured")

    if x_admin_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid Admin API Key")
    return x_admin_api_key

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def success_envelope(data: dict, status: int = 200):
    return JSONResponse({"success": True, "data": data, "timestamp": now_iso()}, status_code=status)

def error_envelope(code: str, message: str, field=None, status: int = 400, data: dict = None):
    error_dict = {"code": code, "message": message, "field": field}
    if data:
        error_dict["data"] = data
    return JSONResponse(
        {"success": False, "error": error_dict, "timestamp": now_iso()},
        status_code=status
    )

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return error_envelope(exc.code, exc.message, exc.field, exc.status_code, exc.data)

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

@app.get("/api/v1/delegates/count")
def delegates_count(db: Session = Depends(get_db)):
    count = get_delegates_count(db)
    return success_envelope(count)

@app.post("/api/v1/delegates/{roll_number}/transfer")
@limiter.limit(RATE_LIMIT)
def transfer_delegate_endpoint(request: Request, roll_number: str, body: TransferRequest, db: Session = Depends(get_db)):
    result = transfer_delegate(db, roll_number, body.new_committee_id)
    return success_envelope(result)

# ============================================================
# ADMIN API ROUTES
# ============================================================

@app.get("/api/v1/admin/stats", dependencies=[Depends(verify_admin_key)])
def admin_stats(db: Session = Depends(get_db)):
    stats = get_admin_stats(db)
    return success_envelope(stats)

@app.get("/api/v1/admin/delegates", dependencies=[Depends(verify_admin_key)])
def admin_list_delegates(
    committee_id: int = None,
    search: str = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    result = get_all_delegates_admin(db, committee_id, search, page, per_page)
    return success_envelope(result)

@app.get("/api/v1/admin/delegates/{delegate_id}", dependencies=[Depends(verify_admin_key)])
def admin_get_delegate(delegate_id: int, db: Session = Depends(get_db)):
    delegate = get_delegate_by_id_admin(db, delegate_id)
    if not delegate:
        return error_envelope("DELEGATE_NOT_FOUND", "Delegate not found", status=404)
    return success_envelope(delegate)

@app.get("/api/v1/admin/committees", dependencies=[Depends(verify_admin_key)])
def admin_list_committees(db: Session = Depends(get_db)):
    committees = get_committees_for_admin(db)
    return success_envelope({"committees": committees})

@app.put("/api/v1/admin/committees/{committee_id}", dependencies=[Depends(verify_admin_key)])
def admin_update_committee(
    committee_id: int,
    body: dict, # Using dict for flexibility in update
    db: Session = Depends(get_db)
):
    result = update_committee(
        db,
        committee_id,
        chair_name=body.get("chair_name"),
        agenda_1=body.get("agenda_1"),
        agenda_2=body.get("agenda_2"),
        total_seats=body.get("total_seats")
    )
    if not result:
        return error_envelope("COMMITTEE_NOT_FOUND", "Committee not found", status=404)
    return success_envelope(result)

@app.get("/api/v1/admin/queries", dependencies=[Depends(verify_admin_key)])
def admin_list_queries(
    status: str = "all",
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    result = get_queries(db, status, page, per_page)
    return success_envelope(result)

@app.post("/api/v1/admin/queries/{query_id}/reply", dependencies=[Depends(verify_admin_key)])
def admin_reply_query(query_id: int, body: QueryReply, db: Session = Depends(get_db)):
    result = reply_to_query(db, query_id, body.reply)
    if not result:
        return error_envelope("QUERY_NOT_FOUND", "Query not found", status=404)
    return success_envelope(result)

@app.put("/api/v1/admin/queries/{query_id}/status", dependencies=[Depends(verify_admin_key)])
def admin_update_query_status(query_id: int, body: QueryStatusUpdate, db: Session = Depends(get_db)):
    result = update_query_status(db, query_id, body.status)
    if not result:
        return error_envelope("QUERY_NOT_FOUND", "Query not found", status=404)
    return success_envelope(result)

@app.get("/api/v1/admin/settings", dependencies=[Depends(verify_admin_key)])
def admin_get_settings(db: Session = Depends(get_db)):
    res = get_settings(db)
    return success_envelope({"settings": res})

@app.put("/api/v1/admin/settings", dependencies=[Depends(verify_admin_key)])
def admin_update_setting(body: dict, db: Session = Depends(get_db)):
    # body should be {"key": "...", "value": "...", "description": "..."}
    key = body.get("key")
    value = body.get("value")
    if not key or value is None:
        return error_envelope("INVALID_INPUT", "Key and value are required")
    res = update_setting(db, key, str(value), body.get("description"))
    return success_envelope(res)

@app.get("/api/v1/admin/export/delegates", dependencies=[Depends(verify_admin_key)])
def admin_export_delegates(committee_id: int = None, db: Session = Depends(get_db)):
    csv_content = export_delegates_csv(db, committee_id)
    filename = f"delegates_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# Static files — mount LAST so API routes take priority
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
