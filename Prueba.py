import streamlit as st
import pandas as pd
from supabase import create_client, Client
import time
import bcrypt
import pytz
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import io

# ─────────────────────────────────────────
# 0. CONFIGURACIÓN DEL SISTEMA
# ─────────────────────────────────────────
LOGO_SRC = "https://raw.githubusercontent.com/Christian-Infor/Prueba/refs/heads/main/Gotadeleche-removebg-preview.png"
SUPER_ADMIN = "admin" # 👑 COLOCA AQUÍ TU NOMBRE DE USUARIO DE INICIO DE SESIÓN

# ─────────────────────────────────────────
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Gota de Leche - Sistema Maestro",
    layout="wide",
    page_icon=LOGO_SRC, 
)

st.markdown("""
    <style>
    /* ── IMPORTAR FUENTE MODERNA INTER ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body { 
        font-family: 'Inter', sans-serif !important; 
        font-size: 1.1rem !important; 
    }
    
    /* ── CORRECCIÓN URGENTE PARA EL ERROR DE LOS ÍCONOS (_arrow_right_) ── */
    /* Protegemos la fuente original de los iconos para que 'Inter' no los convierta en texto */
    span[class*="material"], i[class*="material"], [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }
    
    /* ── CORRECCIÓN ICONOS EXPANDERS ── */
    details[data-testid="stExpander"] summary::after,
    details[data-testid="stExpander"] summary::before {
        display: none !important;
    }
    
    /* ══════════════════════════════
       FONDO ANIMADO (MOVIMIENTO SUTIL)
    ══════════════════════════════ */
    @keyframes movimientoFondo {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp:not(:has(div[data-testid="stSidebar"])) {
        background: linear-gradient(-45deg, #050C17, #0A1931, #112240, #0a1128) !important;
        background-size: 400% 400% !important;
        animation: movimientoFondo 18s ease infinite !important;
    }
    
    /* Bajar un poco el contenido desde el techo */
    .stApp:not(:has(div[data-testid="stSidebar"])) .stMainBlockContainer {
        padding-top: 6vh !important; 
        max-width: 100% !important;
    }
    
    /* ══════════════════════════════
       ANIMACIONES Y EFECTO CRISTAL (LOGIN)
    ══════════════════════════════ */
    @keyframes entradaLoginCaja {
        0% { opacity: 0; transform: translateY(30px) scale(0.98); }
        100% { opacity: 1; transform: translateY(0px) scale(1); }
    }

    .centered-login {
        max-width: 420px;
        margin: 0 auto;
        text-align: center;
        padding-top: 5vh;
    }

    /* EFECTO GLASSMORPHISM (VIDRIO ESMERILADO) */
    .stForm {
        background: rgba(15, 23, 42, 0.55) !important;
        backdrop-filter: blur(16px) saturate(120%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(120%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        padding: 2rem 2rem 1.6rem 2rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        animation: entradaLoginCaja 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards !important;
    }
    
    /* CAJAS DE TEXTO REACTIVAS */
    .stForm [data-baseweb="input"], .stForm [data-baseweb="textarea"], .stForm [data-baseweb="select"] {
        background-color: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .stForm [data-baseweb="input"]:focus-within, .stForm [data-baseweb="textarea"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.5) !important;
        background-color: rgba(30, 41, 59, 0.7) !important;
    }

    /* ══════════════════════════════
       ANIMACIONES DE BOTONES (PULSO UNIFICADO)
    ══════════════════════════════ */
    @keyframes pulsoLuz {
        0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
        70% { box-shadow: 0 0 0 12px rgba(59, 130, 246, 0); }
        100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }

    button[kind="primary"], 
    .stForm [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        animation: pulsoLuz 2.5s infinite !important;
        border: none !important;
    }
    
    button[kind="primary"]:hover,
    .stForm [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6) !important;
        animation: none !important; 
    }
    
    .stForm [data-testid="stFormSubmitButton"] button {
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.06em !important;
        padding: 0.75rem 1rem !important;
        margin-top: 10px !important;
    }
    
    /* ══════════════════════════════
       TARJETAS 3D PANEL PRINCIPAL
    ══════════════════════════════ */
    @keyframes deslizarArriba {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: deslizarArriba 0.6s ease-out forwards;
    }
    
    .metric-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 12px 25px -5px rgba(56, 189, 248, 0.4);
        border-color: rgba(56, 189, 248, 0.5);
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #38bdf8;
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
        transition: color 0.3s ease;
    }
    
    .metric-card:hover .metric-value {
        color: #ffffff;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.8);
    }

    .ficha-seccion-datos {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }

    /* ══════════════════════════════
       MODERNIZACIÓN DE INTERFAZ (MENÚ Y BOTONES SEGUROS)
    ══════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background-color: #080b13 !important;
        border-right: 1px solid #1e293b !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: rgba(30, 41, 59, 0.4) !important;
        padding: 12px 15px !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
        transform: translateX(4px) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
        background: linear-gradient(90deg, rgba(37,99,235,0.25) 0%, rgba(37,99,235,0.05) 100%) !important;
        border-left: 4px solid #3b82f6 !important;
    }

    @keyframes entradaCascada {
        from { opacity: 0; transform: translateX(-25px); }
        to { opacity: 1; transform: translateX(0); }
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1) { animation: entradaCascada 0.5s ease-out 0.1s forwards; opacity: 0; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2) { animation: entradaCascada 0.5s ease-out 0.2s forwards; opacity: 0; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3) { animation: entradaCascada 0.5s ease-out 0.3s forwards; opacity: 0; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4) { animation: entradaCascada 0.5s ease-out 0.4s forwards; opacity: 0; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(5) { animation: entradaCascada 0.5s ease-out 0.5s forwards; opacity: 0; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(6) { animation: entradaCascada 0.5s ease-out 0.6s forwards; opacity: 0; }

    button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.5) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(4px) !important;
        transition: all 0.3s ease !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(51, 65, 85, 0.9) !important;
        border-color: #94a3b8 !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4) !important;
    }

    [data-testid="stTabs"] button {
        border-radius: 8px 8px 0 0 !important;
        transition: background 0.2s !important;
    }
    [data-testid="stTabs"] button:hover {
        background: rgba(255, 255, 255, 0.05) !important;
    }

    @keyframes suaveAparicion {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .main [data-testid="stVerticalBlock"] > div,
    [data-testid="stDataFrame"], 
    [data-testid="stExpander"], 
    div[role="tabpanel"] {
        animation: suaveAparicion 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards !important;
    }

    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3) !important;
        margin-top: 20px !important;
        animation: none !important; 
    }
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.6) !important;
        border-color: #ffffff !important;
    }
    [data-testid="stSidebar"] button p {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    
    /* ══════════════════════════════
       BARRA DE DESPLAZAMIENTO (SCROLLBAR) DE LUJO
    ══════════════════════════════ */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #050C17;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.3);
        border-radius: 5px;
        transition: background 0.3s ease;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.8);
    }

    /* ══════════════════════════════
       FICHAS (EXPANDERS) REACTIVAS
    ══════════════════════════════ */
    [data-testid="stExpander"] {
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.15) !important;
        background-color: rgba(15, 23, 42, 0.3) !important;
        transition: all 0.3s ease !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.1) !important;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 2. UTILIDADES Y CONFIGURACIÓN HORARIA
# ─────────────────────────────────────────
CHILE_TZ = pytz.timezone("America/Santiago")

def get_local_now() -> str:
    return datetime.now(CHILE_TZ).replace(microsecond=0).isoformat()

def get_local_date() -> str:
    return datetime.now(CHILE_TZ).strftime("%d/%m/%Y")

def verify_password(plain: str, stored) -> bool:
    stored = str(stored)
    if stored.startswith("$2b$") or stored.startswith("$2a$"):
        return bcrypt.checkpw(plain.encode(), stored.encode())
    return plain == stored

def clean_timestamp_to_date(raw_date) -> str:
    if not raw_date or raw_date == "-": return "-"
    raw_str = str(raw_date).strip()
    if 'T' in raw_str: raw_str = raw_str.split('T')[0]
    if '-' in raw_str and not raw_str.startswith('-'):
        try:
            parts = raw_str.split('-')
            if len(parts[0]) == 4:
                dt = datetime.strptime(raw_str, "%Y-%m-%d")
                return dt.strftime("%d/%m/%Y")
        except: pass
    return raw_str

# ─────────────────────────────────────────
# PDF EXPORT 
# ─────────────────────────────────────────
def export_pdf_component(child_data):
    f_ingreso_pdf = clean_timestamp_to_date(child_data.get('fecha_ingreso', '-'))
    f_egreso_pdf = clean_timestamp_to_date(child_data.get('fecha_egreso', '-'))

    html_madre = str(child_data.get('madre', '-')).replace('\n', '<br>')
    html_padre = str(child_data.get('padre', '-')).replace('\n', '<br>')
    html_historia = str(child_data.get('historia_social', 'No se registran antecedentes adicionales.')).replace('\n', '<br>')

    html_content = f"""
    <div id="pdf-container" style="font-family: Arial, sans-serif; color: #1e293b; background: #ffffff; padding: 0;">
        <table style="width: 100%; background-color: #1e3a8a; color: white; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="padding: 20px; width: 15%; text-align: center;"><img src="{LOGO_SRC}" style="height: 60px;"></td>
                <td style="padding: 20px 10px; width: 50%;">
                    <h1 style="margin: 0; font-size: 24px;">GOTA DE LECHE</h1>
                    <p style="margin: 4px 0 0 0; font-size: 11px; text-transform: uppercase;">Ficha Oficial del Beneficiario</p>
                </td>
                <td style="padding: 20px; width: 35%; text-align: right;">
                    <div style="font-size: 11px; margin-bottom: 6px; text-transform: uppercase;">Documento Clínico - Social</div>
                    <div style="font-size: 14px; font-weight: bold; color: #1e3a8a; background: white; padding: 6px 12px; border-radius: 4px; display: inline-block;">Ficha N° {child_data.get('ficha', '-')}</div>
                </td>
            </tr>
        </table>
        <div style="padding: 0 30px;">
            <p style="text-align: right; font-size: 12px; color: #64748b; margin-bottom: 20px; font-style: italic;">Fecha de Emisión: {get_local_date()}</p>
            <h3 style="color: #1e3a8a; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; margin-bottom: 15px;">1. Identificación y Datos Clínicos</h3>
            <table style="width: 100%; font-size: 13px; border-collapse: collapse; margin-bottom: 30px;">
                <tr><td colspan="2" style="padding-bottom: 12px;"><b>NOMBRE COMPLETO DEL NIÑO(A):</b> <br> {child_data.get('nombre', '-')}</td></tr>
                <tr>
                    <td style="width: 50%; padding-bottom: 12px;"><b>RUN / IDENTIFICACIÓN:</b> <br> {child_data.get('rut', '-')}</td>
                    <td style="width: 50%; padding-bottom: 12px;"><b>FECHA DE NACIMIENTO:</b> <br> {child_data.get('nacimiento', '-')}</td>
                </tr>
                <tr>
                    <td style="padding-bottom: 12px;"><b>SEXO:</b> <br> {child_data.get('sexo', '-')}</td>
                    <td style="padding-bottom: 12px;"><b>PESO AL NACER:</b> <br> {child_data.get('peso_nacer', '-')}</td>
                </tr>
                <tr>
                    <td style="padding-bottom: 12px;"><b>COMUNA:</b> <br> {child_data.get('comuna', '-')}</td>
                    <td style="padding-bottom: 12px;"><b>PREVISIÓN SALUD:</b> <br> {child_data.get('prevision', '-')}</td>
                </tr>
                <tr>
                    <td style="padding-bottom: 12px; color: #dc2626;"><b>ALERGIAS / CONDICIÓN:</b> <br> {child_data.get('alergias', '-')}</td>
                    <td style="padding-bottom: 12px;"><b>VACUNAS AL DÍA:</b> <br> {child_data.get('vacunas', '-')}</td>
                </tr>
                <tr>
                    <td style="padding-bottom: 12px; color: #16a34a;"><b>FECHA INGRESO PROGRAMA:</b> <br> {f_ingreso_pdf}</td>
                    <td style="padding-bottom: 12px; color: #dc2626;"><b>FECHA ESTIMADA EGRESO:</b> <br> {f_egreso_pdf}</td>
                </tr>
            </table>
            <h3 style="color: #1e3a8a; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; margin-bottom: 15px;">2. Contexto Familiar y Contactos</h3>
            <div style="font-size: 13px; margin-bottom: 15px; line-height: 1.5;">
                <b style="text-transform: uppercase; color: #1e3a8a;">Antecedentes de la Madre:</b><br>{html_madre}
            </div>
            <div style="font-size: 13px; margin-bottom: 20px; line-height: 1.5;">
                <b style="text-transform: uppercase; color: #1e3a8a;">Antecedentes del Padre:</b><br>{html_padre}
            </div>
            <table style="width: 100%; font-size: 12px; background-color: #f8fafc; border-collapse: collapse; margin-bottom: 30px; border: 1px solid #e2e8f0;">
                <tr><td colspan="2" style="padding: 10px; border-bottom: 1px solid #e2e8f0;"><b>DIRECCIÓN PARTICULAR:</b> {child_data.get('direccion', '-')}</td></tr>
                <tr>
                    <td style="width: 50%; padding: 10px; border-right: 1px solid #e2e8f0;"><b>TELÉFONO MADRE:</b> <br> {child_data.get('telefono_madre', '-')}</td>
                    <td style="width: 50%; padding: 10px;"><b>TELÉFONO PADRE:</b> <br> {child_data.get('telefono_padre', '-')}</td>
                </tr>
                <tr><td colspan="2" style="padding: 10px; border-top: 1px solid #e2e8f0;"><b>TELÉFONO Y NOMBRE SUPLENTE AUTORIZADO:</b> <br> {child_data.get('suplentes', '-')}</td></tr>
            </table>
            <h3 style="color: #065f46; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #10b981; padding-bottom: 5px; margin-bottom: 15px;">3. Historia Social y Antecedentes Generales</h3>
            <div style="font-size: 13px; line-height: 1.6; text-align: justify; margin-bottom: 40px; color: #334155;">{html_historia}</div>
            <table style="width: 100%; margin-top: 50px; border-collapse: collapse; page-break-inside: avoid;">
                <tr>
                    <td style="width: 40%; text-align: center; border-top: 1px solid #94a3b8; padding-top: 10px; font-size: 12px; color: #475569;"><b style="color: #0f172a;">Firma Asistente Social</b><br>Gota de Leche</td>
                    <td style="width: 20%;"></td>
                    <td style="width: 40%; text-align: center; border-top: 1px solid #94a3b8; padding-top: 10px; font-size: 12px; color: #475569;"><b style="color: #0f172a;">Validación Interna</b><br>Revisión Documental</td>
                </tr>
            </table>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script>
        window.onload = function() {{
            setTimeout(function() {{
                var element = document.getElementById('pdf-container');
                var opt = {{
                    margin:       [15, 10, 20, 10], 
                    filename:     'Ficha_GotaDeLeche_{child_data.get("ficha", "_")}.pdf',
                    image:        {{ type: 'jpeg', quality: 1.0 }},
                    html2canvas:  {{ scale: 2, useCORS: true, logging: false }},
                    jsPDF:        {{ unit: 'mm', format: 'letter', orientation: 'portrait' }},
                    pagebreak:    {{ mode: ['css'] }} 
                }};
                html2pdf().set(opt).from(element).save();
            }}, 600);
        }}
    </script>
    """
    components.html(html_content, height=0, width=0)

# ─────────────────────────────────────────
# 3. CONEXIÓN A BASE DATOS
# ─────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError as e:
        st.error(f"Falta la credencial en Secrets: {e}"); st.stop()
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}"); st.stop()

supabase = init_supabase()

# ─────────────────────────────────────────
# 4. LOGIN
# ─────────────────────────────────────────
if "user" not in st.session_state:
    st.markdown("<style>section[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 0.8, 1])
    with col_mid:
        st.markdown('<div class="centered-login">', unsafe_allow_html=True)
        
        # LOGO TOTALMENTE LIMPIO
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 28px; width: 100%;">
                <img src="{LOGO_SRC}" style="height: 180px; object-fit: contain; display: inline-block;">
                <h1 style="color:#e2e8f0; font-size:2.2rem; margin:0; font-weight:800; text-align:center;">GOTA DE LECHE</h1>
                <p style="color:#cbd5e1; font-size:0.85rem; margin:2px 0 0 0; letter-spacing:0.15em; text-transform:uppercase; font-weight:600; text-align:center; transform: translateX(4px);">SISTEMA MAESTRO DE GESTIÓN</p>
            </div>
        """, unsafe_allow_html=True)
        
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
                            st.error("Usuario o contraseña incorrectos.")
                    except Exception as e:
                        st.error("No fue posible conectar con el servidor.")
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 5. PANEL PRINCIPAL (SESIÓN ACTIVA)
# ─────────────────────────────────────────
else:
    user = st.session_state.user
    MAX_FICHAS = 210
    
    with st.sidebar:
        # LOGO LATERAL TOTALMENTE LIMPIO
        st.markdown(f"""
            <div style="text-align:center; margin-bottom:20px; margin-top:10px;">
                <img src="{LOGO_SRC}" style="height:130px; object-fit:contain;">
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"### :material/person: {user['nombre']}")
        
        if user["usuario"].lower() == SUPER_ADMIN.lower():
            st.caption(f":material/stars: Super Administrador")
        else:
            st.caption(f"Operador autorizado")
            
        st.divider()
        
        # MENU CON MATERIAL ICONS DE STREAMLIT
        opciones_menu = [
            ":material/bar_chart: PANEL PRINCIPAL", 
            ":material/inventory_2: BODEGA CENTRAL", 
            ":material/medical_services: SALA DE ATENCIÓN", 
            ":material/groups: GESTIÓN DE NIÑOS", 
            ":material/manage_search: HISTORIAL"
        ]
        
        if user["usuario"].lower() == SUPER_ADMIN.lower():
            opciones_menu.append(":material/security: PANEL ADMIN")
        
        menu_choice = st.radio("MENÚ PRINCIPAL", opciones_menu, label_visibility="collapsed")
        
        st.divider()
        if st.button(":material/logout: CERRAR SESIÓN", use_container_width=True, help="logout"):
            st.session_state.clear()
            st.rerun()

    # 📊 PANEL PRINCIPAL
    if menu_choice == ":material/bar_chart: PANEL PRINCIPAL":
        st.header(":material/bar_chart: Resumen de Operación e Info Inmediata", divider="blue")
        try:
            with st.spinner("Actualizando métricas..."):
                stock_res = supabase.table("stock").select("*").order("producto").execute()
                benef_res = supabase.table("beneficiarios").select("rut", count="exact").eq("estado", "Activo").execute()
        except Exception as e:
            st.error(f"Error al conectar con Supabase: {e}"); st.stop()
            
        if stock_res.data:
            df = pd.DataFrame(stock_res.data)
            niños_activos = benef_res.count if benef_res.count else 0
            fichas_disponibles = max(0, MAX_FICHAS - niños_activos)
            
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown(f'<div class="metric-card"><div class="metric-label">Niños Activos</div><div class="metric-value">{niños_activos} <span style="font-size:1.1rem; color:#94a3b8;">/ {MAX_FICHAS}</span></div></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card"><div class="metric-label">Fichas Disponibles</div><div class="metric-value" style="color:#10b981;">{fichas_disponibles}</div></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-card"><div class="metric-label">Total en Sala</div><div class="metric-value">{int(df["sala"].sum())} <span style="font-size:1.1rem; color:#94a3b8;">unid</span></div></div>', unsafe_allow_html=True)
            with m4: st.markdown(f'<div class="metric-card"><div class="metric-label">Bodega Central</div><div class="metric-value">{int(df["bodega"].sum())} <span style="font-size:1.1rem; color:#94a3b8;">unid</span></div></div>', unsafe_allow_html=True)
            
            productos_filtrados = [item for item in stock_res.data if item["producto"].upper() not in ["AJUAR", "OTROS"]]
            
            # 📦 STOCK DE BODEGA NORMALIZADO
            st.write("###")
            st.markdown("### :material/inventory_2: Stock de Bodega")
            cols_bodega = st.columns(3)
            for i, item in enumerate(productos_filtrados):
                with cols_bodega[i % 3]:
                    st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-label" style="font-size:1rem; min-height:40px; display:flex; align-items:center; justify-content:center;">{item["producto"]}</div>
                            <div class="metric-value" style="color: #38bdf8;">{int(item["bodega"])} <span style="font-size:1.2rem; color:#94a3b8;">ud</span></div>
                        </div>
                    ''', unsafe_allow_html=True)

            # ⚖️ INSUMOS SALA NORMALIZADOS
            st.write("###")
            st.markdown("### :material/medical_services: Insumos Sala de Atención")
            cols_sala = st.columns(3)
            for i, item in enumerate(productos_filtrados):
                with cols_sala[i % 3]:
                    st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-label" style="font-size:1rem; min-height:40px; display:flex; align-items:center; justify-content:center;">{item["producto"]}</div>
                            <div class="metric-value" style="color: #38bdf8;">{int(item["sala"])} <span style="font-size:1.2rem; color:#94a3b8;">ud</span></div>
                        </div>
                    ''', unsafe_allow_html=True)

    # 📦 PANEL: BODEGA CENTRAL
    elif menu_choice == ":material/inventory_2: BODEGA CENTRAL":
        st.header(":material/inventory_2: Gestión e Inventario General", divider="blue")
        try:
            raw = supabase.table("stock").select("*").order("id").execute().data
        except Exception as e:
            st.error(f"Fallo al recuperar stock: {e}"); st.stop()
            
        df_inventory = pd.DataFrame(raw)
        st.write("### Niveles Actuales de Existencias")

        html_bodega = "<style>"
        html_bodega += ".bodega-table { width: 100%; border-collapse: collapse; margin-top: 10px; }"
        html_bodega += ".bodega-table th { background: rgba(30, 41, 59, 0.8); color: #94a3b8; font-size: 1.05rem; padding: 14px; text-transform: uppercase; border-bottom: 2px solid #3b82f6; text-align: left; }"
        html_bodega += ".bodega-table th:first-child { border-radius: 8px 0 0 0; }"
        html_bodega += ".bodega-table th:last-child { border-radius: 0 8px 0 0; }"
        html_bodega += ".bodega-table td { padding: 14px 14px; font-size: 1.15rem; color: #f8fafc; border-bottom: 1px solid rgba(148, 163, 184, 0.1); }"
        html_bodega += ".bodega-table td:first-child { font-weight: 500; color: #cbd5e1; }"
        html_bodega += ".bodega-table tr:hover td { background-color: rgba(59, 130, 246, 0.15); }"
        html_bodega += ".bodega-num { font-size: 1.35rem !important; font-weight: 800; color: #38bdf8; }" 
        html_bodega += ".bodega-unidades { font-size: 1rem; color: #94a3b8; font-weight: 500; }"
        html_bodega += "</style>"

        html_bodega += "<table class='bodega-table'>"
        html_bodega += "<thead><tr><th>Descripción de Insumo</th><th>Cantidad en Bodega Principal</th><th>Cantidad en Sala de Atención</th></tr></thead>"
        html_bodega += "<tbody>"

        for _, row in df_inventory.iterrows():
            html_bodega += f"<tr>"
            html_bodega += f"<td>{row['producto']}</td>"
            html_bodega += f"<td><span class='bodega-num'>{int(row['bodega'])}</span> <span class='bodega-unidades'>Unidades</span></td>"
            html_bodega += f"<td><span class='bodega-num'>{int(row['sala'])}</span> <span class='bodega-unidades'>Unidades</span></td>"
            html_bodega += f"</tr>"

        html_bodega += "</tbody></table>"

        st.markdown(html_bodega, unsafe_allow_html=True)
        
        st.write("###")
        with st.expander(":material/sync_alt: EJECUTAR MOVIMIENTO INTERNO DE STOCK", expanded=True):
            with st.form("mov_form"):
                c1, c2, c3 = st.columns([1.5, 1, 1.5])
                with c1: product_name = st.selectbox("Seleccione Insumo / Alimento", df_inventory["producto"].tolist())
                with c2: quantity = st.number_input("Cantidad de Unidades", min_value=1, step=1)
                with c3: movement_type = st.radio("Acción a realizar", ["Ingreso a Bodega", "Traslado a Sala"], horizontal=True)
                
                if st.form_submit_button("PROCESAR OPERACIÓN", type="primary", use_container_width=True):
                    row = df_inventory[df_inventory["producto"] == product_name].iloc[0]
                    if movement_type == "Traslado a Sala" and row["bodega"] < quantity:
                        st.error(f"⚠️ Stock insuficiente en bodega principal. Disponibles: {row['bodega']} unidades.")
                    else:
                        with st.spinner(f"Procesando {movement_type}..."):
                            try:
                                cant_operacion = int(quantity)
                                bodega_actual = int(row["bodega"])
                                sala_actual = int(row["sala"])
                                id_registro = int(row["id"])

                                if movement_type == "Ingreso a Bodega":
                                    supabase.table("stock").update({"bodega": bodega_actual + cant_operacion}).eq("id", id_registro).execute()
                                else:
                                    supabase.table("stock").update({"bodega": bodega_actual - cant_operacion, "sala": sala_actual + cant_operacion}).eq("id", id_registro).execute()
                                
                                detalle = f"Operación realizada: {movement_type} de {cant_operacion} unidades."
                                supabase.table("historial").insert({
                                    "responsable": user["nombre"], 
                                    "producto": product_name,
                                    "cantidad": cant_operacion, 
                                    "tipo": movement_type.upper(), 
                                    "observaciones": detalle, 
                                    "created_at": get_local_now() 
                                }).execute()
                                
                                st.toast("Inventario actualizado.", icon="✅")
                                time.sleep(1.2); st.rerun() 
                            except Exception as e:
                                st.error(f"Error crítico en la transacción: {e}")

    # ⚖️ PANEL: SALA DE ATENCIÓN
    elif menu_choice == ":material/medical_services: SALA DE ATENCIÓN":
        st.header(":material/medical_services: Sala de Atención - Despacho y Control", divider="blue")
        tab_entrega, tab_resumen_stock = st.tabs([":material/edit_document: CONTROL DE ENTREGA Y PESO", ":material/analytics: RESUMEN DE INGRESOS Y SALIDAS"])
        
        try:
            stock_data = supabase.table("stock").select("*").order("producto").execute().data
        except Exception as e:
            st.error(f"Error de stock: {e}"); st.stop()
            
        with tab_entrega:
            metodo_busqueda = st.radio("Buscar beneficiario por:", [":material/badge: N° de Ficha", ":material/id_card: RUN / Identificación"], horizontal=True)
            recipient_name, ficha_vinculada, opciones_retiro, beneficiary = "", 0, ["--"], None
            
            if metodo_busqueda == ":material/badge: N° de Ficha":
                ficha_number = st.number_input("Escanear o Digitar N° de Ficha", min_value=0, step=1, key="input_ficha_entrega")
                if ficha_number > 0:
                    try:
                        res = supabase.table("beneficiarios").select("*").eq("ficha", ficha_number).eq("estado", "Activo").execute()
                        if res.data: beneficiary = res.data[0]
                        else: st.warning("No se localizó ningún beneficiario activo bajo este número de ficha.")
                    except Exception as e: st.error(f"Error: {e}")
            else:
                rut_input = st.text_input("Escanear o Ingresar RUN / Identificación", placeholder="Ej: 12345678-9", key="input_rut_entrega").strip()
                if rut_input:
                    try:
                        res = supabase.table("beneficiarios").select("*").eq("rut", rut_input).eq("estado", "Activo").execute()
                        if res.data: beneficiary = res.data[0]
                        else: st.warning("No se localizó ningún beneficiario activo con el RUN ingresado.")
                    except Exception as e: st.error(f"Error: {e}")
            
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
            
            product_options = ["--"] + [f"{x['producto']} (Disp: {int(x['sala'])})" for x in stock_data if x["producto"].upper() not in ["AJUAR", "OTROS"]]
            
            with st.form("delivery_master_form"):
                st.markdown("##### :material/inventory: Desglose Obligatorio de Insumos")
                
                pills_html = "<div style='display:flex; flex-wrap:wrap; gap:12px; margin-bottom: 24px;'>"
                for item in stock_data:
                    if item["producto"].upper() not in ["AJUAR", "OTROS"]:
                        color_alerta = "#ef4444" if item['sala'] <= 0 else "#38bdf8"
                        borde_alerta = "rgba(239, 68, 68, 0.6)" if item['sala'] <= 0 else "rgba(148, 163, 184, 0.3)"
                        bg_alerta = "rgba(239, 68, 68, 0.15)" if item['sala'] <= 0 else "rgba(15, 23, 42, 0.6)"
                        
                        pills_html += f"<div style='background:{bg_alerta}; border:2px solid {borde_alerta}; padding: 10px 18px; border-radius: 8px; font-size: 1.15rem; color: #f8fafc; display: flex; align-items: center; gap: 8px;'><span>{item['producto']}:</span> <strong style='color:{color_alerta}; font-size: 1.4rem;'>{int(item['sala'])}</strong></div>"
                pills_html += "</div>"
                st.markdown(pills_html, unsafe_allow_html=True)
                
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
                st.markdown("##### :material/monitor_weight: Control de Peso (Opcional)")
                peso_visita = st.text_input("Registrar peso actual del niño(a) en esta visita:", placeholder="Ej: 14.5 kg")

                st.divider()
                st.markdown("##### :material/how_to_reg: Control de Retiro Autorizado")
                quien_retira_tipo = st.selectbox("Persona que retira de la ficha:", opciones_retiro)
                nombre_firma_especifico = st.text_input("Nombre completo de quien recibe físicamente (Firma digital):", placeholder="Escriba el nombre de la persona que se lleva los insumos")
                
                if st.form_submit_button(":material/task_alt: CONVALIDAR Y REGISTRAR ENTREGA", type="primary", use_container_width=True):
                    
                    def clean_name(val):
                        return val.rsplit(" (Disp:", 1)[0] if val != "--" else "--"
                        
                    items_validados = [(clean_name(prod_1), qty_1), (clean_name(prod_2), qty_2), (clean_name(prod_3), qty_3)]
                    any_empty = any(p == "--" or q <= 0 for p, q in items_validados)
                    
                    if ficha_vinculada == 0: st.error("Operación abortada: Debe identificar primero a un beneficiario activo mediante Ficha o RUN.")
                    elif any_empty: st.error("❌ ERROR DE CAMPO OBLIGATORIO: Las voluntarias deben registrar obligatoriamente los 3 ítems de insumos con cantidades mayores a cero.")
                    elif not nombre_firma_especifico: st.error("❌ ERROR DE CAMPO OBLIGATORIO: Debe ingresar el nombre completo de la persona que recibe físicamente.")
                    else:
                        errors_stock = []
                        for p_name, qty in items_validados:
                            item = next((x for x in stock_data if x["producto"] == p_name), None)
                            if not item: errors_stock.append(f"El producto '{p_name}' no existe.")
                            elif item["sala"] < qty: errors_stock.append(f"Falta Stock para '{p_name}'. En sala: {item['sala']} | Solicitado: {qty}.")
                                
                        if errors_stock:
                            for err in errors_stock: st.error(err)
                        else:
                            with st.spinner("Validando stock y registrando operación..."):
                                try:
                                    if peso_visita.strip():
                                        supabase.table("controles_peso").insert({
                                            "ficha": ficha_vinculada,
                                            "rut": beneficiary["rut"],
                                            "fecha": get_local_now(),
                                            "peso": peso_visita.strip(),
                                            "responsable": user["nombre"]
                                        }).execute()
                                        
                                        nuevo_control = f"{get_local_date()} - {peso_visita.strip()}"
                                        supabase.table("beneficiarios").update({"control": nuevo_control}).eq("rut", beneficiary["rut"]).execute()

                                    detalle_receptor = f"{quien_retira_tipo} (Recibe: {nombre_firma_especifico})"
                                    for p_name, qty in items_validados:
                                        item = next(x for x in stock_data if x["producto"] == p_name)
                                        supabase.table("stock").update({"sala": int(item["sala"] - qty)}).eq("id", int(item["id"])).execute()
                                        
                                        obs_limpia = f"Ficha {ficha_vinculada} | RUT: {beneficiary['rut']} - {detalle_receptor}"
                                        supabase.table("historial").insert({
                                            "responsable": user["nombre"], "producto": p_name, "cantidad": int(qty),
                                            "tipo": "ENTREGA", "observaciones": obs_limpia, "created_at": get_local_now(),
                                        }).execute()
                                    
                                    st.balloons() 
                                    st.toast("Entrega guardada con éxito.", icon="✅")
                                    time.sleep(1.8); st.rerun() 
                                except Exception as e: st.error(f"Error crítico guardando la entrega: {e}")
                                
        with tab_resumen_stock:
            st.markdown("### :material/analytics: Resumen Estadístico de Cargas en Sala de Atención")
            try:
                historial_completo = supabase.table("historial").select("*").execute().data
                df_h = pd.DataFrame(historial_completo) if historial_completo else pd.DataFrame()
            except: df_h = pd.DataFrame()
                
            if df_h.empty: st.info("No hay transacciones registradas.")
            else:
                resumen_productos = []
                for p in stock_data:
                    p_name = p["producto"]
                    if p_name.upper() in ["AJUAR", "OTROS"]: continue
                    entradas = df_h[(df_h["producto"] == p_name) & (df_h["tipo"] == "TRASLADO A SALA")]["cantidad"].astype(int).sum()
                    salidas = df_h[(df_h["producto"] == p_name) & (df_h["tipo"] == "ENTREGA")]["cantidad"].astype(int).sum()
                    resumen_productos.append({"Insumo / Alimento": p_name, "Recibidos (Desde Bodega)": entradas, "Total Entregado": salidas, "Saldo Disponible": p["sala"]})
                
                df_resumen = pd.DataFrame(resumen_productos)
                
                html_table = "<style>"
                html_table += ".big-table { width: 100%; border-collapse: collapse; margin-top: 10px; }"
                html_table += ".big-table th { background: rgba(30, 41, 59, 0.8); color: #94a3b8; font-size: 1.05rem; padding: 14px; text-transform: uppercase; border-bottom: 2px solid #3b82f6; text-align: center; }"
                html_table += ".big-table th:first-child { text-align: left; border-radius: 8px 0 0 0; }"
                html_table += ".big-table th:last-child { border-radius: 0 8px 0 0; }"
                html_table += ".big-table td { padding: 16px 14px; font-size: 1.5rem; color: #f8fafc; border-bottom: 1px solid rgba(148, 163, 184, 0.1); text-align: center; font-weight: 600; }"
                html_table += ".big-table td:first-child { text-align: left; font-size: 1.25rem; font-weight: 500; color: #cbd5e1; }"
                html_table += ".big-table tr:hover td { background-color: rgba(59, 130, 246, 0.15); }"
                html_table += ".saldo-destacado { color: #38bdf8 !important; font-weight: 800 !important; font-size: 1.7rem !important; text-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }"
                html_table += "</style>"
                
                html_table += "<table class='big-table'>"
                html_table += "<thead><tr><th>Insumo / Alimento</th><th>Recibidos</th><th>Entregados</th><th>Saldo Disponible</th></tr></thead>"
                html_table += "<tbody>"
                
                for _, row in df_resumen.iterrows():
                    html_table += f"<tr><td>{row['Insumo / Alimento']}</td><td>{row['Recibidos (Desde Bodega)']}</td><td>{row['Total Entregado']}</td><td class='saldo-destacado'>{row['Saldo Disponible']}</td></tr>"
                    
                html_table += "</tbody></table>"
                
                st.markdown(html_table, unsafe_allow_html=True)
                
                st.write("###")
                buffer_resumen = io.BytesIO()
                with pd.ExcelWriter(buffer_resumen, engine='openpyxl') as writer:
                    df_resumen.to_excel(writer, index=False, sheet_name='Resumen Sala')
                
                st.download_button(
                    label=":material/download: Descargar Resumen en Excel (.xlsx)",
                    data=buffer_resumen.getvalue(),
                    file_name=f"Resumen_Sala_{datetime.now(CHILE_TZ).strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

    # 👥 PANEL: GESTIÓN DE NIÑOS
    elif menu_choice == ":material/groups: GESTIÓN DE NIÑOS":
        st.header(":material/groups: Padrón de Beneficiarios", divider="blue")
        tab_active, tab_inactive = st.tabs([":material/person_check: NIÑOS ACTIVOS", ":material/person_off: HISTORIAL DE EGRESOS"])
        
        try:
            todas_fichas_res = supabase.table("beneficiarios").select("ficha").eq("estado", "Activo").execute()
            fichas_ocupadas = {row["ficha"] for row in todas_fichas_res.data} if todas_fichas_res.data else set()
        except: 
            fichas_ocupadas = set()
        
        fichas_disponibles = sorted(list(set(range(1, MAX_FICHAS + 1)) - fichas_ocupadas))

        try:
            todo_el_historial = supabase.table("historial").select("*").eq("tipo", "ENTREGA").execute().data
            df_entregas_global = pd.DataFrame(todo_el_historial) if todo_el_historial else pd.DataFrame()
            if not df_entregas_global.empty:
                df_entregas_global["created_at"] = pd.to_datetime(df_entregas_global["created_at"], errors="coerce")
                if df_entregas_global["created_at"].dt.tz is None:
                    df_entregas_global["created_at"] = df_entregas_global["created_at"].dt.tz_localize('UTC').dt.tz_convert(CHILE_TZ)
                else:
                    df_entregas_global["created_at"] = df_entregas_global["created_at"].dt.tz_convert(CHILE_TZ)
                    
            todo_los_pesos = supabase.table("controles_peso").select("*").execute().data
            df_pesos_global = pd.DataFrame(todo_los_pesos) if todo_los_pesos else pd.DataFrame()
            if not df_pesos_global.empty:
                df_pesos_global["fecha"] = pd.to_datetime(df_pesos_global["fecha"], errors="coerce")
                if df_pesos_global["fecha"].dt.tz is None:
                    df_pesos_global["fecha"] = df_pesos_global["fecha"].dt.tz_localize('UTC').dt.tz_convert(CHILE_TZ)
                else:
                    df_pesos_global["fecha"] = df_pesos_global["fecha"].dt.tz_convert(CHILE_TZ)
        except: 
            df_entregas_global = pd.DataFrame()
            df_pesos_global = pd.DataFrame()

        if "pdf_trigger" in st.session_state and st.session_state.pdf_trigger is not None:
            export_pdf_component(st.session_state.pdf_trigger)
            st.session_state.pdf_trigger = None

        with tab_active:
            with st.expander(":material/person_add: INSCRIBIR NUEVO BENEFICIARIO (MÁXIMO 210 FICHAS)", expanded=False):
                if not fichas_disponibles:
                    st.warning("⚠️ Se ha alcanzado el límite histórico de 210 fichas físicas asignadas al mismo tiempo.")
                else:
                    with st.form("new_child_form"):
                        st.markdown("##### I. Identificación General")
                        c1, c2, c3 = st.columns([2, 1.5, 1])
                        name = c1.text_input("Nombre Completo del Niño(a) *")
                        rut = c2.text_input("RUN / Identificación *")
                        ficha = c3.selectbox("N° Ficha Disponible", fichas_disponibles)
                        
                        st.markdown("##### II. Datos Clínicos")
                        cc1, cc2, cc3 = st.columns(3)
                        birth_date = cc1.text_input("Fecha Nacimiento (DD/MM/AAAA)")
                        sexo = cc2.selectbox("Sexo", ["Masculino", "Femenino"])
                        peso_nacer = cc3.text_input("Peso al Nacer (ej: 3.935 kg)")
                        
                        cx1, cx2, cx3 = st.columns(3)
                        alergias = cx1.text_input("Alergias / Condiciones Médicas")
                        prevision = cx2.selectbox("Previsión de Salud", ["Fonasa A", "Fonasa B", "Fonasa C", "Fonasa D", "Isapre", "Particular", "Ninguna"])
                        vacunas = cx3.selectbox("¿Vacunas al Día?", ["Sí", "No"])
                        
                        ultimo_control = st.text_input("Último Control Médico base (ej: 30.03.26 / 3.820 kg)")
                        
                        st.markdown("##### III. Contacto y Familia")
                        comuna = st.text_input("Comuna de Residencia")
                        
                        c_tel1, c_tel2, c_tel3 = st.columns(3)
                        tel_madre = c_tel1.text_input("Teléfono de la Madre")
                        tel_padre = c_tel2.text_input("Teléfono del Padre")
                        tel_suplente = c_tel3.text_input("Teléfono de Suplente")
                        
                        address = st.text_input("Dirección Particular Completa")
                        
                        mother = st.text_area("Datos de la Madre (Nacionalidad, Edad, Escolaridad, Ocupación)")
                        father = st.text_area("Datos del Padre (Nacionalidad, Edad, Escolaridad, Ocupación)")
                        nombre_suplente = st.text_input("Nombre del Suplente Autorizado (Asociado al teléfono arriba)")
                        
                        social_history = st.text_area("Antecedentes Importantes / Historia Social")
                        
                        if st.form_submit_button(":material/save: INGRESAR BENEFICIARIO AL SISTEMA", type="primary"):
                            if not name or not rut: st.error("Campos obligatorios faltantes: Nombre y RUN son requeridos.")
                            else:
                                with st.spinner("Generando nueva ficha clínica en el servidor..."):
                                    try:
                                        f_ingreso_dt = datetime.now(CHILE_TZ)
                                        f_egreso_dt = f_ingreso_dt + timedelta(days=730)
                                        
                                        string_ingreso = f_ingreso_dt.strftime("%Y-%m-%d")
                                        string_egreso = f_egreso_dt.strftime("%Y-%m-%d")
                                        
                                        u_suplentes_new = f"{nombre_suplente.strip()} - Tel: {tel_suplente.strip()}" if tel_suplente.strip() else nombre_suplente.strip()
                                        if not u_suplentes_new: u_suplentes_new = "-"
                                            
                                        check_ficha = supabase.table("beneficiarios").select("ficha, nombre").eq("ficha", ficha).eq("estado", "Activo").execute()
                                        if check_ficha.data: st.error(f"Conflicto: El N° de ficha {ficha} está actualmente en uso por: {check_ficha.data[0]['nombre']}")
                                        else:
                                            supabase.table("beneficiarios").insert({
                                                "nombre": name, "rut": rut, "ficha": ficha, "nacimiento": birth_date,
                                                "sexo": sexo, "peso_nacer": peso_nacer, "vacunas": vacunas, "control": ultimo_control,
                                                "alergias": alergias, "prevision": prevision, "comuna": comuna,
                                                "telefono_madre": tel_madre, "telefono_padre": tel_padre, 
                                                "direccion": address, "madre": mother, "padre": father,
                                                "suplentes": u_suplentes_new, "historia_social": social_history, "estado": "Activo",
                                                "fecha_ingreso": string_ingreso, "fecha_egreso": string_egreso
                                            }).execute()
                                            st.success("Registro clínico-social creado exitosamente.", icon="✅")
                                            st.balloons() 
                                            time.sleep(1.8); st.rerun() 
                                    except Exception as e: st.error(f"Fallo en inserción: {e}")
                                
            try: children = supabase.table("beneficiarios").select("*").eq("estado", "Activo").order("ficha").execute().data
            except Exception as e: st.error(f"Error cargando padrón: {e}"); st.stop()
                
            st.write("### Fichas Clínicas en Sistema")
            
            # ICONO BUSCADOR
            busqueda_activos = st.text_input("Buscar niño(a) por Nombre o RUN:", placeholder="Ej: Juan Pérez o 12345678-9")
            
            if busqueda_activos:
                termino = busqueda_activos.lower()
                children_filtrados = [c for c in children if termino in c["nombre"].lower() or termino in c["rut"].lower()]
            else:
                children_filtrados = children

            if not children_filtrados:
                st.warning("No se encontraron fichas activas que coincidan con su búsqueda.")
            else:
                for child in children_filtrados:
                    with st.expander(f":material/folder_shared: Ficha {child['ficha']} — {child['nombre']} ({child.get('sexo','-')})"):
                        btn_col1, btn_col2, btn_col3, _ = st.columns([1.5, 1.5, 1.5, 2.5])
                        with btn_col1:
                            if st.button(f":material/picture_as_pdf: Descargar Ficha PDF", key=f"pdf_{child['ficha']}_{child['rut']}", use_container_width=True):
                                st.session_state.pdf_trigger = child; st.rerun()
                        with btn_col2:
                            edit_key = f"edit_mode_{child['rut']}"
                            if edit_key not in st.session_state: st.session_state[edit_key] = False
                            if st.button(f":material/edit: Editar Datos", key=f"btn_edit_{child['rut']}", use_container_width=True):
                                st.session_state[edit_key] = not st.session_state[edit_key]; st.rerun()
                        with btn_col3:
                            with st.popover(":material/person_remove: Registrar Egreso", use_container_width=True):
                                st.markdown("**Seguridad: Confirmar Acción**")
                                pass_confirm = st.text_input("Ingrese su contraseña para autorizar la baja:", type="password", key=f"pass_egr_{child['rut']}")
                                
                                if st.button("Confirmar Egreso", key=f"btn_conf_egr_{child['rut']}", type="primary", use_container_width=True):
                                    if not pass_confirm:
                                        st.error("⚠️ Debe ingresar su contraseña.")
                                    elif verify_password(pass_confirm, user["clave"]):
                                        with st.spinner("Procesando egreso de ficha..."):
                                            try:
                                                supabase.table("beneficiarios").update({"estado": "Egresado"}).eq("rut", child["rut"]).execute()
                                                supabase.table("historial").insert({"responsable": user["nombre"], "producto": "PADRÓN", "cantidad": 1, "tipo": "EGRESO", "observaciones": f"Ficha {child['ficha']} | RUT: {child['rut']} dada de baja", "created_at": get_local_now()}).execute()
                                                st.toast(f"Beneficiario marcado como Egresado.", icon="✅")
                                                time.sleep(1.5); st.rerun()
                                            except Exception as e: 
                                                st.error(f"Error al egresar: {e}")
                                    else:
                                        st.error("❌ Contraseña incorrecta. Acción denegada.")
                        st.write("---")
                        
                        if st.session_state[edit_key]:
                            with st.form(key=f"form_edit_data_{child['rut']}"):
                                st.markdown("##### Editando Datos Médicos y Personales")
                                ec1, ec2, ec3 = st.columns([2, 1.5, 1])
                                u_name = ec1.text_input("Nombre Completo *", value=child["nombre"])
                                u_rut = ec2.text_input("RUN / Identificación *", value=child["rut"], disabled=True) 
                                u_ficha = ec3.number_input("N° Ficha (Lectura)", value=int(child["ficha"]), disabled=True)
                                
                                ecc1, ecc2, ecc3 = st.columns(3)
                                u_birth = ecc1.text_input("Fecha Nacimiento", value=child.get("nacimiento", ""))
                                u_sexo = ecc2.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if child.get("sexo") == "Masculino" else 1)
                                u_peso = ecc3.text_input("Peso al Nacer", value=child.get("peso_nacer", ""))
                                
                                ecx1, ecx2, ecx3 = st.columns(3)
                                u_alergias = ecx1.text_input("Alergias / Condiciones Médicas", value=child.get("alergias", ""))
                                u_prevision = ecx2.selectbox("Previsión de Salud", ["Fonasa A", "Fonasa B", "Fonasa C", "Fonasa D", "Isapre", "Particular", "Ninguna"], index=["Fonasa A", "Fonasa B", "Fonasa C", "Fonasa D", "Isapre", "Particular", "Ninguna"].index(child.get("prevision", "Fonasa A")) if child.get("prevision") in ["Fonasa A", "Fonasa B", "Fonasa C", "Fonasa D", "Isapre", "Particular", "Ninguna"] else 0)
                                u_vacunas = ecx3.selectbox("¿Vacunas al Día?", ["Sí", "No"], index=0 if child.get("vacunas") == "Sí" else 1)
                                
                                u_control = st.text_input("Último Control Médico base", value=child.get("control", ""))
                                
                                u_comuna = st.text_input("Comuna", value=child.get("comuna", ""))
                                
                                eccc1, eccc2, eccc3 = st.columns(3)
                                u_phone_m = eccc1.text_input("Teléfono Madre", value=child.get("telefono_madre", ""))
                                u_phone_p = eccc2.text_input("Teléfono Padre", value=child.get("telefono_padre", ""))
                                u_suplentes_edit = eccc3.text_input("Nombre y Teléfono Suplente", value=child.get("suplentes", ""))
                                
                                u_address = st.text_input("Dirección Particular", value=child.get("direccion", ""))
                                
                                u_mother = st.text_area("Datos de la Madre (Nacionalidad, Edad, Escolaridad, Ocupación)", value=child.get("madre", ""))
                                u_father = st.text_area("Datos del Padre (Nacionalidad, Edad, Escolaridad, Ocupación)", value=child.get("padre", ""))
                                u_social = st.text_area("Antecedentes / Historia Social", value=child.get("historia_social", ""))
                                
                                if st.form_submit_button(":material/save: GUARDAR CAMBIOS", type="primary", use_container_width=True):
                                    if not u_name: st.error("El nombre no puede quedar vacío.")
                                    else:
                                        with st.spinner("Actualizando datos en el servidor..."):
                                            try:
                                                supabase.table("beneficiarios").update({
                                                    "nombre": u_name, "nacimiento": u_birth, "sexo": u_sexo, 
                                                    "peso_nacer": u_peso, "vacunas": u_vacunas, "control": u_control, 
                                                    "alergias": u_alergias, "prevision": u_prevision, "comuna": u_comuna,
                                                    "madre": u_mother, "padre": u_father, "telefono_madre": u_phone_m, 
                                                    "telefono_padre": u_phone_p, "direccion": u_address, 
                                                    "suplentes": u_suplentes_edit, "historia_social": u_social
                                                }).eq("rut", child["rut"]).execute()
                                                
                                                supabase.table("historial").insert({"responsable": user["nombre"], "producto": "PADRÓN", "cantidad": 1, "tipo": "EDICIÓN", "observaciones": f"Ficha {child['ficha']} corregida", "created_at": get_local_now()}).execute()
                                                st.session_state[edit_key] = False
                                                st.toast("Datos actualizados de manera exitosa.", icon="✅")
                                                time.sleep(1.2); st.rerun()
                                            except Exception as e: st.error(f"Error al actualizar: {e}")
                        else:
                            fecha_ingreso_clean = clean_timestamp_to_date(child.get('fecha_ingreso', '-'))
                            fecha_egreso_clean = clean_timestamp_to_date(child.get('fecha_egreso', '-'))
                            
                            sub_c1, sub_c2, sub_c3 = st.columns(3)
                            with sub_c1:
                                st.markdown(f"**RUN:** `{child['rut']}`")
                                st.markdown(f"**Nacimiento:** {child.get('nacimiento', '-')}")
                                st.markdown(f"**Peso al Nacer:** {child.get('peso_nacer', '-')}")
                                st.markdown(f"**Vacunas al Día:** `{child.get('vacunas', '-')}`")
                                st.markdown(f"**Control Médico:** {child.get('control', '-')}")
                            with sub_c2:
                                st.markdown(f"**Comuna:** {child.get('comuna', '-')}")
                                st.markdown(f"**Dirección:** {child.get('direccion', '-')}")
                                st.markdown(f"**Previsión:** {child.get('prevision', '-')}")
                                st.markdown(f"**Alergias:** `{child.get('alergias', '-')}`")
                            with sub_c3:
                                st.markdown(f"**Tel. Madre:** `{child.get('telefono_madre', '-')}`")
                                st.markdown(f"**Tel. Padre:** `{child.get('telefono_padre', '-')}`")
                                st.markdown(f"**Suplentes:** {child.get('suplentes', '-')}")
                                st.markdown(f"**Ingreso:** `{fecha_ingreso_clean}`")
                                st.markdown(f"**Egreso:** `{fecha_egreso_clean}`")
                            
                            st.write("###")
                            st.markdown('<div class="ficha-seccion-datos">', unsafe_allow_html=True)
                            st.markdown(f":material/woman: **ANTECEDENTES DE LA MADRE:** \n{child.get('madre', '-')}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('<div class="ficha-seccion-datos">', unsafe_allow_html=True)
                            st.markdown(f":material/man: **ANTECEDENTES DEL PADRE:** \n{child.get('padre', '-')}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.write("###")
                            st.markdown("##### :material/description: ANTECEDENTES GENERALES E HISTORIA SOCIAL")
                            historia = child.get('historia_social')
                            if historia: st.info(historia)
                            else: st.caption("No se registran antecedentes sociales.")
                        
                        st.write("###")
                        col_hist1, col_hist2 = st.columns(2)
                        with col_hist1:
                            st.markdown("##### :material/inventory_2: HISTORIAL DE ENTREGAS RECIBIDAS")
                            if not df_entregas_global.empty:
                                string_busqueda_rut = f"RUT: {child['rut']}"
                                df_niño = df_entregas_global[df_entregas_global["observaciones"].astype(str).str.contains(string_busqueda_rut, na=False)].copy()
                                
                                if not df_niño.empty:
                                    df_niño["Fecha"] = df_niño["created_at"].dt.strftime("%d/%m/%Y")
                                    st.dataframe(df_niño[["Fecha", "producto", "cantidad"]].rename(columns={"producto": "Insumo", "cantidad": "Cant"}), use_container_width=True, hide_index=True)
                                else: st.caption("No registra entregas aún.")
                            else: st.caption("No registra entregas.")
                            
                        with col_hist2:
                            st.markdown("##### :material/monitor_weight: HISTORIAL DE PESO Y CONTROLES")
                            if not df_pesos_global.empty and 'rut' in df_pesos_global.columns:
                                df_pesos_niño = df_pesos_global[df_pesos_global["rut"] == child["rut"]].copy()
                                if not df_pesos_niño.empty:
                                    df_pesos_niño = df_pesos_niño.sort_values(by="fecha", ascending=False)
                                    df_pesos_niño["Fecha"] = df_pesos_niño["fecha"].dt.strftime("%d/%m/%Y")
                                    st.dataframe(df_pesos_niño[["Fecha", "peso", "responsable"]].rename(columns={"peso": "Peso Registrado", "responsable": "Atendió"}), use_container_width=True, hide_index=True)
                                else: st.caption("No registra controles de peso.")
                            else: st.caption("No registra controles de peso.")

        with tab_inactive:
            st.write("### Historial de Egresos Pasivos")
            try: egresados = supabase.table("beneficiarios").select("*").eq("estado", "Egresado").order("ficha").execute().data
            except Exception as e: st.error(f"Error: {e}"); st.stop()
                
            if not egresados: st.info("No se registran egresados.")
            else:
                col_search, col_export = st.columns([3, 1])
                with col_search:
                    busqueda_egresados = st.text_input("Buscar egresado(a) por Nombre o RUN:", placeholder="Ej: Juan Pérez o 12345678-9", key="search_egresados")
                
                if busqueda_egresados:
                    termino_eg = busqueda_egresados.lower()
                    egresados_filtrados = [e for e in egresados if termino_eg in e["nombre"].lower() or termino_eg in e["rut"].lower()]
                else:
                    egresados_filtrados = egresados

                with col_export:
                    st.write("###") 
                    df_eg = pd.DataFrame(egresados_filtrados)
                    if not df_eg.empty:
                        cols_rename = {
                            "ficha": "N° Ficha", "rut": "RUT", "nombre": "Nombre Completo",
                            "nacimiento": "Nacimiento", "sexo": "Sexo", "peso_nacer": "Peso Nacer",
                            "comuna": "Comuna", "direccion": "Dirección", "prevision": "Previsión",
                            "telefono_madre": "Tel. Madre", "telefono_padre": "Tel. Padre", "suplentes": "Suplentes",
                            "fecha_ingreso": "Ingreso", "fecha_egreso": "Egreso", "historia_social": "Historia Social"
                        }
                        exist_cols = {k: v for k, v in cols_rename.items() if k in df_eg.columns}
                        df_export = df_eg[list(exist_cols.keys())].rename(columns=exist_cols)
                        
                        buffer_eg = io.BytesIO()
                        with pd.ExcelWriter(buffer_eg, engine='openpyxl') as writer:
                            df_export.to_excel(writer, index=False, sheet_name='Niños Egresados')
                        
                        st.download_button(
                            label=":material/download: Exportar Egresados",
                            data=buffer_eg.getvalue(),
                            file_name=f"Egresados_GotaDeLeche_{datetime.now(CHILE_TZ).strftime('%d_%m_%Y')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            type="secondary"
                        )

                if not egresados_filtrados:
                    st.warning("No se encontraron fichas de egresados que coincidan con su búsqueda.")
                else:
                    for inactive_child in egresados_filtrados:
                        with st.expander(f":material/person_off: Egresado: {inactive_child['nombre']} (RUT: {inactive_child['rut']})"):
                            
                            with st.popover(":material/restore: Deshacer Egreso (Error)", use_container_width=True):
                                st.write("**Restaurar Ficha (Solo en caso de error)**")
                                st.caption("Esta opción es únicamente para corregir un egreso accidental. El niño(a) no debería reingresar si fue dado de alta formalmente.")
                                
                                ficha_original = inactive_child['ficha']
                                if ficha_original in fichas_disponibles:
                                    st.success(f"La ficha física original (**N° {ficha_original}**) sigue libre. Se le reasignará automáticamente.")
                                    ficha_a_restaurar = ficha_original
                                else:
                                    st.warning(f"La ficha original (**N° {ficha_original}**) ya fue ocupada por otro niño. Debe asignarle un cartón nuevo.")
                                    if not fichas_disponibles:
                                        st.error("No hay fichas físicas disponibles en este momento.")
                                        ficha_a_restaurar = None
                                    else:
                                        ficha_a_restaurar = st.selectbox("Seleccione ficha libre para restaurarlo:", fichas_disponibles, key=f"re_ficha_{inactive_child['rut']}")

                                if ficha_a_restaurar is not None:
                                    if st.button("Confirmar Restauración", key=f"btn_re_{inactive_child['rut']}", type="primary", use_container_width=True):
                                        with st.spinner("Restaurando ficha en el padrón..."): 
                                            try:
                                                supabase.table("beneficiarios").update({"estado": "Activo", "ficha": int(ficha_a_restaurar)}).eq("rut", inactive_child["rut"]).execute()
                                                supabase.table("historial").insert({"responsable": user["nombre"], "producto": "PADRÓN", "cantidad": 1, "tipo": "RESTAURACIÓN", "observaciones": f"Error corregido: RUT {inactive_child['rut']} restaurado en Ficha {ficha_a_restaurar}", "created_at": get_local_now()}).execute()
                                                st.toast("Ficha restaurada exitosamente.", icon="✅")
                                                time.sleep(1.5); st.rerun()
                                            except Exception as e: st.error(f"Error: {e}")
                            
                            st.write("---")
                            
                            fecha_ingreso_clean = clean_timestamp_to_date(inactive_child.get('fecha_ingreso', '-'))
                            fecha_egreso_clean = clean_timestamp_to_date(inactive_child.get('fecha_egreso', '-'))
                            
                            sub_c1, sub_c2, sub_c3 = st.columns(3)
                            with sub_c1:
                                st.markdown(f"**RUN:** `{inactive_child['rut']}`")
                                st.markdown(f"**Nacimiento:** {inactive_child.get('nacimiento', '-')}")
                                st.markdown(f"**Peso al Nacer:** {inactive_child.get('peso_nacer', '-')}")
                                st.markdown(f"**Vacunas al Día:** `{inactive_child.get('vacunas', '-')}`")
                                st.markdown(f"**Control Médico:** {inactive_child.get('control', '-')}")
                            with sub_c2:
                                st.markdown(f"**Comuna:** {inactive_child.get('comuna', '-')}")
                                st.markdown(f"**Dirección:** {inactive_child.get('direccion', '-')}")
                                st.markdown(f"**Previsión:** {inactive_child.get('prevision', '-')}")
                                st.markdown(f"**Alergias:** `{inactive_child.get('alergias', '-')}`")
                            with sub_c3:
                                st.markdown(f"**Tel. Madre:** `{inactive_child.get('telefono_madre', '-')}`")
                                st.markdown(f"**Tel. Padre:** `{inactive_child.get('telefono_padre', '-')}`")
                                st.markdown(f"**Suplentes:** {inactive_child.get('suplentes', '-')}")
                                st.markdown(f"**Ingreso:** `{fecha_ingreso_clean}`")
                                st.markdown(f"**Egreso:** `{fecha_egreso_clean}`")
                            
                            st.write("###")
                            st.markdown('<div class="ficha-seccion-datos">', unsafe_allow_html=True)
                            st.markdown(f":material/woman: **ANTECEDENTES DE LA MADRE:** \n{inactive_child.get('madre', '-')}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('<div class="ficha-seccion-datos">', unsafe_allow_html=True)
                            st.markdown(f":material/man: **ANTECEDENTES DEL PADRE:** \n{inactive_child.get('padre', '-')}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.write("###")
                            st.markdown("##### :material/description: ANTECEDENTES GENERALES E HISTORIA SOCIAL")
                            historia = inactive_child.get('historia_social')
                            if historia: st.info(historia)
                            else: st.caption("No se registran antecedentes sociales.")
                        
                            st.write("###")
                            col_hist1, col_hist2 = st.columns(2)
                            with col_hist1:
                                st.markdown("##### :material/inventory_2: HISTORIAL DE ENTREGAS RECIBIDAS")
                                if not df_entregas_global.empty:
                                    string_busqueda_rut = f"RUT: {inactive_child['rut']}"
                                    df_niño = df_entregas_global[df_entregas_global["observaciones"].astype(str).str.contains(string_busqueda_rut, na=False)].copy()
                                    
                                    if not df_niño.empty:
                                        df_niño["Fecha"] = df_niño["created_at"].dt.strftime("%d/%m/%Y")
                                        st.dataframe(df_niño[["Fecha", "producto", "cantidad"]].rename(columns={"producto": "Insumo", "cantidad": "Cant"}), use_container_width=True, hide_index=True)
                                    else: st.caption("No registra entregas aún.")
                                else: st.caption("No registra entregas.")
                                
                            with col_hist2:
                                st.markdown("##### :material/monitor_weight: HISTORIAL DE PESO Y CONTROLES")
                                if not df_pesos_global.empty and 'rut' in df_pesos_global.columns:
                                    df_pesos_niño = df_pesos_global[df_pesos_global["rut"] == inactive_child["rut"]].copy()
                                    if not df_pesos_niño.empty:
                                        df_pesos_niño = df_pesos_niño.sort_values(by="fecha", ascending=False)
                                        df_pesos_niño["Fecha"] = df_pesos_niño["fecha"].dt.strftime("%d/%m/%Y")
                                        st.dataframe(df_pesos_niño[["Fecha", "peso", "responsable"]].rename(columns={"peso": "Peso Registrado", "responsable": "Atendió"}), use_container_width=True, hide_index=True)
                                    else: st.caption("No registra controles de peso.")
                                else: st.caption("No registra controles de peso.")

    # 📜 PANEL: HISTORIAL
    elif menu_choice == ":material/manage_search: HISTORIAL":
        st.header(":material/manage_search: Historial de Operaciones", divider="blue")
        
        if "tipo_busqueda" not in st.session_state:
            st.session_state.tipo_busqueda = "Por Día específico"
        if "fecha_seleccionada" not in st.session_state:
            st.session_state.fecha_seleccionada = datetime.now(CHILE_TZ).date()

        tipo_busqueda = st.radio("¿Cómo desea buscar?", ["Por Mes completo", "Por Día específico"], 
                                 index=0 if st.session_state.tipo_busqueda == "Por Mes completo" else 1)
        st.session_state.tipo_busqueda = tipo_busqueda

        if tipo_busqueda == "Por Mes completo":
            col1, col2 = st.columns(2)
            meses = {
                "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
                "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
            }
            with col1: seleccion_mes = st.selectbox("Seleccione el MES:", list(meses.keys()), index=datetime.now(CHILE_TZ).month - 1)
            with col2: seleccion_anio = st.selectbox("Seleccione el AÑO:", [2026, 2025], index=0)
        else:
            fecha_dia = st.date_input("Seleccione el DÍA específico:", value=st.session_state.fecha_seleccionada, format="DD/MM/YYYY")
            st.session_state.fecha_seleccionada = fecha_dia

        try:
            with st.spinner("Consultando..."): 
                datos_historial = supabase.table("historial").select("*").order("id", desc=True).execute().data
        except Exception as e: 
            st.error(f"Error: {e}"); st.stop()
            
        if not datos_historial: 
            st.info("No hay movimientos registrados.")
        else:
            df = pd.DataFrame(datos_historial)
            
            df["dt"] = pd.to_datetime(df["created_at"], errors="coerce")
            df["dt"] = df["dt"].apply(lambda x: x.tz_localize('UTC').tz_convert(CHILE_TZ) if x.tzinfo is None else x.tz_convert(CHILE_TZ))
            df = df.dropna(subset=["dt"])
            
            if tipo_busqueda == "Por Mes completo":
                df_filtrado = df[(df["dt"].dt.month == meses[seleccion_mes]) & (df["dt"].dt.year == seleccion_anio)].copy()
                titulo_alerta = f"No hay registros para {seleccion_mes} de {seleccion_anio}."
            else:
                df_filtrado = df[df["dt"].dt.date == st.session_state.fecha_seleccionada].copy()
                titulo_alerta = f"No hay registros para el día {st.session_state.fecha_seleccionada.strftime('%d/%m/%Y')}."
            
            if df_filtrado.empty: 
                st.warning(titulo_alerta)
            else:
                df_filtrado["Fecha"] = df_filtrado["dt"].dt.strftime("%d/%m/%Y %H:%M")
                
                df_mostrar = df_filtrado[["Fecha", "tipo", "producto", "cantidad", "responsable", "observaciones"]].rename(columns={
                        "tipo": "Operación", 
                        "producto": "Insumo", 
                        "cantidad": "Cant.", 
                        "responsable": "Responsable", 
                        "observaciones": "Detalle"
                    })
                
                st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
                
                st.write("###")
                
                buffer_historial = io.BytesIO()
                with pd.ExcelWriter(buffer_historial, engine='openpyxl') as writer:
                    df_mostrar.to_excel(writer, index=False, sheet_name='Historial')
                
                st.download_button(
                    label=":material/download: Descargar Historial en Excel (.xlsx)",
                    data=buffer_historial.getvalue(),
                    file_name=f"Historial_Operaciones_{datetime.now(CHILE_TZ).strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

    # 🔐 PANEL DE ADMINISTRACIÓN
    elif menu_choice == ":material/security: PANEL ADMIN":
        st.header(":material/security: Panel de Administración de Usuarios", divider="blue")
        st.warning("⚠️ Zona de acceso restringido. Aquí puede gestionar las cuentas de las voluntarias y operadores del sistema.")
        
        try:
            res_users = supabase.table("usuarios").select("usuario, nombre").execute()
            df_users = pd.DataFrame(res_users.data)
        except Exception as e:
            st.error(f"Error al conectar con la base de datos: {e}")
            st.stop()
            
        st.write("### :material/group: Usuarios Actuales en el Sistema")
        if not df_users.empty:
            st.dataframe(df_users.rename(columns={"usuario": "Nombre de Usuario (Login)", "nombre": "Nombre Completo"}), hide_index=True, use_container_width=True)
        else:
            st.info("No hay usuarios registrados o no se pudo cargar la tabla.")
        
        st.write("---")
        
        tab_add, tab_edit, tab_del = st.tabs([":material/person_add: Crear Nueva Voluntaria", ":material/key: Actualizar Contraseña", ":material/person_remove: Eliminar Acceso"])
        
        with tab_add:
            with st.form("add_user_form"):
                st.markdown("##### Registrar nuevo operador")
                c1, c2 = st.columns(2)
                with c1: new_nombre = st.text_input("Nombre Completo")
                with c2: new_usuario = st.text_input("Nombre de Usuario (Para el Login)")
                
                new_pass = st.text_input("Asigne una Contraseña", type="password")
                
                if st.form_submit_button("Crear Usuario de Acceso", type="primary", use_container_width=True):
                    if not new_nombre or not new_usuario or not new_pass:
                        st.error("Por favor llene todos los campos para crear la cuenta.")
                    else:
                        with st.spinner("Encriptando credenciales y creando usuario..."):
                            try:
                                hashed_pw = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                                supabase.table("usuarios").insert({"nombre": new_nombre, "usuario": new_usuario, "clave": hashed_pw}).execute()
                                st.success(f"La cuenta de {new_nombre} ha sido creada con éxito.")
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al crear usuario (Verifique que el usuario no exista ya): {e}")
                        
        with tab_edit:
            with st.form("edit_user_form"):
                st.markdown("##### Cambiar clave de una voluntaria")
                if not df_users.empty:
                    edit_usuario = st.selectbox("Seleccione la cuenta que desea modificar", df_users['usuario'].tolist())
                else:
                    edit_usuario = None
                    st.warning("No hay usuarios cargados para editar.")
                    
                edit_pass = st.text_input("Escriba la nueva contraseña", type="password")
                
                if st.form_submit_button("Actualizar Contraseña de Seguridad", type="primary", use_container_width=True):
                    if not edit_usuario or not edit_pass:
                        st.error("Debe seleccionar un usuario e ingresar una contraseña válida.")
                    else:
                        with st.spinner("Actualizando seguridad..."):
                            try:
                                hashed_pw = bcrypt.hashpw(edit_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                                supabase.table("usuarios").update({"clave": hashed_pw}).eq("usuario", edit_usuario).execute()
                                st.success(f"Contraseña actualizada para el usuario: {edit_usuario}")
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al actualizar: {e}")
                        
        with tab_del:
            with st.form("del_user_form"):
                st.markdown("##### Revocar acceso al sistema")
                st.caption("Esta acción es irreversible y la persona ya no podrá iniciar sesión en Gota de Leche.")
                if not df_users.empty:
                    del_usuario = st.selectbox("Seleccionar cuenta a ELIMINAR", df_users['usuario'].tolist())
                else:
                    del_usuario = None
                    
                st.divider()
                st.markdown("**Seguridad**")
                admin_pass = st.text_input("Ingrese SU contraseña actual para confirmar esta acción", type="password")
                
                if st.form_submit_button(":material/warning: Eliminar Usuario Permanentemente", use_container_width=True):
                    if not del_usuario:
                        st.error("No hay un usuario seleccionado.")
                    elif del_usuario == user['usuario']:
                        st.error("Operación bloqueada: No puede eliminar su propia sesión mientras está activo.")
                    elif not admin_pass:
                        st.error("Debe ingresar su contraseña para autorizar el borrado.")
                    elif verify_password(admin_pass, user['clave']):
                        with st.spinner("Borrando registros de acceso..."):
                            try:
                                supabase.table("usuarios").delete().eq("usuario", del_usuario).execute()
                                st.toast(f"Usuario {del_usuario} ha sido eliminado.", icon="✅")
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error en la base de datos: {e}")
                    else:
                        st.error("❌ Contraseña de autorización incorrecta. Acción denegada.")
