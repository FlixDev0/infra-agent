import asyncio
import yaml
from agent.observer.docker_observer import DockerObserver
from agent.diff.engine import DiffEngine
from models.desired_state import DesiredState

async def main():
    #Cargar estado desado
    with open("config/desired_state.yaml") as f:
        data = yaml.safe_load(f)
    desired = DesiredState(**data)
    
    # Observar infraestructura
    observer = DockerObserver(environment=desired.environment)
    snapshot = await observer.observe()

    #Calcular derivaciones
    engine = DiffEngine()
    events = engine.compute(desired, snapshot)

    if not events:
        print("Sin desviaciones - Infraestructura en estado deseado")
        return
    
    print(f" {len(events)} desviaciones detectadas:\n")
    for e in events:
        print(f"  [{e.severity.upper()}] {e.service_name} — {e.drift_type}")
        print(f"    esperado: {e.expected}")
        print(f"    actual:   {e.actual}")
        print(f"    acción:   {e.remediation_action}\n")

asyncio.run(main())