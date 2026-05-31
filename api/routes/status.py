from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_status():
    # TODO: conectar con el estado real del AgentLoop
    return {"agent": "running", "interval_seconds": 30, "dry_run": False}
