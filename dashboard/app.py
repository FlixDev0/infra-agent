"""
Dashboard Streamlit — conecta con la API del agente.
Correr con: streamlit run dashboard/app.py
"""
import streamlit as st
import httpx

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Infra Agent", page_icon="🤖", layout="wide")
st.title("Infra Agent — Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado del agente")
    try:
        r = httpx.get(f"{API_URL}/status/", timeout=3)
        st.json(r.json())
    except Exception:
        st.error("No se pudo conectar con la API. ¿Está corriendo?")

with col2:
    st.subheader("Desviaciones activas")
    try:
        r = httpx.get(f"{API_URL}/drift/", timeout=3)
        st.json(r.json())
    except Exception:
        st.error("Sin datos de drift disponibles.")

st.subheader("Historial de remediaciones")
try:
    r = httpx.get(f"{API_URL}/audit/", timeout=3)
    data = r.json()
    st.metric("Total remediaciones", data["total"])
    st.json(data["entries"][-10:] if data["entries"] else [])
except Exception:
    st.error("Sin historial disponible.")
