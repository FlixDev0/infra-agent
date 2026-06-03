import yaml
from models.desired_state import DesiredState
from agent.observer.docker_observer import DockerObserver
from agent.loop import AgentLoop

def main():
    with open("config/desired_state.yaml") as f:
        data = yaml.safe_load(f)
    desired = DesiredState(**data)

    observer = DockerObserver(environment=desired.environment)
    loop = AgentLoop(desired=desired, observer=observer, interval_seconds=15)

    print(" Agente iniciado ")
    loop.start()

if __name__ == "__main__":
    main()