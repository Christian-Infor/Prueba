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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Gota de Leche - Sistema Maestro",
    layout="wide",
    page_icon="🥛",
)

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 1.1rem !important; }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .stApp { animation: fadeIn 0.4s ease-out; }
    
    .centered-login {
        max-width: 450px;
        margin: 0 auto;
        text-align: center;
        padding-top: 10vh;
    }
    .stForm {
        background-color: #1E293B !important;
        border: 3px solid #3B82F6 !important;
        border-radius: 20px !important;
        padding: 2.5rem !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5) !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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

def export_pdf_component(child_data):
    html_content = f"""
    <div id="pdf-container" style="font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; padding: 0; background: #ffffff; max-width: 820px; margin: auto; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden;">
        
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 35px 40px; color: white; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 0.5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">🥛 GOTA DE LECHE</h1>
                <p style="margin: 6px 0 0 0; color: #bfdbfe; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px;">Ficha Oficial del Beneficiario</p>
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
                    <div><span style="color: #64748b; font-weight: 500;">Nombre Completo:</span> <br><strong style="color: #0f172a; font-size: 15px;">{child_data.get('nombre', '-')}</strong></div>
                    <div><span style="color: #64748b; font-weight: 500;">RUN / Identificación:</span> <br><strong style="color: #0f172a;">{child_data.get('rut', '-')}</strong></div>
                    <div><span style="color: #64748b; font-weight: 500;">Fecha de Nacimiento:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('nacimiento', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Sexo:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('sexo', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Peso al Nacer:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('peso_nacer', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Vacunas al Día:</span> <br><span style="color: #334155; font-weight: 600;">{child_data.get('vacunas', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Último Control Médico:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('ultimo_control', '-')}</span></div>
                    <div>&nbsp;</div>
                    <div><span style="color: #64748b; font-weight: 500;">Fecha Ingreso Programa:</span> <br><span style="color: #16a34a; font-weight: bold;">{child_data.get('fecha_ingreso', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Fecha Estimada Egreso (2 años):</span> <br><span style="color: #dc2626; font-weight: bold;">{child_data.get('fecha_egreso', '-')}</span></div>
                </div>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 25px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #3b82f6; padding-bottom: 6px;">
                    <span style="font-size: 18px; margin-right: 8px;">🏠</span>
                    <h3 style="margin: 0; color: #1e3a8a; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px;">2. Contexto Familiar y Personas Autorizadas</h3>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 14px;">
                    <div><span style="color: #64748b; font-weight: 500;">Nombre de la Madre:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('madre', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Nombre del Padre:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('padre', '-')}</span></div>
                    <div style="grid-column: span 2;"><span style="color: #64748b; font-weight: 500;">Dirección Particular:</span> <br><span style="color: #334155; font-weight: 500;">{child_data.get('direccion', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Teléfono de Contacto:</span> <br><span style="color: #334155; font-weight: 600;">{child_data.get('telefono_madre', '-')}</span></div>
                    <div>&nbsp;</div>
                    <div><span style="color: #64748b; font-weight: 500;">Suplente Autorizado 1:</span> <br><span style="color: #475569;">{child_data.get('suplente_1', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Suplente Autorizado 2:</span> <br><span style="color: #475569;">{child_data.get('suplente_2', '-')}</span></div>
                    <div><span style="color: #64748b; font-weight: 500;">Suplente Autorizado 3 (Cuarto):</span> <br><span style="color: #475569;">{child_data.get('suplente_3', '-')}</span></div>
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
# 4. LOGIN CLÁSICO CENTRADO
# ─────────────────────────────────────────
if "user" not in st.session_state:
    st.markdown("<style>section[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown('<div class="centered-login">', unsafe_allow_html=True)
        st.markdown("<h1 style='color:#60A5FA; font-size:3.5rem; margin-bottom:10px;'>🥛 GOTA DE LECHE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#94A3B8; margin-bottom:30px;'>Sistema Maestro de Gestión</p>", unsafe_allow_html=True)
        with st.form("login"):
            username = st.text_input("Usuario", placeholder="👤 Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="🔒 Ingrese su contraseña")
            if st.form_submit_button("INGRESAR AL SISTEMA 🚀", use_container_width=True):
                if not username or not password:
                    st.error("Ingrese usuario y contraseña.")
                else:
                    try:
                        res = supabase.table("usuarios").select("*").eq("usuario", username).execute()
                        if res.data and verify_password(password, res.data[0]["clave"]):
                            st.session_state.user = res.data[0]
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas.")
                    except Exception as e:
                        st.error(f"Error al verificar credenciales: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 5. PANEL PRINCIPAL (SESIÓN ACTIVA)
# ─────────────────────────────────────────
else:
    user = st.session_state.user
    MAX_FICHAS = 210
    
    with st.sidebar:
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
                stock_res = supabase.table("stock").select("*").execute()
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
            
            # INFO INMEDIATA: TRASLADADA DESDE SALA DE PESO
            st.write("###")
            st.markdown("### 🚨 Estado Crítico de Insumos (Sala de Atención)")
            cols_sala = st.columns(4)
            for i, item in enumerate(stock_res.data):
                with cols_sala[i % 4]:
                    if item["sala"] <= 5:
                        badge = f'<span style="background-color: #ef4444; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">🚨 CRÍTICO: {item["sala"]} ud.</span>'
                    elif item["sala"] <= 15:
                        badge = f'<span style="background-color: #f59e0b; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">⚠️ BAJO: {item["sala"]} ud.</span>'
                    else:
                        badge = f'<span style="background-color: #10b981; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">📦 OK: {item["sala"]} ud.</span>'
                    
                    st.markdown(f"""
                        <div class="metric-card" style="margin-bottom: 10px; border-top: 4px solid #3b82f6; padding:15px;">
                            <div style="font-size:0.95rem; color: #f8fafc; font-weight:600; min-height:30px;">{item['producto']}</div>
                            <div style="margin-top: 10px;">{badge}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.write("###")
            fig = px.bar(
                df, x="producto", y="sala", text="sala",
                title="Distribución de Stock Disponible en Sala de Atención",
                labels={"sala": "Unidades", "producto": "Insumo"},
                template="plotly_dark"
            )
            fig.update_traces(marker_color='#38bdf8', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

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

    # ⚖️ PANEL: SALA DE ATENCIÓN (UNIFICADO)
    elif menu_choice == "⚖️ SALA DE ATENCIÓN":
        st.header("⚖️ Sala de Atención - Despacho y Control", divider="blue")
        
        tab_entrega, tab_resumen_stock = st.tabs(["📝 CONTROL DE ENTREGA (REGISTRAR)", "📊 RESUMEN DE INGRESOS Y SALIDAS"])
        
        try:
            stock_data = supabase.table("stock").select("*").order("producto").execute().data
        except Exception as e:
            st.error(f"Error de stock: {e}"); st.stop()
            
        with tab_entrega:
            metodo_busqueda = st.radio("Buscar beneficiario por:", ["N° de Ficha 📋", "RUN / Identificación 🪪"], horizontal=True)
            
            # Variables de control vacías
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
            
            # Si se encontró un beneficiario, armamos su lista independiente de receptores
            if beneficiary:
                recipient_name = beneficiary["nombre"]
                ficha_vinculada = beneficiary["ficha"]
                
                # Armamos las opciones basadas estrictamente en su ficha
                opciones_retiro = []
                if beneficiary.get("madre"): opciones_retiro.append(f"Madre: {beneficiary['madre']}")
                if beneficiary.get("padre"): opciones_retiro.append(f"Padre: {beneficiary['padre']}")
                if beneficiary.get("suplente_1"): opciones_retiro.append(f"Suplente 1: {beneficiary['suplente_1']}")
                if beneficiary.get("suplente_2"): opciones_retiro.append(f"Suplente 2: {beneficiary['suplente_2']}")
                if beneficiary.get("suplente_3"): opciones_retiro.append(f"Suplente 3 (Cuarto): {beneficiary['suplente_3']}")
                opciones_retiro.append("Otro Suplente (No registrado)")
                
                st.success(f"**Beneficiario:** {recipient_name} | **Ficha:** {ficha_vinculada} | **Último Control:** {beneficiary.get('ultimo_control','-')}", icon="👶")

            st.write("###")
            product_options = ["--"] + [x["producto"] for x in stock_data]
            
            with st.form("delivery_master_form"):
                st.markdown("##### 📦 Desglose Obligatorio de Insumos (Se deben registrar exactamente 3 ítems)")
                
                # Forzamos exactamente 3 ítems visuales en pantalla
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
                    # Validación estricta: los 3 campos son obligatorios
                    items_validados = [(prod_1, qty_1), (prod_2, qty_2), (prod_3, qty_3)]
                    any_empty = any(p == "--" or q <= 0 for p, q in items_validados)
                    
                    if ficha_vinculada == 0:
                        st.error("Operación abortada: Debe identificar primero a un beneficiario activo mediante Ficha o RUN.")
                    elif any_empty:
                        st.error("❌ ERROR DE CAMPO OBLIGATORIO: Las voluntarias deben registrar obligatoriamente los 3 ítems de insumos con cantidades mayores a cero para poder convalidar la entrega.")
                    elif not nombre_firma_especifico:
                        st.error("❌ ERROR DE CAMPO OBLIGATORIO: Debe ingresar el nombre completo de la persona que recibe físicamente.")
                    else:
                        errors_stock = []
                        for p_name, qty in items_validados:
                            item = next((x for x in stock_data if x["producto"] == p_name), None)
                            if not item:
                                errors_stock.append(f"El producto '{p_name}' no existe en el catálogo.")
                            elif item["sala"] < qty:
                                errors_stock.append(f"Falta Stock para '{p_name}'. En sala: {item['sala']} | Solicitado: {qty}.")
                                
                        if errors_stock:
                            for err in errors_stock: st.error(err)
                        else:
                            try:
                                detalle_receptor = f"{quien_retira_tipo} (Recibe: {nombre_firma_especifico})"
                                for p_name, qty in items_validados:
                                    item = next(x for x in stock_data if x["producto"] == p_name)
                                    # Descuento explícito en INT nativo
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
            st.caption("Balance total de cuánto ha recibido la sala (traslados) versus cuánto ha entregado a beneficiarios.")
            
            try:
                historial_completo = supabase.table("historial").select("*").execute().data
                df_h = pd.DataFrame(historial_completo) if historial_completo else pd.DataFrame()
            except:
                df_h = pd.DataFrame()
                
            if df_h.empty:
                st.info("No hay transacciones registradas para computar resúmenes.")
            else:
                resumen_productos = []
                for p in stock_data:
                    p_name = p["producto"]
                    
                    # Sumamos lo que ha entrado a sala (TRASLADO A SALA)
                    entradas = df_h[(df_h["producto"] == p_name) & (df_h["tipo"] == "TRASLADO A SALA")]["cantidad"].astype(int).sum()
                    # Sumamos lo que ha salido de sala (ENTREGA)
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
                    name = c1.text_input("Nombre Completo *")
                    rut = c2.text_input("RUN / Identificación *")
                    ficha = c3.number_input("N° Ficha Asignado", min_value=1, value=siguiente_ficha, step=1)
                    
                    cc1, cc2, cc3 = st.columns(3)
                    birth_date = cc1.text_input("Fecha Nacimiento (DD/MM/AAAA)")
                    sexo = cc2.selectbox("Sexo", ["Masculino", "Femenino"])
                    peso_nacer = cc3.text_input("Peso al Nacer (ej: 3.250 kg)")
                    
                    cx1, cx2 = st.columns(2)
                    vacunas = cx1.selectbox("¿Vacunas al Día?", ["Sí", "No"])
                    ultimo_control = cx2.text_input("Fecha de Último Control Médico (DD/MM/AAAA)")
                    
                    st.markdown("---")
                    st.markdown("##### 👥 Registro de Contactos e Independencia de Retiro")
                    ccc1, ccc2, ccc3 = st.columns(3)
                    mother = ccc1.text_input("Nombre de la Madre")
                    father = ccc2.text_input("Nombre del Padre")
                    phone = ccc3.text_input("Teléfono de Contacto")
                    
                    address = st.text_input("Dirección Particular")
                    
                    st.markdown("##### 🛡️ Suplentes Autorizados para Retiro")
                    cs1, cs2, cs3 = st.columns(3)
                    suplente_1 = cs1.text_input("Suplente Autorizado 1")
                    suplente_2 = cs2.text_input("Suplente Autorizado 2")
                    suplente_3 = cs3.text_input("Suplente Autorizado 3 (Cuarto Suplente)")
                    
                    social_history = st.text_area("Antecedentes Importantes / Historia Social")
                    
                    if st.form_submit_button("INGRESAR BENEFICIARIO AL SISTEMA", type="primary"):
                        if not name or not rut:
                            st.error("Campos obligatorios faltantes: Nombre y RUN son requeridos.")
                        else:
                            try:
                                # Cálculo automático de egreso a 2 años aproximados
                                f_ingreso_dt = datetime.now(CHILE_TZ)
                                f_egreso_dt = f_ingreso_dt + timedelta(days=730) # 2 años app
                                
                                string_ingreso = f_ingreso_dt.strftime("%d/%m/%Y")
                                string_egreso = f_egreso_dt.strftime("%d/%m/%Y")
                                
                                check_ficha = supabase.table("beneficiarios").select("ficha, nombre").eq("ficha", ficha).execute()
                                if check_ficha.data:
                                    st.error(f"Conflicto: El N° de ficha {ficha} ya está asignado a: {check_ficha.data[0]['nombre']}")
                                else:
                                    supabase.table("beneficiarios").insert({
                                        "nombre": name, "rut": rut, "ficha": ficha, "nacimiento": birth_date,
                                        "sexo": sexo, "peso_nacer": peso_nacer, "vacunas": vacunas, "ultimo_control": ultimo_control,
                                        "telefono_madre": phone, "direccion": address, "madre": mother, "padre": father,
                                        "suplente_1": suplente_1, "suplente_2": suplente_2, "suplente_3": suplente_3,
                                        "historia_social": social_history, "estado": "Activo",
                                        "fecha_ingreso": string_ingreso, "fecha_egreso": string_egreso
                                    }).execute()
                                    st.success("Registro clínico-social creado exitosamente con egreso estimado a 2 años.")
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
                    
                    btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 4])
                    with btn_col1:
                        if st.button(f"📄 Descargar Ficha PDF", key=f"pdf_{child['ficha']}", use_container_width=True):
                            st.session_state.pdf_trigger = child
                            st.rerun()
                    with btn_col2:
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
                    
                    sub_c1, sub_c2 = st.columns(2)
                    with sub_c1:
                        st.markdown(f"**RUN:** `{child['rut']}`")
                        st.markdown(f"**Fecha Nacimiento:** {child.get('nacimiento', '-')}")
                        st.markdown(f"**Peso al Nacer:** {child.get('peso_nacer', '-')}")
                        st.markdown(f"**Vacunas al Día:** `{child.get('vacunas', '-')}`")
                        st.markdown(f"**Último Control Médico:** {child.get('ultimo_control', '-')}")
                        st.markdown(f"**Dirección:** {child.get('direccion', '-')}")
                    with sub_c2:
                        st.markdown(f"**Madre:** {child.get('madre', '-')} | **Padre:** {child.get('padre', '-')}")
                        st.markdown(f"**Teléfono:** {child.get('telefono_madre', '-')}")
                        st.markdown(f"**Fecha Ingreso:** `{child.get('fecha_ingreso', '-')}`")
                        st.markdown(f"**Egreso Estimado (2 años):** `{child.get('fecha_egreso', '-')}`")
                        st.markdown(f"**Suplentes:** 1: {child.get('suplente_1','-')} | 2: {child.get('suplente_2','-')} | 3: {child.get('suplente_3','-')}")
                    
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

    # 📜 PANEL: HISTORIAL (BÚSQUEDA POR FECHA Y FILTROS)
    elif menu_choice == "📜 HISTORIAL":
        st.header("📜 Historial de Operaciones y Movimientos", divider="blue")
        
        # FILTRO AVANZADO DE BÚSQUEDA POR RANGO DE FECHAS
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
            
            # Filtrado por rango de fecha seleccionado por la voluntaria
            df_historial_general = df_historial_general[
                (df_historial_general["created_at_dt"].dt.date >= fecha_inicio) & 
                (df_historial_general["created_at_dt"].dt.date <= fecha_fin)
            ]
            
            df_historial_general["Fecha y Hora ⏰"] = df_historial_general["created_at_dt"].dt.strftime("%d/%m/%Y %H:%M")
            
            tipos_disponibles = ["TODOS"] + list(df_historial_general["tipo"].unique()) if not df_historial_general.empty else ["TODOS"]
            filtro_tipo = st.selectbox("Filtrar por tipo de operación:", tipos_disponibles)
            
            if filtro_tipo != "TODOS" and not df_historial_general.empty:
                df_filtrado = df_historial_general[df_historial_general["tipo"] == filtro_tipo]
            else:
                df_filtrado = df_historial_general
            
            if df_filtrado.empty:
                st.warning("No se encontraron registros bajo el rango de fechas u operación seleccionado.")
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