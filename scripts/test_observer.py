import asyncio
from agent.observer.docker_observer import DockerObserver

async def main():
    observer = DockerObserver(environment="local")
    snapshot = await observer.observe()

    print(f"\nEntorno: {snapshot.environment}")
    print(f"Observando: {snapshot.environment}")
    print(f"Servicios encontrados: {len(snapshot.environment)}\n")

    for svc in snapshot.services:
        print(f"[{svc.status.upper}] {svc.name}")
        print(f"Imagen: {svc.image}")
        print(f"Réplicas: {svc.replicas_running}")
        print(f"Puertos: {[(p.host, p.container) for p in svc.ports]}")
        print(f"CPU: {svc.cpu_usage}%")
        print(f"RAM: {svc.memory_usage_mb} MB\n")
    if snapshot.unknown_containers:
        print(f"Contenedores no declarados: {snapshot.unknown_containers}")

asyncio.run(main())