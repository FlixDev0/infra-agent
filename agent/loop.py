"""
Control loop principal del agente.
Implementa el patrón observe → diff → remediate en ciclos continuos.
"""
import asyncio
import time
import math
from datetime import datetime

from models.desired_state import DesiredState
from models.drift import DriftEvent
from models.audit import RemediationResult
from agent.observer.base import BaseObserver
from agent.diff.engine import DiffEngine
from agent.remediator.registry import get_handler
from agent.audit.logger import AuditLogger


class AgentLoop:
    def __init__(
        self,
        desired: DesiredState,
        observer: BaseObserver,
        interval_seconds: int = 30,
    ):
        self.desired = desired
        self.observer = observer
        self.interval = interval_seconds
        self.engine = DiffEngine()
        self.logger = AuditLogger()
        self._running = False
        self._remediation_attempts: dict[str, int] = {}
        self._last_remediation: dict[str, datetime] = {}

    def start(self):
        self._running = True
        asyncio.run(self._loop())

    def stop(self):
        self._running = False

    async def _loop(self):
        print(f"[agent] Loop iniciado — intervalo: {self.interval}s | dry_run: {self.desired.policies.dry_run}")
        while self._running:
            await self._tick()
            await asyncio.sleep(self.interval)

    async def _tick(self):
        try:
            snapshot = await self.observer.observe()
        except Exception as e:
            print(f"[agent] ERROR observando infraestructura: {e}")
            return

        events = self.engine.compute(self.desired, snapshot)

        if not events:
            print(f"[agent] {datetime.utcnow().isoformat()} — Sin desviaciones detectadas")
            return

        print(f"[agent] {len(events)} desviación(es) detectada(s)")
        for drift in events:
            await self._handle_drift(drift)

    async def _handle_drift(self, drift: DriftEvent):
        key = f"{drift.service_name}:{drift.drift_type}"
        policies = self.desired.policies

        attempts = self._remediation_attempts.get(key, 0)

        # Límite de intentos
        if attempts >= policies.max_remediation_attempts:
            print(f"[agent] LIMITE — '{key}' alcanzó {policies.max_remediation_attempts} intentos, requiere intervención manual")
            self.logger.log(drift, RemediationResult.SKIPPED, attempts, 0)
            return

        # Cooldown con backoff exponencial
        last = self._last_remediation.get(key)
        if last:
            backoff = policies.remediation_cooldown_seconds * (2 ** attempts)
            elapsed = (datetime.utcnow() - last).total_seconds()
            if elapsed < backoff:
                remaining = int(backoff - elapsed)
                print(f"[agent] COOLDOWN — '{key}' esperando {remaining}s (intento {attempts})")
                return

        if policies.dry_run:
            print(f"[agent] DRY_RUN — {drift.remediation_action}")
            self.logger.log(drift, RemediationResult.SKIPPED, 0, 0)
            return

        handler = get_handler(drift.drift_type)
        if not handler:
            print(f"[agent] Sin handler para {drift.drift_type}")
            return

        start = time.monotonic()
        try:
            await handler.remediate(drift)
            duration_ms = int((time.monotonic() - start) * 1000)
            self._remediation_attempts[key] = attempts + 1
            self._last_remediation[key] = datetime.utcnow()
            self.logger.log(drift, RemediationResult.SUCCESS, attempts + 1, duration_ms)
            print(f"[agent] OK — {drift.remediation_action} ({duration_ms}ms)")
        except Exception as e:
            duration_ms = int((time.monotonic() - start) * 1000)
            self._remediation_attempts[key] = attempts + 1
            self._last_remediation[key] = datetime.utcnow()
            self.logger.log(drift, RemediationResult.FAILED, attempts + 1, duration_ms, str(e))
            print(f"[agent] ERROR — {drift.remediation_action}: {e}")