import docker
from agent.remediator.base import BaseRemediator
from models.drift import DriftEvent


class FixImageHandler(BaseRemediator):
    async def remediate(self, drift: DriftEvent) -> None:
        client = docker.from_env()
        try:
            container = client.containers.get(drift.service_name)
            image = drift.expected

            print(f"[fix_image] Recreando '{drift.service_name}' con imagen {image}")

            # Guardar configuración antes de destruir
            config = container.attrs.get("HostConfig", {})
            ports = container.ports
            name = container.name

            # Detener y eliminar contenedor actual
            container.stop()
            container.remove()

            # Intentar pull de la imagen correcta
            try:
                client.images.pull(image)
            except Exception:
                print(f"[fix_image] No se pudo hacer pull de {image} — usando caché local")

            # Recrear con la imagen correcta
            client.containers.run(
                image=image,
                name=name,
                detach=True,
                ports=ports,
                host_config=client.api.create_host_config(**config) if config else None,
            )
            print(f"[fix_image] '{name}' recreado con imagen {image}")

        except docker.errors.NotFound:
            print(f"[fix_image] Contenedor '{drift.service_name}' no encontrado")
        except Exception as e:
            print(f"[fix_image] Error recreando '{drift.service_name}': {e}")
            raise