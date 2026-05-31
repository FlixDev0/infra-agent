from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_drift():
    # TODO: retornar últimos DriftEvents detectados
    return {"events": []}
