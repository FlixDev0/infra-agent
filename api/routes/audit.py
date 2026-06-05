from fastapi import APIRouter, Query
from agent.audit.logger import AuditLogger

router = APIRouter()
_logger = AuditLogger()


@router.get("/")
def get_audit(limit: int = Query(default=20, le=100)):
    entries = _logger.read_all()
    return {
        "total": len(entries),
        "entries": [e.model_dump() for e in entries[-limit:]],
    }
