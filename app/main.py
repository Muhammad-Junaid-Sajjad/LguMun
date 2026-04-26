import time
import logging
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
from app.schemas import DelegateCreate, TransferRequest, AdminQueryCreate, QueryReply, QueryStatusUpdate, DelegateQueryCreate, AnnouncementCreate
from app.services import (
    get_all_committees, get_committee_by_id, register_delegate,
    get_delegates_count, transfer_delegate,
    get_admin_stats, get_all_delegates_admin, get_delegate_by_id_admin,
    get_committees_for_admin, update_committee,
    create_query, get_queries, reply_to_query, update_query_status,
    get_settings, update_setting, export_delegates_csv,
    # GAP-001: Delegate Query System
    create_delegate_query, get_delegate_query_by_tracking, get_all_delegate_queries_admin, reply_delegate_query,
    # GAP-003: Announcements
    create_announcement, get_active_announcements, get_all_announcements_admin, dismiss_announcement,
    # GAP-004: Country Allocation
    set_committee_country_list, auto_assign_countries, get_committee_allocations, publish_committee_allocations,
    get_global_countries, import_to_committee_pool,
)
from app.exceptions import AppException
from app.constants import RATE_LIMIT, ADMIN_API_KEY_HEADER

logger = logging.getLogger(__name__)

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
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "X-Admin-API-Key"],
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
    logger.warning("App exception: %s - %s", exc.code, exc.message)
    return error_envelope(exc.code, exc.message, exc.field, exc.status_code, exc.data)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = exc.detail or "HTTP_ERROR"
    message = str(exc.detail) if exc.detail else "An HTTP error occurred"
    status = exc.status_code
    logger.warning("HTTP exception: %s - status=%d", code, status)
    return error_envelope(code, message, status=status)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return error_envelope(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred. Please try again later.",
        status=500
    )

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "timestamp": time.time()}

@app.get("/api/v1/settings")
def public_settings(db: Session = Depends(get_db)):
    # Public settings that don't require authentication
    # Returns only display-suitable settings (no keys, no flags potentially hiding features)
    all_settings = get_settings(db)
    public_keys = {'event_title', 'event_date', 'event_venue', 'event_name', 'registration_open', 'transfer_enabled'}
    public_settings = [s for s in all_settings if s['key'] in public_keys]
    return success_envelope({"settings": public_settings})

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

# ═══════════════════════════════════════════════════════════════════════════════
# GAP-001: DELEGATE QUERY SYSTEM (Public API)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/query", tags=["Queries"])
def submit_delegate_query(body: dict, db: Session = Depends(get_db)):
    """Submit a new delegate query (public endpoint)."""
    # Validate required fields
    required = ["roll_number", "name", "email", "category", "message"]
    for field in required:
        if not body.get(field):
            return error_envelope("MISSING_FIELD", f"Field '{field}' is required")

    # Validate category
    valid_categories = ["Payment", "Technical", "Research", "Other"]
    if body.get("category") not in valid_categories:
        return error_envelope("INVALID_CATEGORY", f"Category must be one of: {', '.join(valid_categories)}")

    result = create_delegate_query(db, body)
    return success_envelope(result)


@app.get("/api/v1/query/{tracking_id}", tags=["Queries"])
def check_query_status(tracking_id: str, db: Session = Depends(get_db)):
    """Check query status by tracking ID (public endpoint)."""
    result = get_delegate_query_by_tracking(db, tracking_id)
    if not result:
        return error_envelope("QUERY_NOT_FOUND", "Query not found", status=404)
    return success_envelope(result)


