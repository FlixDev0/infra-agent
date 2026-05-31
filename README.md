# infra-agent

Agente de remediación automática de infraestructura.
Implementa el patrón observe → diff → remediate en ciclos continuos.

## Requisitos

- Python 3.11+
- Docker Desktop corriendo

## Inicio rápido

```bash
# 1. Instalar dependencias
pip install -e ".[dev]"

# 2. Copiar configuración
cp .env.example .env
cp config/desired_state.example.yaml config/desired_state.yaml

# 3. Correr tests
pytest tests/unit/ -v

# 4. Levantar entorno completo
docker compose up --build
```

## Estructura

```
agent/          # Núcleo del agente
api/            # API REST con FastAPI
dashboard/      # Dashboard Streamlit
models/         # Modelos Pydantic compartidos
config/         # Archivos de estado deseado (YAML)
tests/          # Tests unitarios e integración
docker/         # Dockerfiles
```

## Correr solo el agente (sin Docker)

```bash
python -m agent.loop
```

## Correr la API

```bash
uvicorn api.main:app --reload
# Swagger en http://localhost:8000/docs
```

## Correr tests con cobertura

```bash
pytest --cov=agent --cov-report=html
```
