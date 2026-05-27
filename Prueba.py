import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
import time
import bcrypt
import pytz
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ─────────────────────────────────────────
# 0. CONFIGURACIÓN DEL LOGO OFICIAL (URL DIRECTA)
# ─────────────────────────────────────────
LOGO_SRC = "https://i.ibb.co/nNxy2zyt/Gd-L-removebg-preview.png"

# ─────────────────────────────────────────
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Gota de Leche - Sistema Maestro",
    layout="wide",
    page_icon=LOGO_SRC, # El ícono de la pestaña ahora es el logo oficial
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    /* Ocultar definitivamente el texto del icono de la flecha rota en los expanders */
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary [data-testid="stIconVisibility"],
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary div:first-child {
        display: none !important;
    }
    
    /* Asegurar que el título ocupe el espacio correcto sin la flecha */
    [data-testid="stExpander"] summary > div {
        width: 100% !important;
    }

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
    }

    /* ── Fondo global ── */
    .stApp {
        background: #070d1a !important;
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Eliminar padding superior por defecto ── */
    .block-container { padding-top: 1.5rem !important; }

    /* ══════════════════════════════
       LOGIN
    ══════════════════════════════ */
    .centered-login {
        max-width: 420px;
        margin: 0 auto;
        text-align: center;
        padding-top: 5vh;
    }
    .centered-login h1, .centered-login p { text-align: center !important; }

    /* Formulario de login */
    .stForm {
        background: linear-gradient(160deg, #111827 0%, #0f172a 100%) !important;
        border: 1px solid rgba(99, 131, 246, 0.35) !important;
        border-radius: 20px !important;
        padding: 2rem 2rem 1.6rem 2rem !important;
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.12), 0 20px 60px rgba(0,0,0,0.5) !important;
    }
    /* Botón submit del login */
    .stForm [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
        color: #fff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.06em !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4) !important;
    }
    .stForm [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 28px rgba(79, 70, 229, 0.55) !important;
    }

    /* ══════════════════════════════
       SIDEBAR PROFESIONAL
    ══════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1526 0%, #090f1e 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    section[data-testid="stSidebar"] > div { padding: 0 !important; }

    /* Header del sidebar */
    .sidebar-header {
        background: rgba(15, 23, 42, 0.6);
        padding: 24px 20px 20px 20px;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .sidebar-user-name {
        color: #f1f5f9;
        font-size: 1rem;
        font-weight: 700;
        margin: 10px 0 2px 0;
        letter-spacing: 0.01em;
    }
    .sidebar-user-role {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 500;
        margin-top: 4px;
    }

    /* ══════════════════════════════
       SIDEBAR — RADIO COMO NAV
    ══════════════════════════════ */
    /* Ocultar el label del radio group */
    section[data-testid="stSidebar"] .stRadio > label { display: none !important; }

    /* Contenedor de opciones en columna */
    section[data-testid="stSidebar"] .stRadio > div {
        display: flex !important;
        flex-direction: column !important;
        gap: 2px !important;
        padding: 4px 0 !important;
    }

    /* Cada opción del radio */
    section[data-testid="stSidebar"] .stRadio > div > label {
        display: flex !important;
        align-items: center !important;
        padding: 11px 20px !important;
        border-left: 3px solid transparent !important;
        border-radius: 0 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        color: #94a3b8 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em !important;
        background: transparent !important;
        margin: 0 !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(59,130,246,0.08) !important;
        color: #e2e8f0 !important;
        border-left-color: rgba(59,130,246,0.35) !important;
    }
    /* Opción seleccionada */
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(59,130,246,0.12) !important;
        color: #60a5fa !important;
        border-left-color: #3b82f6 !important;
        font-weight: 600 !important;
    }
    /* Ocultar el círculo del radio */
    section[data-testid="stSidebar"] .stRadio > div > label > div:first-child {
        display: none !important;
    }

    /* Botón cerrar sesión en sidebar */
    .sidebar-logout .stButton button {
        background: rgba(239,68,68,0.08) !important;
        color: #f87171 !important;
        border: 1px solid rgba(239,68,68,0.2) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        transition: all 0.2s !important;
    }
    .sidebar-logout .stButton button:hover {
        background: rgba(239,68,68,0.15) !important;
        border-color: rgba(239,68,68,0.4) !important;
    }

    /* ══════════════════════════════
       PAGE HEADER UNIFICADO
    ══════════════════════════════ */
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding: 0 0 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 28px;
    }
    .page-header-left h2 {
        color: #f1f5f9;
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0 0 4px 0;
        letter-spacing: -0.01em;
    }
    .page-header-left p {
        color: #64748b;
        font-size: 0.82rem;
        margin: 0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .page-header-right {
        text-align: right;
        font-size: 0.8rem;
        color: #475569;
        font-weight: 500;
        line-height: 1.6;
    }
    .page-header-badge {
        display: inline-block;
        background: rgba(59,130,246,0.12);
        color: #60a5fa;
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 4px;
        letter-spacing: 0.04em;
    }

    /* ══════════════════════════════
       TARJETAS KPI
    ══════════════════════════════ */
    .kpi-card {
        background: linear-gradient(145deg, #131f35 0%, #0d1526 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: var(--accent, linear-gradient(90deg, #3b82f6, #6366f1));
    }
    .kpi-label {
        color: #64748b;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .kpi-value {
        color: #f1f5f9;
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.02em;
    }
    .kpi-sub {
        color: #475569;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 6px;
    }
    .kpi-progress-bar {
        height: 4px;
        background: rgba(255,255,255,0.06);
        border-radius: 4px;
        margin-top: 12px;
        overflow: hidden;
    }
    .kpi-progress-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #3b82f6, #6366f1);
        transition: width 0.6s ease;
    }

    /* ══════════════════════════════
       TARJETAS DE STOCK
    ══════════════════════════════ */
    .metric-card {
        background: linear-gradient(145deg, #131f35 0%, #0d1526 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        margin-bottom: 14px;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-label {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 10px;
        min-height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .metric-value {
        color: #38bdf8;
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.02em;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-top: 12px;
    }
    .status-ok    { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
    .status-warn  { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
    .status-crit  { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.2); }

    /* ══════════════════════════════
       SECCIÓN DE TÍTULO (sub-header)
    ══════════════════════════════ */
    .section-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 20px 0 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ══════════════════════════════
       FICHA DATOS
    ══════════════════════════════ */
    .ficha-seccion-datos {
        background: rgba(30, 41, 59, 0.5);
        border-left: 3px solid #3b82f6;
        padding: 14px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        font-size: 0.93rem;
        line-height: 1.6;
    }

    /* ══════════════════════════════
       TABLAS Y DATAFRAMES
    ══════════════════════════════ */
    .stDataFrame { border-radius: 12px !important; overflow: hidden; }

    /* ══════════════════════════════
       EXPANDERS — ocultar ícono ▸ y estilizar
    ══════════════════════════════ */
    /* El ícono _arrow_ de Streamlit es un span con aria-hidden */
    [data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpander"] summary > div > div:first-child {
        display: none !important;
    }
    /* Ocultar el SVG de flecha dentro del expander */
    [data-testid="stExpander"] summary svg {
        display: none !important;
    }
    [data-testid="stExpander"] summary::-webkit-details-marker {
        display: none !important;
    }
    /* En Streamlit el label del expander va dentro de un <p> con clase especial */
    [data-testid="stExpander"] summary p {
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
    }
    /* Estilo del summary */
    [data-testid="stExpander"] summary {
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        list-style: none !important;
        cursor: pointer !important;
        transition: background 0.15s !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: rgba(30, 41, 59, 0.9) !important;
        border-color: rgba(59,130,246,0.25) !important;
    }
    [data-testid="stExpander"][open] > summary {
        border-radius: 10px 10px 0 0 !important;
        border-bottom-color: rgba(59,130,246,0.2) !important;
    }

    /* ══════════════════════════════
       INPUTS Y SELECTBOXES
    ══════════════════════════════ */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #0d1526 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-size: 0.92rem !important;
        transition: border-color 0.2s !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    }

    /* ══════════════════════════════
       OCULTAR ÍCONO ▸ DE TODOS LOS BOTONES
    ══════════════════════════════ */
    /* El ícono _arrow_ que Streamlit agrega a st.button */
    button[data-testid="stBaseButton-secondary"] svg,
    button[data-testid="stBaseButton-primary"] svg,
    .stButton button svg {
        display: none !important;
    }
    /* Alternativa: el span del ícono dentro del botón */
    .stButton button [data-testid="stMarkdownContainer"] + span,
    .stButton button > div > span:first-child {
        display: none !important;
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 14px rgba(79,70,229,0.3) !important;
    }
    .stButton button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(79,70,229,0.45) !important;
    }

    /* ══════════════════════════════
       ALERTS / MENSAJES
    ══════════════════════════════ */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        font-size: 0.9rem !important;
    }

    /* ══════════════════════════════
       DIVIDER
    ══════════════════════════════ */
    hr { border-color: rgba(255,255,255,0.07) !important; }

    /* ══════════════════════════════
       TABS
    ══════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 4px !important;
        border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.04em !important;
        padding: 10px 20px !important;
        border-radius: 8px 8px 0 0 !important;
        border: none !important;
        transition: color 0.2s !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(59,130,246,0.1) !important;
        color: #60a5fa !important;
        border-bottom: 2px solid #3b82f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 2. UTILIDADES Y CONFIGURACIÓN HORARIA
# ─────────────────────────────────────────
CHILE_TZ = pytz.timezone("America/Santiago")

def get_local_now() -> str:
    return datetime.now(CHILE_TZ).strftime("%Y-%m-%d %H:%M:%S")

def get_local_date() -> str:
    return datetime.now(CHILE_TZ).strftime("%d/%m/%Y")

def verify_password(plain: str, stored) -> bool:
    stored = str(stored)
    if stored.startswith("$2b$") or stored.startswith("$2a$"):
        return bcrypt.checkpw(plain.encode(), stored.encode())
    return plain == stored

def clean_timestamp_to_date(raw_date) -> str:
    if not raw_date or raw_date == "-":
        return "-"
    raw_str = str(raw_date).strip()
    if 'T' in raw_str:
        raw_str = raw_str.split('T')[0]
    
    if '-' in raw_str and not raw_str.startswith('-'):
        try:
            parts = raw_str.split('-')
            if len(parts[0]) == 4:
                dt = datetime.strptime(raw_str, "%Y-%m-%d")
                return dt.strftime("%d/%m/%Y")
        except:
            pass
    return raw_str

def export_pdf_component(child_data):
    f_ingreso_pdf = clean_timestamp_to_date(child_data.get('fecha_ingreso', '-'))
    f_egreso_pdf = clean_timestamp_to_date(child_data.get('fecha_egreso', '-'))

    html_content = f"""
    <div id="pdf-container" style="font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; padding: 0; background: #ffffff; max-width: 820px; margin: auto; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden;">
        
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 30px 40px; color: white; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <img src="{LOGO_SRC}" style="height: 65px; width: auto; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.15));" alt="Logo">
                <div>
                    <h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 0.5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">GOTAS DE LECHE</h1>
                    <p style="margin: 4px 0 0 0; color: #bfdbfe; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px;">Ficha Oficial del Beneficiario</p>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 11px; color: #93c5fd; font-weight: bold; text-transform: uppercase; margin-bottom: 6px;">Documento Clínico - Social</div>
                <div style="font-size: 15px; font-weight: bold; color: #1e3a8a; background: #ffffff; padding: 6px 16px; border-radius: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: inline-block;">Ficha N° {child_data.get('ficha', '-')}</div>
            </div>
        </div>

        <div style="padding: 40px;">
            <div style="text-align: right; font-size: 12px; color: #64748b; margin-bottom: 25px; font-style: italic;">
                Fecha de Emisión: {get_local_date()}
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 25px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #3b82f6; padding-bottom: 6px;">
                    <span style="font-size: 18px; margin-right: 8px;">👶</span>
                    <h3 style="margin: 0; color: #1e3a8a; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">1. Identificación y Datos Clínicos</h3>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 14px;">
                    <div style="grid-column: span 2;"><span style="color: #64748b; font-weight: 500;">Nombre Completo del Niño(a):</span> <br><strong style="color: #0f172a; font-size: 16px;">{child_data.get('nombre', '-')}</strong></div>
                    <div><span style="color: #64748b; font-weight: 500;">RUN / Identificación:</span> <br><strong style="color: #0f172a;">{child_data.get('rut', '-')}</strong></div>
                    <div><span style="color: #64748b; font-weight: 500;">Fecha de Nacimiento:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('nacimiento', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Sexo:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('sexo', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Peso al Nacer:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('peso_nacer', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Vacunas al Día:</span> <br><span style="color: #334155; font-weight: 600;">{child_data.get('vacunas', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Último Control Médico:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('control', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Fecha Ingreso Programa:</span> <br><span style="color: #16a34a; font-weight: bold;">{f_ingreso_pdf}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Fecha Estimada Egreso:</span> <br><span style="color: #dc2626; font-weight: bold;">{f_egreso_pdf}</span></div>
                </div>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 25px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #3b82f6; padding-bottom: 6px;">
                    <span style="font-size: 18px; margin-right: 8px;">🏠</span>
                    <h3 style="margin: 0; color: #1e3a8a; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">2. Contexto Familiar (Descripción Profunda)</h3>
                </div>
                
                <div style="font-size: 14px; display: flex; flex-direction: column; gap: 14px;">
                    <div style="border-bottom: 1px dashed #e2e8f0; padding-bottom: 8px;">
                        <span style="color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">Madre (Antecedentes, Escolaridad y Ocupación):</span> <br>
                        <span style="color: #1e293b; font-size: 14px; line-height: 1.5; display: block; margin-top: 2px;">{child_data.get('madre', '-')}</span>
                    </div>
                    <div style="border-bottom: 1px dashed #e2e8f0; padding-bottom: 8px;">
                        <span style="color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">Padre (Antecedentes, Escolaridad y Ocupación):</span> <br>
                        <span style="color: #1e293b; font-size: 14px; line-height: 1.5; display: block; margin-top: 2px;">{child_data.get('padre', '-')}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div><span style="color: #64748b; font-weight: 500;">Teléfono de Contacto:</span> <br><strong style="color: #334155;">{child_data.get('telefono_madre', '-')}</strong></div>
                        <div><span style="color: #64748b; font-weight: 500;">Dirección Particular:</span> <br><span style="color: #334155;">{child_data.get('direccion', '-')}</span></div>
                    </div>
                    <div style="background: #fff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px;">
                        <span style="color: #64748b; font-weight: 500;">Suplentes Autorizados para Retiro:</span> <br>
                        <span style="color: #475569; font-weight: 500;">{child_data.get('suplentes', '-')}</span>
                    </div>
                </div>
            </div>

            <div style="margin-bottom: 40px;">
                <div style="display: flex; align-items: center; margin-bottom: 12px; border-bottom: 2px solid #10b981; padding-bottom: 6px;">
                    <span style="font-size: 18px; margin-right: 8px;">📝</span>
                    <h3 style="margin: 0; color: #065f46; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">3. Historia Social y Antecedentes</h3>
                </div>
                <div style="background: #f0fdf4; border-left: 5px solid #10b981; padding: 20px; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{child_data.get('historia_social', 'No se registran antecedentes adicionales.')}</div>
            </div>

            <div style="margin-top: 70px; display: flex; justify-content: space-between; padding: 0 20px;">
                <div style="width: 42%; text-align: center; border-top: 1.5px dashed #cbd5e1; padding-top: 10px; font-size: 12px; color: #64748b;">
                    <br><strong style="color: #334155;">Firma Asistente Social</strong>
                </div>
                <div style="width: 42%; text-align: center; border-top: 1.5px dashed #cbd5e1; padding-top: 10px; font-size: 12px; color: #64748b;">
                    <br><strong style="color: #334155;">Validación Interna</strong>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script>
        window.onload = function() {{
            var element = document.getElementById('pdf-container');
            var opt = {{
                margin:       [8, 4, 8, 4],
                filename:     'Ficha_GotaDeLeche_{child_data.get('ficha', '_')}.pdf',
                image:        {{ type: 'jpeg', quality: 0.98 }},
                html2canvas:  {{ scale: 2, useCORS: true, logging: false }},
                jsPDF:        {{ unit: 'mm', format: 'letter', orientation: 'portrait' }}
            }};
            html2pdf().set(opt).from(element).save();
        }}
    </script>
    """
    components.html(html_content, height=0, width=0)

# ─────────────────────────────────────────
# 3. CONEXIÓN A BASE DE DATOS
# ─────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError as e:
        st.error(f"Configuración incompleta: falta la credencial {e}. Revise los Secrets.")
        st.stop()
    except Exception as e:
        st.error("No fue posible establecer conexión con la base de datos. Intente más tarde.")
        st.stop()

supabase = init_supabase()

# ─────────────────────────────────────────
# 4. LOGIN MEJORADO (CON LOGO INTEGRADO EN MODO OSCURO)
# ─────────────────────────────────────────
if "user" not in st.session_state:
    st.markdown("<style>section[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 0.8, 1])
    with col_mid:
        st.markdown('<div class="centered-login">', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 16px;">
                <img src="{LOGO_SRC}" style="
                    height: 180px; 
                    object-fit: contain; 
                    mix-blend-mode: screen; 
                    filter: brightness(1.4) drop-shadow(0px 6px 18px rgba(96, 165, 250, 0.5));
                ">
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h1 style='color:#e2e8f0; font-size:2rem; margin-bottom:2px; font-weight:800; letter-spacing:-0.01em; text-align:center;'>GOTAS DE LECHE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#475569; font-size:0.8rem; margin-bottom:28px; letter-spacing:0.12em; text-transform:uppercase; font-weight:600; text-align:center;'>Sistema Maestro de Gestión</p>", unsafe_allow_html=True)
        
        with st.form("login"):
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            if st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True):
                if not username or not password:
                    st.error("Por favor complete usuario y contraseña.")
                else:
                    try:
                        res = supabase.table("usuarios").select("*").eq("usuario", username).execute()
                        if res.data and verify_password(password, res.data[0]["clave"]):
                            st.session_state.user = res.data[0]
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos. Intente nuevamente.")
                    except Exception as e:
                        st.error("No fue posible conectar con el servidor. Intente más tarde.")
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 5. PANEL PRINCIPAL (SESIÓN ACTIVA)
# ─────────────────────────────────────────
else:
    user = st.session_state.user
    MAX_FICHAS = 210

    if "menu_choice" not in st.session_state:
        st.session_state.menu_choice = "📊  DASHBOARD"

    with st.sidebar:
        # ── Header del sidebar ──
        st.markdown(f"""
            <div class="sidebar-header">
                <div style="text-align:center;">
                    <img src="{LOGO_SRC}" style="height:72px; object-fit:contain; mix-blend-mode:screen; filter:brightness(1.35);">
                </div>
                <div style="text-align:center; margin-top:12px;">
                    <div class="sidebar-user-name">{user['nombre']}</div>
                    <div class="sidebar-user-role">Operador Autorizado</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='padding: 6px 0 4px 0;'>", unsafe_allow_html=True)

        # ── Navegación con radio estilizado ──
        menu_choice_selected = st.radio(
            "nav",
            ["📊  DASHBOARD", "📦  BODEGA CENTRAL", "⚖️  SALA DE ATENCIÓN", "👥  GESTIÓN DE NIÑOS", "📜  HISTORIAL"],
            label_visibility="collapsed",
            key="menu_radio"
        )
        st.session_state.menu_choice = menu_choice_selected

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Separador ──
        st.markdown("<div style='height:1px; background:rgba(255,255,255,0.06); margin: 8px 0 12px 0;'></div>", unsafe_allow_html=True)

        # ── Cerrar sesión ──
        st.markdown("<div class='sidebar-logout'>", unsafe_allow_html=True)
        if st.button("🚪  CERRAR SESIÓN", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Timestamp en el fondo ──
        st.markdown(f"""
            <div style="padding: 16px 20px; color: #334155; font-size: 0.72rem; font-weight:500; letter-spacing:0.04em;">
                {datetime.now(CHILE_TZ).strftime("%d/%m/%Y  %H:%M")} — Chile
            </div>
        """, unsafe_allow_html=True)

    menu_choice = st.session_state.get("menu_radio", "📊  DASHBOARD")

    # ── Helper: page header unificado ──
    def render_page_header(title: str, subtitle: str, badge: str = ""):
        fecha_hoy = datetime.now(CHILE_TZ).strftime("%d/%m/%Y")
        nombre_usuario = user['nombre']
        st.markdown(
            f'<div class="page-header">'
            f'<div class="page-header-left"><h2>{title}</h2><p>{subtitle}</p></div>'
            f'<div class="page-header-right">{fecha_hoy}<br><span style="color:#475569;">{nombre_usuario}</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # 📊 PANEL: DASHBOARD
    if menu_choice == "📊  DASHBOARD":
        render_page_header("Dashboard", "Resumen operacional en tiempo real", "SISTEMA ACTIVO")
        try:
            with st.spinner("Cargando métricas..."):
                stock_res = supabase.table("stock").select("*").order("producto").execute()
                benef_res = supabase.table("beneficiarios").select("rut", count="exact").eq("estado", "Activo").execute()
        except Exception as e:
            st.error("No fue posible cargar los datos. Verifique la conexión."); st.stop()
            
        if stock_res.data:
            df = pd.DataFrame(stock_res.data)
            niños_activos = benef_res.count if benef_res.count else 0
            fichas_disponibles = max(0, MAX_FICHAS - niños_activos)
            pct_ocupacion = int((niños_activos / MAX_FICHAS) * 100)
            color_ocupacion = "#ef4444" if pct_ocupacion >= 90 else "#f59e0b" if pct_ocupacion >= 70 else "#3b82f6"

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                    <div class="kpi-card" style="--accent: linear-gradient(90deg,{color_ocupacion},{color_ocupacion}88);">
                        <div class="kpi-label">Niños Activos</div>
                        <div class="kpi-value" style="color:{color_ocupacion};">{niños_activos}</div>
                        <div class="kpi-sub">de {MAX_FICHAS} fichas totales</div>
                        <div class="kpi-progress-bar">
                            <div class="kpi-progress-fill" style="width:{pct_ocupacion}%; background:{color_ocupacion};"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                    <div class="kpi-card" style="--accent: linear-gradient(90deg,#10b981,#059669);">
                        <div class="kpi-label">Fichas Disponibles</div>
                        <div class="kpi-value" style="color:#34d399;">{fichas_disponibles}</div>
                        <div class="kpi-sub">{100 - pct_ocupacion}% de capacidad libre</div>
                    </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                    <div class="kpi-card" style="--accent: linear-gradient(90deg,#6366f1,#8b5cf6);">
                        <div class="kpi-label">Total en Sala</div>
                        <div class="kpi-value" style="color:#a78bfa;">{int(df["sala"].sum())}</div>
                        <div class="kpi-sub">unidades disponibles</div>
                    </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                    <div class="kpi-card" style="--accent: linear-gradient(90deg,#0ea5e9,#38bdf8);">
                        <div class="kpi-label">Bodega Central</div>
                        <div class="kpi-value" style="color:#38bdf8;">{int(df["bodega"].sum())}</div>
                        <div class="kpi-sub">unidades almacenadas</div>
                    </div>
                """, unsafe_allow_html=True)
            
            productos_filtrados = [item for item in stock_res.data if item["producto"].upper() not in ["AJUAR", "OTROS"]]
            
            st.markdown('<div class="section-title">🏢 Stock de Bodega Central</div>', unsafe_allow_html=True)
            cols_bodega = st.columns(3)
            for i, item in enumerate(productos_filtrados):
                with cols_bodega[i % 3]:
                    if item["bodega"] <= 15:
                        color_valor = "#f87171"
                        badge = '<span class="status-badge status-crit">🚨 Crítico</span>'
                    elif item["bodega"] <= 40:
                        color_valor = "#fbbf24"
                        badge = '<span class="status-badge status-warn">⚠️ Bajo</span>'
                    else:
                        color_valor = "#60a5fa"
                        badge = '<span class="status-badge status-ok">✓ Estable</span>'
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{item['producto']}</div>
                            <div class="metric-value" style="color:{color_valor};">
                                {int(item['bodega'])} <span style="font-size:1rem; color:#475569; font-weight:500;">ud</span>
                            </div>
                            {badge}
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown('<div class="section-title">⚖️ Insumos en Sala de Atención</div>', unsafe_allow_html=True)
            cols_sala = st.columns(3)
            for i, item in enumerate(productos_filtrados):
                with cols_sala[i % 3]:
                    if item["sala"] <= 5:
                        color_valor = "#f87171"
                        badge = '<span class="status-badge status-crit">🚨 Crítico</span>'
                    elif item["sala"] <= 15:
                        color_valor = "#fbbf24"
                        badge = '<span class="status-badge status-warn">⚠️ Bajo</span>'
                    else:
                        color_valor = "#34d399"
                        badge = '<span class="status-badge status-ok">✓ Estable</span>'
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{item['producto']}</div>
                            <div class="metric-value" style="color:{color_valor};">
                                {int(item['sala'])} <span style="font-size:1rem; color:#475569; font-weight:500;">ud</span>
                            </div>
                            {badge}
                        </div>
                    """, unsafe_allow_html=True)

    # 📦 PANEL: BODEGA CENTRAL
    elif menu_choice == "📦  BODEGA CENTRAL":
        render_page_header("Bodega Central", "Gestión e inventario general de insumos")
        try:
            raw = supabase.table("stock").select("*").order("id").execute().data
        except Exception as e:
            st.error("No fue posible recuperar el stock. Verifique la conexión."); st.stop()
            
        df_inventory = pd.DataFrame(raw)
        st.markdown('<div class="section-title">📋 Niveles Actuales de Existencias</div>', unsafe_allow_html=True)
        st.dataframe(
            df_inventory[["producto", "bodega", "sala"]], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "producto": "Descripción de Insumo",
                "bodega": st.column_config.NumberColumn("Cantidad en Bodega Principal", format="%d Unidades 🏢"),
                "sala": st.column_config.NumberColumn("Cantidad en Sala de Peso", format="%d Unidades ⚖️")
            }
        )
        
        st.write("###")
        with st.expander("🔄 EJECUTAR MOVIMIENTO INTERNO DE STOCK", expanded=True):
            with st.form("mov_form"):
                c1, c2, c3 = st.columns([1.5, 1, 1.5])
                with c1:
                    product_name = st.selectbox("Seleccione Insumo / Alimento", df_inventory["producto"].tolist())
                with c2:
                    quantity = st.number_input("Cantidad de Unidades", min_value=1, step=1)
                with c3:
                    movement_type = st.radio("Acción a realizar", ["Ingreso a Bodega", "Traslado a Sala"], horizontal=True)
                
                if st.form_submit_button("PROCESAR OPERACIÓN", type="primary", use_container_width=True):
                    row = df_inventory[df_inventory["producto"] == product_name].iloc[0]
                    if movement_type == "Traslado a Sala" and row["bodega"] < quantity:
                        st.error(f"⚠️ Stock insuficiente en bodega principal. Disponibles únicamente {row['bodega']} unidades.")
                    else:
                        try:
                            cant_operacion = int(quantity)
                            bodega_actual = int(row["bodega"])
                            sala_actual = int(row["sala"])
                            id_registro = int(row["id"])

                            if movement_type == "Ingreso a Bodega":
                                supabase.table("stock").update({"bodega": bodega_actual + cant_operacion}).eq("id", id_registro).execute()
                            else:
                                supabase.table("stock").update({
                                    "bodega": bodega_actual - cant_operacion,
                                    "sala": sala_actual + cant_operacion,
                                }).eq("id", id_registro).execute()
                                
                            supabase.table("historial").insert({
                                "responsable": user["nombre"], "producto": product_name,
                                "cantidad": cant_operacion, "tipo": movement_type.upper(), "created_at": get_local_now(),
                            }).execute()
                            
                            st.toast("✅ Inventario actualizado correctamente.", icon="📥")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error("Error al procesar el movimiento. Intente nuevamente.")

    # ⚖️ PANEL: SALA DE ATENCIÓN
    elif menu_choice == "⚖️  SALA DE ATENCIÓN":
        render_page_header("Sala de Atención", "Despacho y control de insumos")
        
        tab_entrega, tab_resumen_stock = st.tabs(["📝 CONTROL DE ENTREGA (REGISTRAR)", "📊 RESUMEN DE INGRESOS Y SALIDAS"])
        
        try:
            stock_data = supabase.table("stock").select("*").order("producto").execute().data
        except Exception as e:
            st.error("Error de stock. Verifique la conexión."); st.stop()
            
        with tab_entrega:
            metodo_busqueda = st.radio("Buscar beneficiario por:", ["N° de Ficha 📋", "RUN / Identificación 🪪"], horizontal=True)
            
            recipient_name = ""
            ficha_vinculada = 0
            opciones_retiro = ["--"]
            beneficiary = None
            
            if metodo_busqueda == "N° de Ficha 📋":
                ficha_number = st.number_input("🔍 Escanear o Digitar N° de Ficha", min_value=0, step=1, key="input_ficha_entrega")
                if ficha_number > 0:
                    try:
                        res = supabase.table("beneficiarios").select("*").eq("ficha", ficha_number).eq("estado", "Activo").execute()
                        if res.data:
                            beneficiary = res.data[0]
                        else:
                            st.warning("No se localizó ningún beneficiario activo bajo este número de ficha.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                rut_input = st.text_input("🔍 Escanear o Ingresar RUN / Identificación", placeholder="Ej: 12345678-9", key="input_rut_entrega").strip()
                if rut_input:
                    try:
                        res = supabase.table("beneficiarios").select("*").eq("rut", rut_input).eq("estado", "Activo").execute()
                        if res.data:
                            beneficiary = res.data[0]
                        else:
                            st.warning("No se localizó ningún beneficiario activo con el RUN ingresado.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            if beneficiary:
                recipient_name = beneficiary["nombre"]
                ficha_vinculada = beneficiary["ficha"]
                
                opciones_retiro = []
                if beneficiary.get("madre"): opciones_retiro.append(f"Madre: {beneficiary['madre'][:40]}...")
                if beneficiary.get("padre"): opciones_retiro.append(f"Padre: {beneficiary['padre'][:40]}...")
                if beneficiary.get("suplentes"): opciones_retiro.append(f"Suplentes: {beneficiary['suplentes']}")
                opciones_retiro.append("Otro Suplente (No registrado)")
                
                st.success(f"**Beneficiario:** {recipient_name} | **Ficha:** {ficha_vinculada} | **Último Control:** {beneficiary.get('control','-')}", icon="👶")

            st.write("###")
            product_options = ["--"] + [x["producto"] for x in stock_data if x["producto"].upper() not in ["AJUAR", "OTROS"]]
            
            with st.form("delivery_master_form"):
                st.markdown("##### 📦 Desglose Obligatorio de Insumos (Se deben registrar exactamente 3 ítems)")
                
                col_p1, col_q1 = st.columns([3, 1])
                with col_p1: prod_1 = st.selectbox("Insumo 1", product_options, key="p1")
                with col_q1: qty_1 = st.number_input("Cant 1", min_value=0, step=1, key="q1")
                
                col_p2, col_q2 = st.columns([3, 1])
                with col_p2: prod_2 = st.selectbox("Insumo 2", product_options, key="p2")
                with col_q2: qty_2 = st.number_input("Cant 2", min_value=0, step=1, key="q2")
                
                col_p3, col_q3 = st.columns([3, 1])
                with col_p3: prod_3 = st.selectbox("Insumo 3", product_options, key="p3")
                with col_q3: qty_3 = st.number_input("Cant 3", min_value=0, step=1, key="q3")
                
                st.divider()
                st.markdown("##### 👤 Control de Retiro Autorizado")
                quien_retira_tipo = st.selectbox("Persona que retira de la ficha:", opciones_retiro)
                nombre_firma_especifico = st.text_input("Nombre completo de quien recibe físicamente (Firma digital):", placeholder="Escriba el nombre de la persona que se lleva los insumos")
                
                if st.form_submit_button("🔥 CONVALIDAR Y REGISTRAR ENTREGA", type="primary", use_container_width=True):
                    items_validados = [(prod_1, qty_1), (prod_2, qty_2), (prod_3, qty_3)]
                    any_empty = any(p == "--" or q <= 0 for p, q in items_validados)
                    
                    if ficha_vinculada == 0:
                        st.error("Operación abortada: Debe identificar primero a un beneficiario activo mediante Ficha o RUN.")
                    elif any_empty:
                        st.error("❌ ERROR DE CAMPO OBLIGATORIO: Las voluntarias deben registrar obligatoriamente los 3 ítems de insumos con cantidades mayores a cero.")
                    elif not nombre_firma_especifico:
                        st.error("❌ ERROR DE CAMPO OBLIGATORIO: Debe ingresar el nombre completo de la persona que recibe físicamente.")
                    else:
                        errors_stock = []
                        for p_name, qty in items_validados:
                            item = next((x for x in stock_data if x["producto"] == p_name), None)
                            if not item:
                                errors_stock.append(f"El producto '{p_name}' no existe.")
                            elif item["sala"] < qty:
                                errors_stock.append(f"Falta Stock para '{p_name}'. En sala: {item['sala']} | Solicitado: {qty}.")
                                
                        if errors_stock:
                            for err in errors_stock: st.error(err)
                        else:
                            try:
                                detalle_receptor = f"{quien_retira_tipo} (Recibe: {nombre_firma_especifico})"
                                for p_name, qty in items_validados:
                                    item = next(x for x in stock_data if x["producto"] == p_name)
                                    supabase.table("stock").update({"sala": int(item["sala"] - qty)}).eq("id", int(item["id"])).execute()
                                    
                                    supabase.table("historial").insert({
                                        "responsable": user["nombre"], "producto": p_name, "cantidad": int(qty),
                                        "tipo": "ENTREGA", "observaciones": f"Ficha {ficha_vinculada} - {detalle_receptor}", "created_at": get_local_now(),
                                    }).execute()
                                    
                                st.balloons()
                                st.toast("Entrega asentada de manera exitosa en Sala de Atención.", icon="🎉")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error("Error al guardar la entrega. Intente nuevamente.")
                                
        with tab_resumen_stock:
            st.markdown("### 📊 Resumen Estadístico de Cargas en Sala de Atención")
            
            try:
                historial_completo = supabase.table("historial").select("*").execute().data
                df_h = pd.DataFrame(historial_completo) if historial_completo else pd.DataFrame()
            except:
                df_h = pd.DataFrame()
                
            if df_h.empty:
                st.info("No hay transacciones registradas.")
            else:
                resumen_productos = []
                for p in stock_data:
                    p_name = p["producto"]
                    if p_name.upper() in ["AJUAR", "OTROS"]: continue
                    
                    entradas = df_h[(df_h["producto"] == p_name) & (df_h["tipo"] == "TRASLADO A SALA")]["cantidad"].astype(int).sum()
                    salidas = df_h[(df_h["producto"] == p_name) & (df_h["tipo"] == "ENTREGA")]["cantidad"].astype(int).sum()
                    
                    resumen_productos.append({
                        "Insumo / Alimento": p_name,
                        "Total Recibido (Cargado) 📥": entradas,
                        "Total Entregado (Despachado) 📤": salidas,
                        "Stock Disponible Neto ⚖️": p["sala"]
                    })
                    
                st.dataframe(pd.DataFrame(resumen_productos), use_container_width=True, hide_index=True)

    # 👥 PANEL: GESTIÓN DE NIÑOS
    elif menu_choice == "👥  GESTIÓN DE NIÑOS":
        render_page_header("Padrón de Beneficiarios", "Gestión de fichas clínicas activas e historial de egresos")
        tab_active, tab_inactive = st.tabs(["🟢 NIÑOS ACTIVOS", "⚪ HISTORIAL DE EGRESOS"])
        
        try:
            todo_el_historial = supabase.table("historial").select("*").eq("tipo", "ENTREGA").execute().data
            df_entregas_global = pd.DataFrame(todo_el_historial) if todo_el_historial else pd.DataFrame()
            if not df_entregas_global.empty:
                df_entregas_global["created_at"] = pd.to_datetime(df_entregas_global["created_at"], errors="coerce")
                try:
                    df_entregas_global["created_at"] = df_entregas_global["created_at"].dt.tz_convert("America/Santiago")
                except:
                    df_entregas_global["created_at"] = df_entregas_global["created_at"].dt.tz_localize("UTC").dt.tz_convert("America/Santiago")
        except:
            df_entregas_global = pd.DataFrame()

        if "pdf_trigger" in st.session_state and st.session_state.pdf_trigger is not None:
            export_pdf_component(st.session_state.pdf_trigger)
            st.session_state.pdf_trigger = None

        with tab_active:
            try:
                res_max = supabase.table("beneficiarios").select("ficha").order("ficha", desc=True).limit(1).execute()
                siguiente_ficha = (res_max.data[0]['ficha'] + 1) if res_max.data else 1
            except:
                siguiente_ficha = 1
                
            with st.expander("➕ INSCRIBIR NUEVO BENEFICIARIO (MÁXIMO 210 FICHAS)", expanded=False):
                with st.form("new_child_form"):
                    c1, c2, c3 = st.columns([2, 1.5, 1])
                    name = c1.text_input("Nombre Completo del Niño(a) *")
                    rut = c2.text_input("RUN / Identificación *")
                    ficha = c3.number_input("N° Ficha Asignado", min_value=1, value=siguiente_ficha, step=1)
                    
                    cc1, cc2, cc3 = st.columns(3)
                    birth_date = cc1.text_input("Fecha Nacimiento (DD/MM/AAAA)")
                    sexo = cc2.selectbox("Sexo", ["Masculino", "Femenino"])
                    peso_nacer = cc3.text_input("Peso al Nacer (ej: 3.935 kg)")
                    
                    cx1, cx2 = st.columns(2)
                    vacunas = cx1.selectbox("¿Vacunas al Día?", ["Sí", "No"])
                    ultimo_control = cx2.text_input("Último Control Médico (ej: 30.03.26 / 3.820 kg)")
                    
                    st.markdown("---")
                    st.markdown("##### 👥 Registro de Núcleo Familiar (Fila completa para descripción profunda)")
                    mother = st.text_area("Madre (Nombre, Nacionalidad, Estado Civil, Edad, Escolaridad, Ocupación)", placeholder="Ej: María Bernardita Tapia Cáceres, Chilena, soltera, 27 años...")
                    father = st.text_area("Padre (Nombre, Nacionalidad, Estado Civil, Edad, Escolaridad, Ocupación)", placeholder="Ej: Jimmy Franco Saavedra Soto, Chileno, soltero, 33 años...")
                    
                    st.markdown("##### 📞 Contacto y Dirección")
                    ccc1, ccc2 = st.columns(2)
                    phone = ccc1.text_input("Teléfono de Contacto")
                    address = ccc2.text_input("Dirección Particular")
                    
                    st.markdown("##### 🛡️ Suplentes Autorizados para Retiro")
                    u_suplentes_new = st.text_input("Nombres de Suplentes Autorizados", placeholder="Ej: Harely Tapia Cáceres - Tía")
                    
                    social_history = st.text_area("Antecedentes Importantes / Historia Social")
                    
                    if st.form_submit_button("INGRESAR BENEFICIARIO AL SISTEMA", type="primary"):
                        if not name or not rut:
                            st.error("Campos obligatorios faltantes: Nombre y RUN son requeridos.")
                        else:
                            try:
                                f_ingreso_dt = datetime.now(CHILE_TZ)
                                f_egreso_dt = f_ingreso_dt + timedelta(days=730)
                                
                                string_ingreso = f_ingreso_dt.strftime("%d/%m/%Y")
                                string_egreso = f_egreso_dt.strftime("%d/%m/%Y")
                                
                                check_ficha = supabase.table("beneficiarios").select("ficha, nombre").eq("ficha", ficha).execute()
                                if check_ficha.data:
                                    st.error(f"Conflicto: El N° de ficha {ficha} ya está asignado a: {check_ficha.data[0]['nombre']}")
                                else:
                                    supabase.table("beneficiarios").insert({
                                        "nombre": name, "rut": rut, "ficha": ficha, "nacimiento": birth_date,
                                        "sexo": sexo, "peso_nacer": peso_nacer, "vacunas": vacunas, "control": ultimo_control,
                                        "telefono_madre": phone, "direccion": address, "madre": mother, "padre": father,
                                        "suplentes": u_suplentes_new,
                                        "historia_social": social_history, "estado": "Activo",
                                        "fecha_ingreso": string_ingreso, "fecha_egreso": string_egreso
                                    }).execute()
                                    st.success("Registro clínico-social creado exitosamente.")
                                    time.sleep(0.5)
                                    st.rerun()
                            except Exception as e:
                                st.error("Error al inscribir el beneficiario. Intente nuevamente.")
                                
            try:
                children = supabase.table("beneficiarios").select("*").eq("estado", "Activo").order("ficha").execute().data
            except Exception as e:
                st.error("Error al cargar el padrón de beneficiarios."); st.stop()
                
            st.markdown('<div class="section-title">📋 Fichas Clínicas en Sistema</div>', unsafe_allow_html=True)
            for child in children:
                with st.expander(f"📋 Ficha {child['ficha']} — {child['nombre']} ({child.get('sexo','-')})"):
                    
                    btn_col1, btn_col2, btn_col3, _ = st.columns([1.5, 1.5, 1.5, 2.5])
                    with btn_col1:
                        if st.button(f"📄 Descargar Ficha PDF", key=f"pdf_{child['ficha']}", use_container_width=True):
                            st.session_state.pdf_trigger = child
                            st.rerun()
                    with btn_col2:
                        edit_key = f"edit_mode_{child['ficha']}"
                        if edit_key not in st.session_state:
                            st.session_state[edit_key] = False
                            
                        if st.button(f"✏️ Editar Datos", key=f"btn_edit_{child['ficha']}", use_container_width=True):
                            st.session_state[edit_key] = not st.session_state[edit_key]
                            st.rerun()
                    with btn_col3:
                        if st.button(f"❌ Registrar Egreso", key=f"egresar_{child['ficha']}", type="secondary", use_container_width=True):
                            try:
                                supabase.table("beneficiarios").update({"estado": "Egresado"}).eq("ficha", child["ficha"]).execute()
                                supabase.table("historial").insert({
                                    "responsable": user["nombre"], "producto": "PADRÓN", "cantidad": 1,
                                    "tipo": "EGRESO", "observaciones": f"Ficha {child['ficha']} dada de baja", "created_at": get_local_now(),
                                }).execute()
                                st.toast(f"✅ Ficha {child['ficha']} marcada como Egresada.", icon="💼")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error("Error al registrar el egreso. Intente nuevamente.")
                    st.write("---")
                    
                    if st.session_state[edit_key]:
                        st.markdown("##### ✏️ Modificar Datos del Beneficiario")
                        with st.form(key=f"form_edit_data_{child['ficha']}"):
                            ec1, ec2, ec3 = st.columns([2, 1.5, 1])
                            u_name = ec1.text_input("Nombre Completo *", value=child["nombre"])
                            u_rut = ec2.text_input("RUN / Identificación *", value=child["rut"])
                            u_ficha = ec3.number_input("N° Ficha (Lectura)", value=int(child["ficha"]), disabled=True)
                            
                            ecc1, ecc2, ecc3 = st.columns(3)
                            u_birth = ecc1.text_input("Fecha Nacimiento", value=child.get("nacimiento", ""))
                            u_sexo = ecc2.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if child.get("sexo") == "Masculino" else 1)
                            u_peso = ecc3.text_input("Peso al Nacer", value=child.get("peso_nacer", ""))
                            
                            ecx1, ecx2 = st.columns(2)
                            u_vacunas = ecx1.selectbox("¿Vacunas al Día?", ["Sí", "No"], index=0 if child.get("vacunas") == "Sí" else 1)
                            u_control = ecx2.text_input("Último Control Médico", value=child.get("control", ""))
                            
                            st.markdown("##### 👥 Contexto Familiar (Edición Ampliada)")
                            u_mother = st.text_area("Madre (Descripción profunda)", value=child.get("madre", ""))
                            u_father = st.text_area("Padre (Descripción profunda)", value=child.get("padre", ""))
                            
                            st.markdown("##### 📞 Contacto y Dirección")
                            eccc2, eccc3 = st.columns(2)
                            u_phone = eccc2.text_input("Teléfono", value=child.get("telefono_madre", ""))
                            u_address = eccc3.text_input("Dirección Particular", value=child.get("direccion", ""))
                            
                            u_suplentes_edit = st.text_input("Suplentes Autorizados", value=child.get("suplentes", ""))
                            u_social = st.text_area("Antecedentes / Historia Social", value=child.get("historia_social", ""))
                            
                            if st.form_submit_button("💾 GUARDAR CAMBIOS", type="primary", use_container_width=True):
                                if not u_name or not u_rut:
                                    st.error("Nombre y RUN no pueden quedar vacíos.")
                                else:
                                    try:
                                        supabase.table("beneficiarios").update({
                                            "nombre": u_name, "rut": u_rut, "nacimiento": u_birth,
                                            "sexo": u_sexo, "peso_nacer": u_peso, "vacunas": u_vacunas,
                                            "control": u_control, "madre": u_mother, "padre": u_father,
                                            "telefono_madre": u_phone, "direccion": u_address,
                                            "suplentes": u_suplentes_edit,
                                            "historia_social": u_social
                                        }).eq("ficha", child["ficha"]).execute()
                                        
                                        supabase.table("historial").insert({
                                            "responsable": user["nombre"], "producto": "PADRÓN", "cantidad": 1,
                                            "tipo": "EDICIÓN", "observaciones": f"Ficha {child['ficha']} corregida por digitación", "created_at": get_local_now(),
                                        }).execute()
                                        
                                        st.session_state[edit_key] = False
                                        st.toast("✅ Ficha actualizada de manera exitosa.", icon="💾")
                                        time.sleep(0.5)
                                        st.rerun()
                                    except Exception as e:
                                        st.error("Error al actualizar la ficha. Intente nuevamente.")
                    else:
                        fecha_ingreso_clean = clean_timestamp_to_date(child.get('fecha_ingreso', '-'))
                        fecha_egreso_clean = clean_timestamp_to_date(child.get('fecha_egreso', '-'))

                        sub_c1, sub_c2 = st.columns(2)
                        with sub_c1:
                            st.markdown(f"**RUN:** `{child['rut']}`")
                            st.markdown(f"**Fecha Nacimiento:** {child.get('nacimiento', '-')}")
                            st.markdown(f"**Peso al Nacer:** {child.get('peso_nacer', '-')}")
                            st.markdown(f"**Vacunas al Día:** `{child.get('vacunas', '-')}`")
                            st.markdown(f"**Último Control Médico:** {child.get('control', '-')}")
                        with sub_c2:
                            st.markdown(f"**Fecha Ingreso:** `{fecha_ingreso_clean}`")
                            st.markdown(f"**Egreso Estimado:** `{fecha_egreso_clean}`")
                            st.markdown(f"**Teléfono:** `{child.get('telefono_madre', '-')}`")
                            st.markdown(f"**Dirección:** {child.get('direccion', '-')}")
                            st.markdown(f"**Suplentes Autorizados:** {child.get('suplentes', '-')}")
                        
                        st.write("###")
                        st.markdown('<div class="ficha-seccion-datos">', unsafe_allow_html=True)
                        st.markdown(f"👩 **DATOS DE LA MADRE:** \n{child.get('madre', '-')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="ficha-seccion-datos">', unsafe_allow_html=True)
                        st.markdown(f"👨 **DATOS DEL PADRE:** \n{child.get('padre', '-')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.write("###")
                        st.markdown("##### 📝 ANTECEDENTES GENERALES E HISTORIA SOCIAL")
                        historia = child.get('historia_social')
                        if historia: st.info(historia)
                        else: st.caption("No se registran antecedentes sociales.")
                    
                    st.write("###")
                    st.markdown("##### 📦 HISTORIAL DE ENTREGAS RECIBIDAS")
                    if not df_entregas_global.empty:
                        string_busqueda = f"Ficha {child['ficha']} "
                        df_niño = df_entregas_global[df_entregas_global["observaciones"].astype(str).str.contains(string_busqueda, na=False)].copy()
                        
                        if not df_niño.empty:
                            df_niño["Fecha/Hora"] = df_niño["created_at"].dt.strftime("%d/%m/%Y %H:%M")
                            df_niño_render = df_niño[["Fecha/Hora", "producto", "cantidad", "responsable", "observaciones"]].rename(
                                columns={"producto": "Producto", "cantidad": "Cant.", "responsable": "Entregó", "observaciones": "Detalle Retiro"}
                            )
                            st.dataframe(df_niño_render, use_container_width=True, hide_index=True)
                        else:
                            st.info("No se registran entregas históricas.")
                    else:
                        st.info("No se registran entregas históricas.")

        with tab_inactive:
            st.markdown('<div class="section-title">⚪ Historial de Egresos Pasivos</div>', unsafe_allow_html=True)
            try:
                egresados = supabase.table("beneficiarios").select("*").eq("estado", "Egresado").order("ficha").execute().data
            except Exception as e:
                st.error("No fue posible cargar el historial de egresados."); st.stop()
                
            if not egresados:
                st.info("No se registran egresados.")
            else:
                for inactive_child in egresados:
                    with st.expander(f"⚪ Ficha {inactive_child['ficha']} — {inactive_child['nombre']} (EGRESADO)"):
                        if st.button(f"🟢 Re-incorporar", key=f"reactivar_{inactive_child['ficha']}", type="primary"):
                            try:
                                supabase.table("beneficiarios").update({"estado": "Activo"}).eq("ficha", inactive_child["ficha"]).execute()
                                supabase.table("historial").insert({
                                    "responsable": user["nombre"], "producto": "PADRÓN", "cantidad": 1,
                                    "tipo": "REINGRESO", "observaciones": f"Ficha {inactive_child['ficha']} re-incorporada", "created_at": get_local_now(),
                                }).execute()
                                st.toast(f"✅ Ficha {inactive_child['ficha']} re-activada.", icon="🟢")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error("Error al re-incorporar el beneficiario. Intente nuevamente.")

    # 📜 PANEL: HISTORIAL
    elif menu_choice == "📜  HISTORIAL":
        render_page_header("Historial de Operaciones", "Registro completo de movimientos y transacciones")
        
        st.markdown('<div class="section-title">🔍 Filtros de Búsqueda</div>', unsafe_allow_html=True)
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            fecha_inicio = st.date_input("Fecha Inicial de Búsqueda", value=datetime.now(CHILE_TZ) - timedelta(days=30))
        with c_f2:
            fecha_fin = st.date_input("Fecha Final de Búsqueda", value=datetime.now(CHILE_TZ))
            
        try:
            with st.spinner("Consultando registros..."):
                datos_historial = supabase.table("historial").select("*").order("id", desc=True).execute().data
        except Exception as e:
            st.error("No fue posible cargar el historial. Intente nuevamente."); st.stop()
            
        if not datos_historial:
            st.info("No se registran movimientos históricos.")
        else:
            df_historial_general = pd.DataFrame(datos_historial)
            df_historial_general["created_at_dt"] = pd.to_datetime(df_historial_general["created_at"], errors="coerce")
            
            try:
                df_historial_general["created_at_dt"] = df_historial_general["created_at_dt"].dt.tz_convert("America/Santiago")
            except:
                try:
                    df_historial_general["created_at_dt"] = df_historial_general["created_at_dt"].dt.tz_localize("UTC").dt.tz_convert("America/Santiago")
                except:
                    pass
            
            df_historial_general = df_historial_general[
                (df_historial_general["created_at_dt"].dt.date >= fecha_inicio) & 
                (df_historial_general["created_at_dt"].dt.date <= fecha_fin)
            ]
            
            df_historial_general["Fecha y Hora ⏰"] = df_historial_general["created_at_dt"].dt.strftime("%d/%m/%Y %H:%M")
            
            tipos_disponibles = ["TODOS"] + list(df_historial_general["tipo"].unique()) if not df_historial_general.empty else ["TODOS"]
            
            col_filtro, col_export = st.columns([3, 1])
            with col_filtro:
                filtro_tipo = st.selectbox("Filtrar por tipo de operación:", tipos_disponibles)
            with col_export:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if not df_historial_general.empty:
                    csv_data = df_historial_general[["Fecha y Hora ⏰", "tipo", "producto", "cantidad", "responsable", "observaciones"]].to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="⬇️ Exportar CSV",
                        data=csv_data,
                        file_name=f"historial_gdl_{datetime.now(CHILE_TZ).strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
            
            if filtro_tipo != "TODOS" and not df_historial_general.empty:
                df_filtrado = df_historial_general[df_historial_general["tipo"] == filtro_tipo]
            else:
                df_filtrado = df_historial_general
            
            if df_filtrado.empty:
                st.warning("No se encontraron registros.")
            else:
                df_filtrado["observaciones"] = df_filtrado["observaciones"].fillna("Movimiento interno de stock")
                df_render = df_filtrado[["Fecha y Hora ⏰", "tipo", "producto", "cantidad", "responsable", "observaciones"]].rename(
                    columns={
                        "tipo": "Tipo de Operación ⚙️", "producto": "Insumo / Alimento 🥛",
                        "cantidad": "Cantidad 🔢", "responsable": "Responsable 👤", "observaciones": "Detalle / Observación 📝"
                    }
                )
                st.dataframe(
                    df_render, use_container_width=True, hide_index=True,
                    column_config={"Cantidad 🔢": st.column_config.NumberColumn(format="%d unidades 📦")}
                )