# Admin: Delegate Queries Management
@app.get("/api/v1/admin/delegate-queries", dependencies=[Depends(verify_admin_key)])
def admin_list_delegate_queries(
    status: str = "all",
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    result = get_all_delegate_queries_admin(db, status, page, per_page)
    return success_envelope(result)


@app.put("/api/v1/admin/delegate-queries/{query_id}/reply", dependencies=[Depends(verify_admin_key)])
def admin_reply_delegate_query(query_id: int, body: QueryReply, db: Session = Depends(get_db)):
    result = reply_delegate_query(db, query_id, body.reply)
    if not result:
        return error_envelope("QUERY_NOT_FOUND", "Query not found", status=404)
    return success_envelope(result)


# ═══════════════════════════════════════════════════════════════════════════════
# GAP-003: ANNOUNCEMENTS SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/admin/announcements", dependencies=[Depends(verify_admin_key)])
def admin_create_announcement(body: AnnouncementCreate, db: Session = Depends(get_db)):
    """Create a new announcement."""
    # Validate priority
    valid_priorities = ["normal", "important", "urgent"]
    if body.priority not in valid_priorities:
        return error_envelope("INVALID_PRIORITY", f"Priority must be one of: {', '.join(valid_priorities)}")

    result = create_announcement(db, body.model_dump(), "Admin")
    return success_envelope(result)


@app.get("/api/v1/announcements/active", tags=["Announcements"])
def get_active_announcements_public(db: Session = Depends(get_db)):
    """Get active announcements for polling (public endpoint)."""
    result = get_active_announcements(db)
    return success_envelope({"announcements": result})


@app.get("/api/v1/admin/announcements", dependencies=[Depends(verify_admin_key)])
def admin_list_announcements(db: Session = Depends(get_db)):
    """Get all announcements (including archived) for admin panel."""
    result = get_all_announcements_admin(db)
    return success_envelope({"announcements": result})


@app.put("/api/v1/admin/announcements/{announcement_id}/dismiss", dependencies=[Depends(verify_admin_key)])
def admin_dismiss_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """Dismiss an announcement."""
    result = dismiss_announcement(db, announcement_id)
    if not result:
        return error_envelope("NOT_FOUND", "Announcement not found", status=404)
    return success_envelope(result)


# ═══════════════════════════════════════════════════════════════════════════════
# GAP-004: COUNTRY ALLOCATION ENGINE (Admin API)
# ═══════════════════════════════════════════════════════════════════════════════
# GAP-004: COUNTRY ALLOCATION ENGINE - API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/admin/committees/{committee_id}/country-list", dependencies=[Depends(verify_admin_key)])
def admin_set_country_list(committee_id: int, body: dict, db: Session = Depends(get_db)):
    """Step 1: Set the list of countries/personalities available for a committee.

    Accepts values as:
    - JSON array: ["USA", "Iran", "Israel", ...]
    - Text string (comma/newline separated): "USA, Iran, Israel\nChina, Russia"
    - PDF/content reference

    Returns auto-classification by tier (P5, Regional, Conflict, etc.)
    """
    values = body.get("values", [])
    alloc_type = body.get("type", "country")  # "country" or "personality"
    agenda = body.get("agenda", "")

    if not values:
        return error_envelope("INVALID_INPUT", "A list of values is required")

    result = set_committee_country_list(db, committee_id, values, alloc_type, agenda)
    return success_envelope(result)


@app.post("/api/v1/admin/committees/{committee_id}/auto-assign", dependencies=[Depends(verify_admin_key)])
def admin_auto_assign(committee_id: int, body: dict = None, db: Session = Depends(get_db)):
    """Step 2: Run the auto-assignment algorithm (Drafts only).

    Strategies:
    - "smart" (default): P5 first, then Regional, then Conflict, etc.
    - "random": Shuffle all and assign randomly
    - "alphabetical": Sort by name and assign in order
    """
    strategy = body.get("strategy", "smart") if body else "smart"

    result = auto_assign_countries(db, committee_id, strategy)
    return success_envelope(result)


@app.get("/api/v1/admin/committees/{committee_id}/allocations", dependencies=[Depends(verify_admin_key)])
def admin_get_allocations(committee_id: int, include_unpublished: bool = True, db: Session = Depends(get_db)):
    """Step 3: Review current allocations.

    Returns allocations with tier and category classification for visualization.
    """
    result = get_committee_allocations(db, committee_id, include_unpublished)
    return success_envelope({"allocations": result})


@app.get("/api/v1/admin/committees/{committee_id}/allocation-preview", dependencies=[Depends(verify_admin_key)])
def admin_get_allocation_preview(committee_id: int, db: Session = Depends(get_db)):
    """Get a preview of allocation breakdown before assignment.

    Shows tier-by-tier breakdown of available countries vs registered delegates.
    """
    result = get_allocation_preview(db, committee_id)
    return success_envelope(result)


@app.put("/api/v1/admin/allocations/{allocation_id}", dependencies=[Depends(verify_admin_key)])
def admin_update_allocation(allocation_id: int, body: dict, db: Session = Depends(get_db)):
    """Update a single allocation (swap country, lock/unlock).

    Admin can manually adjust allocation for any delegate.
    """
    new_value = body.get("value")
    is_locked = body.get("locked")

    result = update_allocation(db, allocation_id, new_value, is_locked)
    return success_envelope(result)


@app.post("/api/v1/admin/committees/{committee_id}/publish-allocations", dependencies=[Depends(verify_admin_key)])
def admin_publish_allocations(committee_id: int, db: Session = Depends(get_db)):
    """Step 4: Publish allocations (makes them visible to delegates).

    Triggers Email 2 notification to all assigned delegates.
    """
    result = publish_committee_allocations(db, committee_id)
    return success_envelope(result)


# ═══════════════════════════════════════════════════════════════════════════════
# BLOCKED ASSIGNMENTS (Conflict of Interest Prevention)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/admin/committees/{committee_id}/blocked", dependencies=[Depends(verify_admin_key)])
def admin_add_blocked(committee_id: int, body: dict, db: Session = Depends(get_db)):
    """Add a conflict-of-interest block (delegate cannot be assigned this value)."""
    delegate_id = body.get("delegate_id")
    value = body.get("value")
    reason = body.get("reason")

    if not delegate_id or not value:
        return error_envelope("INVALID_INPUT", "delegate_id and value are required")

    result = add_blocked_assignment(db, committee_id, delegate_id, value, reason)
    return success_envelope(result)


@app.get("/api/v1/admin/committees/{committee_id}/blocked", dependencies=[Depends(verify_admin_key)])
def admin_list_blocked(committee_id: int, db: Session = Depends(get_db)):
    """List all blocked assignments for a committee."""
    from app.models import BlockedAssignment, Delegate

    blocked = db.query(BlockedAssignment).filter(
        BlockedAssignment.committee_id == committee_id
    ).all()

    return success_envelope({
        "blocked": [
            {
                "id": b.id,
                "delegate_id": b.delegate_id,
                "delegate_name": b.delegate.full_name if b.delegate else "Unknown",
                "blocked_value": b.blocked_value,
                "reason": b.reason,
                "created_at": b.created_at.isoformat() if b.created_at else None
            }
            for b in blocked
        ]
    })


@app.delete("/api/v1/admin/blocked/{block_id}", dependencies=[Depends(verify_admin_key)])
def admin_remove_blocked(block_id: int, db: Session = Depends(get_db)):
    """Remove a blocked assignment."""
    from app.models import BlockedAssignment

    block = db.query(BlockedAssignment).filter(BlockedAssignment.id == block_id).first()
    if not block:
        return error_envelope("NOT_FOUND", "Blocked assignment not found", status=404)

    db.delete(block)
    db.commit()
    return success_envelope({"status": "deleted"})


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL COUNTRY POOL & PNA PERSONALITIES MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/admin/countries/global", dependencies=[Depends(verify_admin_key)])
def admin_get_global_countries(region: str = None, db: Session = Depends(get_db)):
    """Get all countries from global pool, optionally filtered by region."""
    result = get_global_countries(db, region)
    return success_envelope({"countries": result})


@app.get("/api/v1/admin/personalities", dependencies=[Depends(verify_admin_key)])
def admin_get_pna_personalities(db: Session = Depends(get_db)):
    """Get all PNA personalities from global pool."""
    from app.models import CommitteeAllocationPool

    personalities = db.query(CommitteeAllocationPool).filter(
        CommitteeAllocationPool.committee_id == None,  # Global pool
        CommitteeAllocationPool.allocation_type == "personality"
    ).order_by(CommitteeAllocationPool.tier).all()

    return success_envelope({
        "personalities": [
            {
                "id": p.id,
                "name": p.value,
                "tier": p.tier,
                "category": p.category,
                "is_active": p.is_active
            }
            for p in personalities
        ]
    })


@app.put("/api/v1/admin/personalities/{item_id}/toggle", dependencies=[Depends(verify_admin_key)])
def admin_toggle_personality(item_id: int, body: dict, db: Session = Depends(get_db)):
    """Activate or deactivate a PNA personality."""
    is_active = body.get("is_active", True)
    result = toggle_pool_item_status(db, item_id, is_active)
    return success_envelope(result)


@app.get("/api/v1/admin/committees/{committee_id}/pool", dependencies=[Depends(verify_admin_key)])
def admin_get_committee_pool(committee_id: int, db: Session = Depends(get_db)):
    """Get the committee-specific allocation pool."""
    from app.models import CommitteeAllocationPool

    items = db.query(CommitteeAllocationPool).filter(
        CommitteeAllocationPool.committee_id == committee_id
    ).order_by(CommitteeAllocationPool.tier, CommitteeAllocationPool.value).all()

    return success_envelope({
        "items": [
            {
                "id": i.id,
                "value": i.value,
                "tier": i.tier,
                "category": i.category,
                "is_active": i.is_active,
                "source": i.source
            }
            for i in items
        ]
    })


@app.post("/api/v1/admin/committees/{committee_id}/pool/import", dependencies=[Depends(verify_admin_key)])
def admin_import_to_pool(committee_id: int, body: dict, db: Session = Depends(get_db)):
    """Import countries from global pool to committee pool."""
    values = body.get("values", [])
    if not values:
        return error_envelope("INVALID_INPUT", "values list is required")

    result = import_to_committee_pool(db, committee_id, values)
    return success_envelope(result)


@app.post("/api/v1/admin/pool/{item_id}/toggle", dependencies=[Depends(verify_admin_key)])
def admin_toggle_pool_item(item_id: int, body: dict, db: Session = Depends(get_db)):
    """Toggle active status of a pool item."""
    is_active = body.get("is_active", True)
    result = toggle_pool_item_status(db, item_id, is_active)
    return success_envelope(result)


# Static files — mount LAST so API routes take priority
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
