from fastapi import FastAPI
from api.routes import status, drift, audit

app = FastAPI(
    title="Infra Agent API",
    description="Control y monitoreo del agente de remediación automática",
    version="0.1.0",
)

app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(drift.router,  prefix="/drift",  tags=["drift"])
app.include_router(audit.router,  prefix="/audit",  tags=["audit"])


@app.get("/health")
def health():
    return {"status": "ok"}
