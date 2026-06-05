"""
Dashboard del Infra Agent — Versión profesional.
Correr con: streamlit run dashboard/app.py
"""
import streamlit as st
import httpx
from datetime import datetime
from collections import Counter

API_URL = "http://localhost:8000"

# ── Configuración de página ──
st.set_page_config(
    page_title="Infra Agent — Panel de Control",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ──
st.markdown("""
<style>
    /* Fuente y fondo */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Métricas */
    [data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 16px 20px;
    }
    [data-testid="metric-container"] label {
        color: #8b92a5 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #e8eaf0 !important;
        font-size: 28px !important;
        font-weight: 600 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #13151f;
        border-right: 1px solid #2d3250;
    }

    /* Títulos */
    h1 { color: #e8eaf0 !important; font-weight: 700 !important; }
    h2, h3 { color: #c8cad4 !important; font-weight: 600 !important; }

    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid #2d3250 !important;
        border-radius: 8px !important;
        background-color: #1e2130 !important;
    }

    /* Divider */
    hr { border-color: #2d3250 !important; }

    /* Badges de severidad */
    .badge-critical { background:#ff4d4d22; color:#ff4d4d; border:1px solid #ff4d4d55; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-high     { background:#ff8c0022; color:#ff8c00; border:1px solid #ff8c0055; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-medium   { background:#ffd70022; color:#ffd700; border:1px solid #ffd70055; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-low      { background:#00c85322; color:#00c853; border:1px solid #00c85355; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:600; }

    /* Status indicator */
    .status-active  { color:#00c853; font-weight:700; }
    .status-paused  { color:#ff4d4d; font-weight:700; }

    /* Card info */
    .info-card {
        background:#1e2130;
        border:1px solid #2d3250;
        border-radius:10px;
        padding:16px 20px;
        margin-bottom:12px;
    }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──
def fetch(endpoint: str) -> dict:
    try:
        r = httpx.get(f"{API_URL}{endpoint}", timeout=3)
        return r.json()
    except Exception:
        return {}

def severity_badge(severity: str) -> str:
    icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    icon = icons.get(severity, "⚪")
    return f'<span class="badge-{severity}">{icon} {severity.upper()}</span>'

def result_icon(result: str) -> str:
    return {"success": "✅", "failed": "❌", "skipped": "⏭️"}.get(result, "❓")


# ── Sidebar ──
with st.sidebar:
    st.markdown("## 🛡️ Infra Agent")
    st.caption("Panel de Control v1.0")
    st.divider()

    st.markdown("### ⚙️ Controles")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏸ Pausar", use_container_width=True):
            httpx.post(f"{API_URL}/status/pause")
            st.toast("Agente pausado", icon="⏸")
    with col2:
        if st.button("▶ Reanudar", use_container_width=True):
            httpx.post(f"{API_URL}/status/resume")
            st.toast("Agente reanudado", icon="▶")

    st.divider()

    st.markdown("### 🔧 Configuración")
    dry_run = st.toggle("Modo Dry Run", value=False)
    if st.button("Aplicar cambios", use_container_width=True, type="primary"):
        httpx.post(f"{API_URL}/status/dry-run/{dry_run}")
        st.toast(f"Dry run {'activado' if dry_run else 'desactivado'}", icon="🔧")

    st.divider()

    st.markdown("### 🔄 Actualización")
    auto_refresh = st.toggle("Auto-refresh (15s)", value=True)
    if st.button("🔃 Actualizar ahora", use_container_width=True):
        st.rerun()

    st.divider()
    st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")


# ── Cargar datos ──
status_data = fetch("/status/")
drift_data  = fetch("/drift/")
audit_data  = fetch("/audit/?limit=100")

running  = status_data.get("running", False)
dry_mode = status_data.get("dry_run", True)
entries  = audit_data.get("entries", [])
events   = drift_data.get("events", [])

# ── Header ──
col_title, col_status = st.columns([3, 1])
with col_title:
    st.title("Panel de Control — Infra Agent")
    st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
with col_status:
    st.markdown("<br>", unsafe_allow_html=True)
    if running:
        st.markdown('<p class="status-active">● AGENTE ACTIVO</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-paused">● AGENTE PAUSADO</p>', unsafe_allow_html=True)

st.divider()

# ── Métricas ──
c1, c2, c3, c4, c5 = st.columns(5)

success_count = sum(1 for e in entries if e.get("result") == "success")
failed_count  = sum(1 for e in entries if e.get("result") == "failed")

with c1:
    st.metric("Desviaciones activas", drift_data.get("total", 0))
with c2:
    st.metric("Remediaciones totales", status_data.get("total_remediations", 0))
with c3:
    st.metric("Exitosas", success_count, delta=None)
with c4:
    st.metric("Fallidas", failed_count, delta=None)
with c5:
    last_tick = status_data.get("last_tick")
    if last_tick:
        t = datetime.fromisoformat(last_tick)
        elapsed = int((datetime.utcnow() - t).total_seconds())
        st.metric("Último ciclo", f"{elapsed}s atrás")
    else:
        st.metric("Último ciclo", "—")

st.divider()

# ── Layout principal: 2 columnas ──
left, right = st.columns([3, 2])

with left:
    # ── Desviaciones activas ──
    st.markdown("### ⚠️ Desviaciones activas")

    if not events:
        st.success("✅ Sin desviaciones — infraestructura en estado deseado", icon="✅")
    else:
        for e in events:
            severity = e.get("severity", "low")
            with st.expander(
                f"{e['service_name']} — {e['drift_type'].replace('_', ' ').title()}",
                expanded=True
            ):
                st.markdown(
                    f"**Severidad:** {severity_badge(severity)}",
                    unsafe_allow_html=True
                )
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Esperado:** `{e.get('expected')}`")
                    st.markdown(f"**Actual:** `{e.get('actual')}`")
                with col_b:
                    st.markdown(f"**Acción:** {e.get('remediation_action')}")
                    detected = e.get("detected_at", "")[:19].replace("T", " ")
                    st.markdown(f"**Detectado:** `{detected}`")

    st.divider()

    # ── Historial de remediaciones ──
    st.markdown("### 📋 Historial de remediaciones")

    if not entries:
        st.info("Sin remediaciones registradas aún")
    else:
        table_data = []
        for e in reversed(entries[-20:]):
            drift = e.get("drift", {})
            result = e.get("result", "")
            executed = e.get("executed_at", "")[:19].replace("T", " ")
            table_data.append({
                "": result_icon(result),
                "Servicio": drift.get("service_name", ""),
                "Tipo": drift.get("drift_type", "").replace("_", " "),
                "Severidad": drift.get("severity", "").upper(),
                "ms": e.get("duration_ms", 0),
                "Ejecutado": executed,
            })

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "": st.column_config.TextColumn(width="small"),
                "ms": st.column_config.NumberColumn(
                    "Duración (ms)",
                    format="%d ms",
                ),
            }
        )

with right:
    # ── Gráfico por tipo de drift ──
    st.markdown("### 📊 Remediaciones por tipo")

    if entries:
        drift_types = [
            e.get("drift", {}).get("drift_type", "").replace("_", " ")
            for e in entries
            if e.get("result") == "success"
        ]
        if drift_types:
            counts = Counter(drift_types)
            st.bar_chart(counts, color="#4f8ef7")
        else:
            st.info("Sin remediaciones exitosas aún")
    else:
        st.info("Sin datos aún")

    st.divider()

    # ── Gráfico por resultado ──
    st.markdown("### 📈 Resultados")

    if entries:
        results = Counter(e.get("result", "") for e in entries)
        result_data = {
            "✅ Exitosas":  results.get("success", 0),
            "❌ Fallidas":  results.get("failed", 0),
            "⏭️ Omitidas": results.get("skipped", 0),
        }
        st.bar_chart(result_data, color="#00c853")
    else:
        st.info("Sin datos aún")

    st.divider()

    # ── Info del sistema ──
    st.markdown("### 🖥️ Sistema")
    st.markdown(f"""
    <div class="info-card">
        <p style="margin:4px 0; color:#8b92a5; font-size:12px;">ENTORNO</p>
        <p style="margin:0 0 12px 0; font-weight:600;">{status_data.get('environment', 'staging')}</p>
        <p style="margin:4px 0; color:#8b92a5; font-size:12px;">INTERVALO DE CICLO</p>
        <p style="margin:0 0 12px 0; font-weight:600;">{status_data.get('interval_seconds', 15)}s</p>
        <p style="margin:4px 0; color:#8b92a5; font-size:12px;">MODO</p>
        <p style="margin:0; font-weight:600;">{'🔵 Dry Run' if dry_mode else '🟠 Remediación activa'}</p>
    </div>
    """, unsafe_allow_html=True)


# ── Auto-refresh ──
if auto_refresh:
    import time
    time.sleep(15)
    st.rerun()