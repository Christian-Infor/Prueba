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
    page_icon=LOGO_SRC, 
)

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 1.1rem !important; }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .stApp { animation: fadeIn 0.4s ease-out; }
    
    /* ── CORRECCIÓN CRÍTICA PARA EL LOGIN (DISEÑO FASE 2) ── */
    /* Encapsula toda la pantalla de login cuando no se ha iniciado sesión */
    .stAppHasSidebar[data-sidebar-visible="false"], 
    .stApp:not(:has(div[data-testid="stSidebar"])) [data-testid="stVerticalBlock"] > div:has(.login-card) {
        background-color: #060b13 !important;
    }
    
    /* Contenedor principal de la tarjeta translúcida */
    .login-card {
        background: rgba(13, 22, 41, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 40px 35px !important;
        max-width: 450px !important;
        margin: 8vh auto 0 auto !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5) !important;
        text-align: center;
    }

    /* Forzar a los inputs de Streamlit que siguen a la tarjeta a meterse visualmente dentro del diseño */
    .stApp:not(:has(div[data-testid="stSidebar"])) .stTextInput,
    .stApp:not(:has(div[data-testid="stSidebar"])) .stButton {
        max-width: 380px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Cajas de texto integradas al fondo oscuro */
    .stTextInput div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput div[data-baseweb="input"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }
    .stTextInput label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        text-align: left !important;
        display: block !important;
    }

    /* Botón de ingreso moderno con degradado azul */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        transition: transform 0.1s ease, opacity 0.2s ease !important;
        width: 100% !important;
        margin-top: 10px;
    }
    .stButton > button[kind="primary"]:hover {
        opacity: 0.95 !important;
        transform: translateY(-1px);
    }
    
    /* Modelo de Tarjeta Unificado de tu Dashboard */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
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
    }
    
    /* Bloques de ficha detallados estilo formulario impreso */
    .ficha-seccion-datos {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
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
        st.error(f"Falta la credencial en Secrets: {e}")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        st.stop()

supabase = init_supabase()

# ─────────────────────────────────────────
# 4. LOGIN MEJORADO (DISEÑO GLASSMORPHISM PERFECTO)
# ─────────────────────────────────────────
if "user" not in st.session_state:
    st.markdown("<style>section[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    
    # Abrimos la tarjeta translúcida centralizada
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Logo oficial centrado y destacado
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-bottom: 15px;">
            <img src="{LOGO_SRC}" style="
                height: 100px; 
                object-fit: contain; 
                mix-blend-mode: screen; 
                filter: brightness(1.4) drop-shadow(0px 4px 12px rgba(96, 165, 250, 0.35));
            ">
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='color: white; margin-bottom: 4px; font-weight: 700; font-size: 1.75rem; letter-spacing: 0.5px;'>Iniciar Sesión</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 24px;'>Introduce tus credenciales para acceder</p>", unsafe_allow_html=True)
    
    # Cerramos el contenedor HTML para que los inputs nativos fluyan ordenados por el CSS superior
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Campos utilizando claves nativas e interfaz integrada
    username = st.text_input("Usuario", placeholder="Ej: admin", label_visibility="visible")
    password = st.text_input("Contraseña", type="password", placeholder="••••••••", label_visibility="visible")
    
    if st.button("Ingresar al Sistema 🚀", type="primary"):
        if not username or not password:
            st.error("⚠️ Por favor, ingresa tu usuario y contraseña.")
        else:
            try:
                res = supabase.table("usuarios").select("*").eq("usuario", username).execute()
                if res.data and verify_password(password, res.data[0]["clave"]):
                    st.session_state.user = res.data[0]
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
            except Exception as e:
                st.error(f"Error al verificar credenciales: {e}")

# ─────────────────────────────────────────
# 5. PANEL PRINCIPAL (SESIÓN ACTIVA)
# ─────────────────────────────────────────
else:
    user = st.session_state.user
    MAX_FICHAS = 210
    
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center; margin-bottom:10px;">
                <img src="{LOGO_SRC}" style="height:65px; object-fit:contain; mix-blend-mode:screen; filter:brightness(1.3);">
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"### 👤 {user['nombre']}")
        st.caption(f"Operador autorizado")
        st.divider()
        
        menu_choice = st.radio(
            "MENÚ PRINCIPAL", 
            [
                "📊 DASHBOARD",
                "📦 BODEGA CENTRAL",
                "⚖️ SALA DE ATENCIÓN",
                "👥 GESTIÓN DE NIÑOS",
                "📜 HISTORIAL",
            ],
            label_visibility="collapsed"
        )
        
        st.divider()
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

    # 📊 PANEL: DASHBOARD
    if menu_choice == "📊 DASHBOARD":
        st.header("📊 Resumen de Operación e Info Inmediata", divider="blue")
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
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Niños Activos</div><div class="metric-value">{niños_activos} <span style="font-size:1.1rem; color:#94a3b8;">/ {MAX_FICHAS}</span></div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Fichas Disponibles</div><div class="metric-value" style="color:#10b981;">{fichas_disponibles}</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Total en Sala</div><div class="metric-value">{int(df["sala"].sum())} <span style="font-size:1.1rem; color:#94a3b8;">unid</span></div></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Bodega Central</div><div class="metric-value">{int(df["bodega"].sum())} <span style="font-size:1.1rem; color:#94a3b8;">unid</span></div></div>', unsafe_allow_html=True)
            
            productos_filtrados = [item for item in stock_res.data if item["producto"].upper() not in ["AJUAR", "OTROS"]]
            
            st.write("###")
            st.markdown("### 📦 Stock de Bodega")
            cols_bodega = st.columns(3)
            for i, item in enumerate(productos_filtrados):
                with cols_bodega[i % 3]:
                    if item["bodega"] <= 15:
                        color_valor = "#ef4444"
                        sub_label = '<span style="color:#ef4444; font-weight:bold; font-size:0.9rem;">🚨 CRÍTICO EN BODEGA</span>'
                    elif item["bodega"] <= 40:
                        color_valor = "#f59e0b"
                        sub_label = '<span style="color:#f59e0b; font-weight:bold; font-size:0.9rem;">⚠️ INVENTARIO GLOBAL BAJO</span>'
                    else:
                        color_valor = "#60a5fa"
                        sub_label = '<span style="color:#10b981; font-weight:bold; font-size:0.9rem;">🏢 ALMACENADO</span>'
                        
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label" style="font-size:1rem; min-height:40px; display:flex; align-items:center; justify-content:center;">
                                {item['producto']}
                            </div>
                            <div class="metric-value" style="color: {color_valor};">
                                {int(item['bodega'])} <span style="font-size:1.2rem; color:#94a3b8;">ud</span>
                            </div>
                            <div style="margin-top:10px;">
                                {sub_label}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            st.write("###")
            st.markdown("### ⚖️ Insumos Sala de Atención")
            cols_sala = st.columns(3)
            for i, item in enumerate(productos_filtrados):
                with cols_sala[i % 3]:
                    if item["sala"] <= 5:
                        color_valor = "#ef4444"
                        sub_label = '<span style="color:#ef4444; font-weight:bold; font-size:0.9rem;">🚨 CRÍTICO</span>'
                    elif item["sala"] <= 15:
                        color_valor = "#f59e0b"
                        sub_label = '<span style="color:#f59e0b; font-weight:bold; font-size:0.9rem;">⚠️ INVENTARIO BAJO</span>'
                    else:
                        color_valor = "#10b981"
                        sub_label = '<span style="color:#10b981; font-weight:bold; font-size:0.9rem;">📦 STOCK ESTABLE</span>'
                    
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label" style="font-size:1rem; min-height:40px; display:flex; align-items:center; justify-content:center;">
                                {item['producto']}
                            </div>
                            <div class="metric-value" style="color: {color_valor};">
                                {int(item['sala'])} <span style="font-size:1.2rem; color:#94a3b8;">ud</span>
                            </div>
                            <div style="margin-top:10px;">
                                {sub_label}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    # 📦 PANEL: BODEGA CENTRAL
    elif menu_choice == "📦 BODEGA CENTRAL":
        st.header("📦 Gestión e Inventario General", divider="blue")
        try:
            raw = supabase.table("stock").select("*").order("id").execute().data
        except Exception as e:
            st.error(f"Fallo al recuperar stock: {e}"); st.stop()
            
        df_inventory = pd.DataFrame(raw)
        st.write("### Niveles Actuales de Existencias")
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
                            st.error(f"Error crítico en la transacción: {e}")

    # ⚖️ PANEL: SALA DE ATENCIÓN
    elif menu_choice == "⚖️ SALA DE ATENCIÓN":
        st.header("⚖️ Sala de Atención - Despacho y Control", divider="blue")
        
        tab_entrega, tab_resumen_stock = st.tabs(["📝 CONTROL DE ENTREGA (REGISTRAR)", "📊 RESUMEN DE INGRESOS Y SALIDAS"])
        
        try:
            stock_data = supabase.table("stock").select("*").order("producto").execute().data
        except Exception as e:
            st.error(f"Error de stock: {e}"); st.stop()
            
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
                                st.error(f"Error crítico guardando la entrega: {e}")
                                
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
    elif menu_choice == "👥 GESTIÓN DE NIÑOS":
        st.header("👥 Padrón de Beneficiarios", divider="blue")
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
                                st.error(f"Fallo en inserción: {e}")
                                
            try:
                children = supabase.table("beneficiarios").select("*").eq("estado", "Activo").order("ficha").execute().data
            except Exception as e:
                st.error(f"Error cargando padrón: {e}"); st.stop()
                
            st.write("### Fichas Clínicas en Sistema")
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
                                st.error(f"Error al egresar: {e}")
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
                                        st.error(f"Error al actualizar la base de datos: {e}")
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
            st.write("### Historial de Egresos Pasivos")
            try:
                egresados = supabase.table("beneficiarios").select("*").eq("estado", "Egresado").order("ficha").execute().data
            except Exception as e:
                st.error(f"Error: {e}"); st.stop()
                
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
                                st.error(f"Error: {e}")

    # 📜 PANEL: HISTORIAL
    elif menu_choice == "📜 HISTORIAL":
        st.header("📜 Historial de Operaciones y Movimientos", divider="blue")
        
        st.markdown("##### 🔍 Búsqueda Avanzada por Filtros de Fecha")
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            fecha_inicio = st.date_input("Fecha Inicial de Búsqueda", value=datetime.now(CHILE_TZ) - timedelta(days=30))
        with c_f2:
            fecha_fin = st.date_input("Fecha Final de Búsqueda", value=datetime.now(CHILE_TZ))
            
        try:
            with st.spinner("Consultando registros..."):
                datos_historial = supabase.table("historial").select("*").order("id", desc=True).execute().data
        except Exception as e:
            st.error(f"Fallo al conectar con el historial: {e}"); st.stop()
            
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
            filtro_tipo = st.selectbox("Filtrar por tipo de operation:", tipos_disponibles)
            
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
