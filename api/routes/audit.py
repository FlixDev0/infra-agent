from fastapi import APIRouter
from agent.audit.logger import AuditLogger

router = APIRouter()
_logger = AuditLogger()


@router.get("/")
def get_audit():
    entries = _logger.read_all()
    return {"total": len(entries), "entries": [e.model_dump() for e in entries]}
