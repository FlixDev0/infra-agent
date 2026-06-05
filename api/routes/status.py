from fastapi import APIRouter
from agent.state import agent_state

router = APIRouter()

@router.get("/")
def get_status():
    return agent_state.to_dict()

@router.post("/pause")
def pause_agent():
    agent_state.running = False
    return {"message": "Agente pausado", "running": False}

@router.post("/resume")
def resume_agent():
    agent_state.running = True
    return {"message": "Agente reanudado", "running": True}

@router.post("/dry-run/{enabled}")
def set_dry_run(enabled: bool):
    agent_state.dry_run = enabled
    return {"message": f"dry_run={'activado' if enabled else 'desactivado'}", "dry_run": enabled}