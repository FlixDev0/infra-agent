from fastapi import APIRouter
from agent.state import agent_state 

router = APIRouter()


@router.get("/")
def get_drift():
    return {
        "total": len(agent_state.current_drifts),
        "events": [e.model_dump() for e in agent_state.current_drifts],
    }