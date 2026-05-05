import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database as db
import logic
import os 
import json
import streamlit as st
from datetime import datetime
import streamlit as st
import io

# =========================================================
# CONTROL DE ACCESO (SEGURIDAD INICIAL)
# =========================================================
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def login():
    """Muestra la interfaz de inicio de sesión."""
    # Centramos el formulario con columnas
    _, col_center, _ = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.image('psiconefro.png', width=950) # Opcional: tu logo
            st.title("☀️ Buenos días")
            st.info("Ingrese sus credenciales para gestionar el servicio de Psiconefrología.")
            
            usuario_input = st.text_input("Usuario")
            clave_input = st.text_input("Contraseña", type="password")
            
            if st.button("INGRESAR AL SISTEMA", type="primary", use_container_width=True):
                # Validación de credenciales solicitadas
                if usuario_input == "psiconefro" and clave_input == "psiconefro_2026":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Verifique e intente de nuevo.")
        
        st.caption("Uso exclusivo para el personal del Hospital Ramiro Prialé Prialé.")

# --- LÓGICA DE BLOQUEO ---
if not st.session_state.autenticado:
    login()
    st.stop() # Detiene la ejecución del resto de la app si no está autenticado

# =========================================================
# CONFIGURACIÓN MAESTRA DE DISEÑO (ESTILO PINHOME/EDSMART)
# =========================================================
st.set_page_config(page_title="Psiconefrología Dashboard", layout="wide")

st.markdown("""
    <style>
    /* 1. Fondo general limpio */
    .stApp {
        background-color: #F4F7F6; /* Gris muy claro institucional */
    }

    # [Image: modern-dashboard-design-reference]
    
    /* 2. Barra Lateral (Sidebar) Estilo PinHome/EdSmart */
    [data-testid="stSidebar"] {
        background-color: #00796B; /* Azul-Verde profundo institucional */
        border-right: none;
        box-shadow: 4px 0 10px rgba(0,0,0,0.05);
    }
    
    /* Títulos y texto de Sidebar */
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
        font-family: 'Poppins', sans-serif;
    }

    /* Estilo para los ítems del menú lateral (radio buttons) */
    [data-testid="stSidebar"] .stRadio > div > label {
        color: rgba(255,255,255,0.85);
        padding: 10px 15px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background-color: rgba(255,255,255,0.1);
        color: white;
    }

    /* Ítem seleccionado en el Sidebar */
    [data-testid="stSidebar"] .stRadio > div > label[data-selected="true"] {
        background-color: #009688; /* Color de realce */
        color: white;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }

    /* 3. Contenedores de Contenido (Cards) Replicando tus modelos */
    /* Este CSS se aplica a todos los st.container(border=True) */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-1r6slb0, div[data-testid="stCard"] { 
        background-color: white !important;
        padding: 25px !important;
        border-radius: 20px !important; /* Esquinas muy redondeadas */
        box-shadow: 0 6px 18px rgba(0,0,0,0.04) !important; /* Sombra suave y profunda */
        border: 1px solid #E9EDF0 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .st-emotion-cache-12w0qpk:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.06) !important;
    }

    /* 4. Tipografía y Encabezados Modernos */
    h1, h2, h3 {
        color: #1A1A1A;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* 5. Inputs y Formularios Redondeados */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {
        border-radius: 12px !important;
        border: 1px solid #E0E0E0 !important;
        padding: 8px 12px;
    }

    /* 6. Botones estilo Dashboard Profesional */
    .stButton>button {
        border-radius: 12px;
        border: none;
        background-color: #00A896; /* Teal principal */
        color: white;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        padding: 10px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    .stButton>button:hover {
        background-color: #009688;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    
    /* Botones de eliminación (del historial) */
    .stButton[key*="hist_del"] > button {
        background-color: #FF6B6B !important; /* Rojo profesional */
    }

    /* 7. Tabs modernas como selectores horizontales */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #EEF2F5;
        padding: 8px;
        border-radius: 15px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px;
        color: #616161;
        font-weight: 600;
        padding: 10px 25px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #00A896 !important; /* Teal principal */
        color: white !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
st.set_page_config(page_title="Agenda Psiconefrología", layout="wide")
db.create_tables()

# --- FUNCIONES DE SOPORTE ---
def buscar_paciente(query):
    if not query: return None
    conn = db.get_connection()
    # Usamos try/except por si la tabla aún no existe o está vacía
    try:
        df = pd.read_sql_query(f"SELECT * FROM pacientes WHERE dni='{query}' OR apellidos LIKE '%{query}%'", conn)
    except:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

# =========================================================
# --- NAVEGACIÓN Y BÚSQUEDA GLOBAL (DISEÑO BLINDADO CLÍNICO) ---
# =========================================================

# 1. INYECCIÓN CSS MAESTRA (Asegura tipografía Poppins y diseño Navy-Glow)
st.markdown("""
    <style>
    /* 0. Importar fuente corporativa moderna */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* 1. Fondo general y Tipografía global */
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif !important; 
    }
    .stApp {
        background-color: #F4F7F6 !important; /* Gris claro institucional original */
    }

    /* 2. Barra Lateral (Sidebar) Estilo Teal */
    [data-testid="stSidebar"] {
        background-color: #00897B !important; /* Teal profundo y elegante */
        min-width: 250px !important; /* AUMENTADO para nombres largos en una línea */
        border-right: none !important;
    }
    
    /* Ocultar divisores y nav nativo */
    [data-testid="stSidebar"] hr { display: none; }
    [data-testid="stSidebarNav"] { display: none; }

    /* 3. DISEÑO DEL MENÚ (Ultra Redondeado - Píldoras) */
    /* Ocultar el círculo nativo del radio button */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child { 
        display: none !important; 
    }

    /* Botones de Menú NO seleccionados (Cajas simétricas completas) */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 14px 15px !important; /* Padding lateral reducido */
        border-radius: 50px !important; /* ULTRA REDONDEADO */
        margin-bottom: 12px !important;
        width: 94% !important; /* Ocupa más espacio horizontal */
        margin-left: 3% !important; /* Margen más pequeño para centrar */
        display: flex !important;
        align-items: center !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }

    /* Texto: Forzado a una sola línea */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500 !important;
        font-size: 20px !important;
        white-space: nowrap !important; /* CRUCIAL: Evita el salto de línea */
        overflow: hidden !important;
        text-overflow: ellipsis !important; /* Pone "..." si el nombre es extremadamente largo */
    }

    /* Hover en opciones */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        transform: translateY(-2px);
    }

    /* Opción SELECCIONADA (Blanco con texto Teal y Glow) */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-selected="true"] {
        background-color: #FFFFFF !important;
        border-color: #FFFFFF !important;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15) !important;
    }
    
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] p,
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-selected="true"] p {
        color: #00897B !important;
        font-weight: 700 !important;
    }

    /* --- ESTILO DEL BUSCADOR (CORREGIDO) --- */
[data-testid="stSidebar"] .stTextInput input {
    background-color: #FFFFFF !important; /* Fondo blanco para que resalte el texto negro */
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    color: #000000 !important; /* TEXTO NEGRO */
    border-radius: 50px !important; /* ULTRA REDONDEADO igual que los botones */
    padding: 12px 20px !important;
    width: 94% !important;
    margin-left: 3% !important;
    font-weight: 500 !important;
}

/* Cambiar también el color del placeholder (el texto de fondo) a gris oscuro */
[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: #7F8C8D !important;
}
""", unsafe_allow_html=True)

# 2. ENCABEZADO Institucional
st.sidebar.markdown("""
    <div style="padding: 20px 10px 30px 20px; display: flex; align-items: center; gap: 15px;">
        <div style="background-color: white; width: 45px; height: 45px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 22px;">
            🧠
        </div>
        <div>
            <div style="color: white; font-size: 22px; font-weight: 700; line-height: 1.1;">Psiconefrología</div>
            <div style="color: rgba(255,255,255,0.6); font-size: 11px; font-weight: 600;">HNRPP - EsSalud</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 3. BUSCADOR GLOBAL
busqueda_global = st.sidebar.text_input("Buscador", placeholder="🔍 DNI o Apellido...", label_visibility="collapsed")
p_df = buscar_paciente(busqueda_global) # Tu lógica de búsqueda se mantiene

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# 4. DEFINICIÓN DE LA VARIABLE 'modulo' (ESTA ES LA LÍNEA CRUCIAL ANTES DEL IF)
modulo = st.sidebar.radio(
    "Navegación", 
    [
        "📅 Agenda", 
        "📊 Registro de Atención", 
        "📋 Salas", 
        "📝 Ficha Virtual", 
        "📂 Historia Clínica", 
        "📈 Evolución", 
        "📊 Administración", 
        "📅 Informe Mensual",
        "⚙️ Mantenimiento"
    ], 
    label_visibility="collapsed"
)

# --- BOTÓN DE CERRAR SESIÓN ---
# Agregamos un divisor y un espacio para que el botón se vaya al fondo
st.sidebar.markdown("<br>" * 10, unsafe_allow_html=True) # Espaciador para bajar el botón
st.sidebar.divider()

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
    # Cambiamos el estado a falso y reseteamos la app
    st.session_state.autenticado = False
    st.rerun()

# 5. TARJETA INFERIOR (Status del Sistema)
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <div style="background-color: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); width: 90%; margin-left: 5%;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <div style="background-color: rgba(255, 255, 255, 0.2); width: 35px; height: 35px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;">
                🏥
            </div>
            <div>
                <div style="color: white; font-weight: 700; font-size: 13px;">Servicio Psicología</div>
                <div style="color: rgba(255,255,255,0.5); font-size: 11px;">Hemodiálisis / DIPAC</div>
            </div>
        </div>
        <div style="background-color: rgba(241, 196, 15, 0.2); color: #F1C40F; padding: 6px 12px; border-radius: 50px; font-weight: 700; font-size: 11px; text-align: center; border: 1px solid rgba(241, 196, 15, 0.3);">
            ● Conexión Estable
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# SECCIÓN: MODULO_AGENDA_Y_CALENDARIO (DASHBOARD REFINED)
# =========================================================
if modulo == "📅 Agenda":
    st.title("📅 Gestión de Citas y Calendario")
    
    # --- 1. ENCABEZADO DE ESTADO ---
    fecha_hoy = datetime.now().date()
    
    # CORRECCIÓN DE ERROR DE FECHA:
    # Usamos la clase date directamente para evitar el TypeError
    from datetime import date
    fecha_minima_nac = date(1920, 1, 1)

    with st.container(border=True):
        c_kpi1, c_kpi2 = st.columns([2, 1])
        with c_kpi1:
            st.markdown(f"### 🗓️ Panel del Día: <span style='color: #00A896;'>{fecha_hoy.strftime('%d de %B, %Y')}</span>", unsafe_allow_html=True)
        with c_kpi2:
            st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
            if st.button("🔄 Actualizar Vista", use_container_width=True):
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # AJUSTE DE ANCHO: Cambiamos la proporción a [1.8, 1] para un panel de registro más amplio
    col_registro, col_visualizacion = st.columns([1.8, 1], gap="large")

    # --- 2. COLUMNA DE REGISTRO / PROGRAMACIÓN (PANEL AMPLIADO) ---
    with col_registro:
        with st.container(border=True):
            st.subheader("📋 Programar Atención")
            
            if p_df is not None and not p_df.empty:
                paciente = p_df.iloc[0]
                st.markdown(f"""
                    <div style='background-color: #f0fdfa; padding: 15px; border-radius: 12px; border-left: 5px solid #00A896; margin-bottom: 20px;'>
                        <small style='color: #00A896; font-weight: bold;'>PACIENTE SELECCIONADO</small><br>
                        <span style='font-size: 18px; font-weight: 600;'>{paciente['nombres']} {paciente['apellidos']}</span><br>
                        <small style='color: #616161;'>DNI: {paciente['dni']}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                fecha_sel = st.date_input("Seleccione Fecha de Cita", datetime.now())
                tipo_sel = st.selectbox("Tipo de Atención", [
                    "Atención Psicológica", 
                    "Intervención Individual", 
                    "Intervención Familiar", 
                    "Evaluación Diagnóstica"
                ])
                
                if st.button("🚀 AGENDAR CITA", type="primary", use_container_width=True):
                    db.agendar_cita(paciente['dni'], fecha_sel, tipo_sel)
                    st.toast(f"Cita programada")
                    st.rerun()
            
            elif busqueda_global != "":
                st.markdown(f"""
                    <div style='text-align: center; padding: 20px; border: 1px dashed #BDC3C7; border-radius: 15px; margin-bottom: 15px;'>
                        <p style='color: #7F8C8D;'>El DNI <b>{busqueda_global}</b> no está registrado.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander("➕ Registro Rápido de Nuevo Paciente", expanded=True):
                    with st.form("quick_reg", clear_on_submit=False):
                        st.markdown("##### Datos Personales")
                        c_dni, c_nom, c_ape = st.columns([1.2, 2, 2])
                        with c_dni:
                            q_dni = st.text_input("DNI", value=busqueda_global if busqueda_global.isdigit() else "")
                        with c_nom:
                            q_nom = st.text_input("Nombres")
                        with c_ape:
                            q_ape = st.text_input("Apellidos", value="" if busqueda_global.isdigit() else busqueda_global)
                        
                        c_eda, c_sex, c_fnac = st.columns(3)
                        with c_eda:
                            q_eda = st.number_input("Edad", 0, 110)
                        with c_sex:
                            q_sex = st.selectbox("Sexo", ["M", "F"])
                        with c_fnac:
                            # Calendar corregido para alcanzar 100 años (1920 en adelante)
                            q_fnac = st.date_input(
                                "F. Nacimiento", 
                                value=fecha_hoy,
                                min_value=fecha_minima_nac,
                                max_value=fecha_hoy
                            )
                        
                        st.divider()
                        st.markdown("##### Datos Complementarios")
                        c_lug, c_civ, c_hij = st.columns(3)
                        with c_lug:
                            q_lug = st.text_input("Procedencia")
                        with c_civ:
                            q_civ = st.selectbox("Est. Civil", ["Soltero/a", "Casado/a", "Viudo/a", "Divorciado/a"])
                        with c_hij:
                            q_hij = st.number_input("Hijos", 0)
                        
                        c_ins, c_tra, c_ser = st.columns(3)
                        with c_ins:
                            q_ins = st.text_input("Instrucción")
                        with c_tra:
                            q_tra = st.text_input("Trabajo")
                        with c_ser:
                            q_ser = st.selectbox("Servicio", ["Hemodiálisis", "DIPAC", "ERCA"])
                        
                        q_dir = st.text_input("Dirección actual")
                        q_tel = st.text_input("Teléfono")
                        
                        if st.form_submit_button("✅ Guardar y Habilitar Agenda", use_container_width=True):
                            if q_dni and q_nom and q_ape:
                                # Se pasa str(q_fnac) para mantener compatibilidad con tu lógica de BD
                                if db.guardar_paciente(q_dni, q_nom, q_ape, q_eda, q_sex, str(q_fnac), 
                                                       q_lug, q_civ, q_hij, q_ins, q_tra, q_dir, q_tel, q_ser):
                                    st.success("Paciente registrado con éxito.")
                                    st.rerun()
                                else:
                                    st.error("Error: El DNI ya existe.")
                            else:
                                st.warning("Complete los campos obligatorios.")
            else:
                st.markdown("""
                    <div style='text-align: center; padding: 40px;'>
                        <h1 style='font-size: 40px; margin-bottom: 0;'>🔍</h1>
                        <p style='color: #7F8C8D;'>Busque un paciente en la barra lateral.</p>
                    </div>
                """, unsafe_allow_html=True)

    # --- 3. COLUMNA DE VISUALIZACIÓN ---
    with col_visualizacion:
        with st.container(border=True):
            st.subheader(f"📅 Citas para Hoy")
            st.caption(f"Listado: {fecha_hoy.strftime('%d/%m/%Y')}")
            
            conn = db.get_connection()
            query_sql = f"""
                SELECT p.dni as DNI, p.nombres || ' ' || p.apellidos as Paciente, 
                       a.tipo_cita as 'Tipo de Atención', a.estado as Estado
                FROM agenda a
                JOIN pacientes p ON a.dni_paciente = p.dni
                WHERE a.fecha = '{fecha_hoy}'
                ORDER BY a.id DESC
            """
            try:
                df_hoy = pd.read_sql_query(query_sql, conn)
                if not df_hoy.empty:
                    st.dataframe(
                        df_hoy, 
                        use_container_width=True, 
                        hide_index=True,
                        column_config={
                            "Estado": st.column_config.BadgeColumn(
                                "Estado",
                                options=["Pendiente", "Atendido"],
                                colors={"Pendiente": "orange", "Atendido": "green"}
                            )
                        }
                    )
                else:
                    st.info("Sin citas para hoy.")
            except:
                st.info("Error de conexión.")
            finally:
                conn.close()

# =========================================================
# SECCIÓN: MODULO_FICHA_VIRTUAL (REDISEÑO FINAL DASHBOARD)
# =========================================================
elif modulo == "📝 Ficha Virtual":
    st.title("📝 Gestión de Ficha Psicológica")
    st.markdown("<p style='color: #616161; margin-top: -15px;'>Unidad de Hemodiálisis & DIPAC - Hospital Ramiro Prialé Prialé</p>", unsafe_allow_html=True)
    
    if p_df is not None and not p_df.empty:
        p = p_df.iloc[0]
        
        # --- ENCABEZADO DE PACIENTE (ESTILO NAVBAR) ---
        with st.container(border=True):
            c_p1, c_p2 = st.columns([3, 1])
            with c_p1:
                st.markdown(f"### 👤 {p['nombres']} {p['apellidos']}")
                st.markdown(f"<span style='color: #00A896; font-weight: 600;'>DNI: {p['dni']}</span> | <span style='color: #616161;'>Servicio Actual: {p.get('servicio', 'N/A')}</span>", unsafe_allow_html=True)
            with c_p2:
                st.markdown("<div style='text-align: right; margin-top: 10px;'>", unsafe_allow_html=True)
                if st.session_state.get('pdf_generado') is not None:
                    st.download_button(
                        label="📥 DESCARGAR PDF",
                        data=bytes(st.session_state.pdf_generado),
                        file_name=st.session_state.nombre_archivo,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
                else:
                    st.button("📄 PDF Pendiente", disabled=True, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        if 'pdf_generado' not in st.session_state:
            st.session_state.pdf_generado = None
        if 'nombre_archivo' not in st.session_state:
            st.session_state.nombre_archivo = ""

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("ficha_essalud_hd_dipac", clear_on_submit=False):
            
            # --- CARD I: FILIACIÓN Y CLÍNICA ---
            with st.container(border=True):
                st.subheader("I. Datos de Filiación y Estado Clínico")
                
                # Campos de edición que cargan lo que ya existe en la base de datos
                st.markdown("##### 📝 Completar / Editar Datos de Filiación")
                c_f1, c_f2, c_f3 = st.columns(3)
                
                with c_f1:
                    # Usamos .get() por seguridad y value para que aparezca lo ya registrado
                    edit_lug = st.text_input("📍 Lugar/Procedencia", value=p.get('lugar', ''))
                    
                    # Lógica para el selectbox de Estado Civil
                    ops_civil = ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Conviviente", "N/R"]
                    current_civ = p.get('estado_civil', 'N/R')
                    idx_civ = ops_civil.index(current_civ) if current_civ in ops_civil else 5
                    edit_civ = st.selectbox("💍 Est. Civil", ops_civil, index=idx_civ)

                with c_f2:
                    edit_dir = st.text_input("🏠 Dirección", value=p.get('direccion', ''))
                    edit_ins = st.text_input("🎓 Instrucción", value=p.get('instruccion', ''))
                    edit_ser = st.text_input("🏥 Servicio", value=p.get('servicio', ''))

                with c_f3:
                    edit_tel = st.text_input("📞 Teléfono", value=p.get('telefono', ''))
                    edit_tra = st.text_input("💼 Trabajo", value=p.get('trabajo', ''))
                    
                # Botón para guardar cambios de filiación sin tener que llenar toda la ficha clínica
                if st.form_submit_button("💾 Guardar Cambios de Filiación", use_container_width=True):
                    if db.actualizar_filiacion_completa(p['dni'], edit_lug, edit_dir, edit_tel, edit_civ, edit_ins, edit_tra, edit_ser):
                        st.success("Datos de filiación actualizados en todo el sistema.")
                        st.rerun() # Esto refresca la app y verás los datos nuevos arriba
                    else:
                        st.error("No se pudo actualizar la información.")

                st.divider()

                # --- DATOS DEL ENCUENTRO ACTUAL (Lo que ya tenías) ---
                st.markdown("##### 🩺 Datos del Encuentro Actual")
                c1, c2, c3 = st.columns(3)
                with c1:
                    f_entrevista = st.date_input("🗓️ Fecha de Entrevista", datetime.now().date())
                    te_valor = st.text_input("⏳ Tiempo de Enfermedad (TE)")
                with c2:
                    modalidad = st.radio("🏥 Modalidad", ["HD", "DIPAC"], horizontal=True)
                    turno_te = st.text_input("🕒 Turno / TE")
                with c3:
                    acceso = st.selectbox("💉 Acceso", ["FAV", "CV"])
                    t_dialisis = st.text_input("🔄 T. en diálisis")

                st.markdown("<br>", unsafe_allow_html=True)
                c_ant1, c_ant2 = st.columns(2)
                ant_clinicos = c_ant1.text_area("🗒️ Antecedentes Clínicos", height=100)
                conciencia_enf = c_ant2.text_area("🧠 Conciencia de la enfermedad", height=100)

            # --- CARD II: ENTORNO FAMILIAR Y ADHERENCIA ---
            with st.container(border=True):
                st.subheader("II. Datos Complementarios y Sociales")
                st.markdown("**1. Composición Familiar:**")
                fam_cols = ["Nombre", "Edad", "Parentesco", "E. Civil", "Localización", "Ocupación", "Relación"]
                df_familia = st.data_editor(pd.DataFrame(columns=fam_cols), num_rows="dynamic", key="editor_familia", use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                c_din, c_rol = st.columns(2)
                with c_din:
                    dinamica = st.radio("2. Dinámica Familiar", ["Funcional", "Disfuncional"], horizontal=True)
                    # AGREGADO: Espacio para anotación de dinámica familiar
                    det_dinamica = st.text_area("Anotación sobre Dinámica Familiar", height=70, placeholder="Describa la situación familiar...")
                    educacion = st.text_area("4. Educación", height=80)
                with c_rol:
                    # AGREGADO: Nombre del responsable
                    nombre_cuidador = st.text_input("3. Nombre del Cuidador / Responsable")
                    rol_cuidador = st.multiselect("Rol del cuidador", ["Facilitador", "Barrera", "Sobrecarga"])
                    exp_laboral = st.text_area("5. Experiencia Laboral", height=80)
                
                st.divider()
                st.markdown("**📊 6. Escala de Adherencia (1 al 5)**")
                ca1, ca2, ca3, ca4 = st.columns(4)
                adh_s = ca1.select_slider("Asistencia", options=[1,2,3,4,5], value=3)
                adh_d = ca2.select_slider("Dieta", options=[1,2,3,4,5], value=3)
                adh_f = ca3.select_slider("Farma", options=[1,2,3,4,5], value=3)
                adh_h = ca4.select_slider("Higiene", options=[1,2,3,4,5], value=3)
                
                st.markdown("<br>", unsafe_allow_html=True)
                c_hid, c_hab = st.columns(2)
                hidrico = c_hid.radio("💧 Indicador hídrico", ["Compensado", "Edema"], horizontal=True)
                habitos = c_hab.multiselect("🚬 Hábitos nocivos", ["Tabaco", "Alcohol", "Sedentarismo", "Otros"])

            # --- CARD III: EXAMEN MENTAL ---
            with st.container(border=True):
                st.subheader("III. Examen Mental")
                st.markdown("<p style='font-size: 13px; color: #7F8C8D;'>Marque la casilla para cargar valores basales normales.</p>", unsafe_allow_html=True)
                if st.checkbox("Aplicar Plantilla de Examen Normal (LOTEP)"):
                    v_obs, v_afe, v_cog, v_vol = "Aliño adecuado.", "Eutímico.", "LOTEP.", "Conservada."
                else: v_obs = v_afe = v_cog = v_vol = ""

                m1, m2 = st.columns(2)
                obs = m1.text_area("1. Observaciones generales", value=v_obs, height=80)
                afe = m2.text_area("2. Estado afectivo y conductual", value=v_afe, height=80)
                cog = m1.text_area("3. Aspectos cognoscitivos", value=v_cog, height=80)
                vol = m2.text_area("4. Actividad Voluntaria", value=v_vol, height=80)

            # --- CARD IV & V: MONITOREO Y EVALUACIÓN ---
            with st.container(border=True):
                st.subheader("IV. Evaluación y V. Monitoreo")
                eval_p = st.multiselect("📂 Tests Aplicados:", ["FACES", "EAT", "CAEPO", "HADS", "Otros"])
                
                st.divider()
                st.markdown("#### V. Monitoreo Bio-conductual (Evolución S1-S9)")
                mon_data = {"Área": ["A (Afectivo)", "X (Ansioso)", "D (Adherencia)", "S (Sueño)"]}
                for i in range(1, 10): mon_data[f"S{i}"] = [0, 0, 0, 0]
                
                df_mon_edit = st.data_editor(pd.DataFrame(mon_data), hide_index=True, key="editor_monitoreo", use_container_width=True)

                with st.container():
                    df_plot = df_mon_edit.melt(id_vars='Área', var_name='Sesión', value_name='Puntaje')
                    fig = px.line(df_plot, x='Sesión', y='Puntaje', color='Área', markers=True,
                                 color_discrete_sequence=["#FF4B4B", "#1C83E1", "#00C781", "#FFAA00"])
                    fig.update_layout(yaxis_range=[-0.5, 10.5], height=350, margin=dict(t=20, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

            # --- CARD VI & VII: DIAGNÓSTICO E INTERVENCIÓN ---
            with st.container(border=True):
                st.subheader("VI. Diagnóstico y VII. Intervención")
                diag = st.text_area("📌 VI. Diagnóstico psicológico")
                c_int1, c_int2 = st.columns([1, 2])
                interv = c_int1.radio("🎯 VII. Intervención", ["Individual", "Grupal", "Familiar"])
                det_interv = c_int2.text_area("📝 Detalles de la estrategia")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾 FINALIZAR REGISTRO Y GENERAR EXPEDIENTE", use_container_width=True):
                # CORRECCIÓN: Se incluyen TODOS los campos en el diccionario de datos
                datos_ficha = {
                    "fecha_entrevista": str(f_entrevista),
                    "filiacion": {"modalidad": modalidad, "turno": turno_te, "t_dialisis": t_dialisis, "acceso": acceso, "te": te_valor},
                    "antecedentes": ant_clinicos,
                    "conciencia": conciencia_enf,
                    "familia": df_familia.to_dict(),
                    "dinamica": dinamica,
                    "det_dinamica": det_dinamica,
                    "nombre_cuidador": nombre_cuidador,
                    "rol_cuidador": rol_cuidador,
                    "educacion": educacion,
                    "exp_laboral": exp_laboral,
                    "adherencia": {"asistencia": adh_s, "dieta": adh_d, "farma": adh_f, "higiene": adh_h},
                    "hidrico": hidrico,
                    "habitos": habitos,
                    "examen_mental": {"obs": obs, "afe": afe, "cog": cog, "vol": vol},
                    "eval_p": eval_p,
                    "monitoreo": df_mon_edit.to_dict(),
                    "diagnostico": diag,
                    "intervencion": interv,
                    "det_interv": det_interv
                }
                
                db.guardar_ficha(p['dni'], f_entrevista, datos_ficha)
                img_path = f"temp_grafico_{p['dni']}.png"
                fig.write_image(img_path)
                st.session_state.pdf_generado = logic.generar_pdf_ficha(p, datos_ficha, img_path)
                st.session_state.nombre_archivo = f"Ficha_{p['dni']}.pdf"
                if os.path.exists(img_path): os.remove(img_path)
                st.success("Expediente guardado correctamente.")
                st.rerun()

    else:
        st.markdown("""
            <div style="text-align: center; padding: 100px; border: 2px dashed #E0E0E0; border-radius: 20px;">
                <h2 style="color: #BDC3C7;">📄</h2>
                <h4 style="color: #7F8C8D;">Buscador Global requerido</h4>
                <p style="color: #BDC3C7;">Seleccione un paciente en la barra lateral para habilitar la Ficha Virtual.</p>
            </div>
        """, unsafe_allow_html=True)

# =========================================================
# MÓDULO: 📋 HOJA DE RUTA / INTERVENCIÓN (DISEÑO REFINADO)
# =========================================================
elif modulo == "📋 Salas":
    st.title("📋 Hoja de Ruta y Mapa de Salas")
    
    # --- 1. CONFIGURACIÓN DE ESPACIO (Cards Superiores) ---
    with st.container(border=True):
        c_map1, c_map2, c_map3 = st.columns([1, 1, 1])
        with c_map1:
            dia_mapa = st.selectbox("📅 Día de Hemodiálisis", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"])
        with c_map2:
            turno_mapa = st.selectbox("🕒 Turno", [
                "07:00 am - 12:00 pm", "12:00 pm - 04:00 pm", "04:00 pm - 09:00 pm", 
                "09:00 pm - 01:00 am", "01:00 am - 06:00 am"
            ])
        with c_map3:
            sala_mapa = st.radio("🏥 Sala", ["Sala 1", "Sala 2"], horizontal=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. RENDERIZADO DEL MAPA DIGITAL ---
    st.subheader(f"📍 Gestión de Máquinas - {sala_mapa}")
    
    df_sala = db.obtener_mapa_sala(sala_mapa, turno_mapa, dia_mapa)
    camas_ocupadas = {row['cama']: (f"{row['nombres']} {row['apellidos']}", row['dni']) for _, row in df_sala.iterrows()}

    dni_actual = None
    seleccionado = "No seleccionado"

    # Envolvemos el mapa en una tarjeta blanca principal
    with st.container(border=True):
        cols_cama = st.columns(4)
        for i in range(1, 9):
            with cols_cama[(i-1) % 4]:
                with st.container(border=True): # Sub-card para cada máquina
                    if i in camas_ocupadas:
                        nombre_p, dni_p = camas_ocupadas[i]
                        # Botón de Selección Estilizado
                        if st.button(f"🛌 M-{i}\n{nombre_p}", key=f"sel_{i}", use_container_width=True, type="primary"):
                            st.session_state.dni_mapa = dni_p
                            st.session_state.nombre_mapa = f"{nombre_p} ({dni_p})"
                        
                        c_edit, c_del = st.columns(2)
                        if c_edit.button("🔄", key=f"edit_{i}", help="Cambiar paciente", use_container_width=True):
                            st.session_state.cama_a_asignar = i
                            st.rerun()
                        if c_del.button("🗑️", key=f"del_c_{i}", help="Quitar paciente", use_container_width=True):
                            db.quitar_paciente_cama(sala_mapa, i, turno_mapa, dia_mapa)
                            st.toast(f"Máquina {i} liberada")
                            st.rerun()
                    else:
                        st.markdown(f"<p style='text-align: center; color: #7F8C8D; margin-bottom: 5px;'><b>M-{i}</b></p>", unsafe_allow_html=True)
                        if st.button("➕ Asignar", key=f"add_{i}", use_container_width=True):
                            st.session_state.cama_a_asignar = i
                            st.rerun()

    # --- 3. LÓGICA DE ASIGNACIÓN (Card Flotante) ---
    if 'cama_a_asignar' in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"#### ⚙️ Configurar Máquina {st.session_state.cama_a_asignar}")
            dni_input = st.text_input("DNI del paciente:")
            ca1, ca2 = st.columns(2)
            if ca1.button("Guardar Cambios", type="primary", use_container_width=True):
                if dni_input:
                    db.asignar_paciente_cama(sala_mapa, st.session_state.cama_a_asignar, turno_mapa, dia_mapa, dni_input)
                    del st.session_state.cama_a_asignar
                    st.rerun()
            if ca2.button("Cancelar", use_container_width=True):
                del st.session_state.cama_a_asignar
                st.rerun()

    # --- 4. CARGA DE DATOS ---
    if 'dni_mapa' in st.session_state:
        dni_actual = st.session_state.dni_mapa
        seleccionado = st.session_state.nombre_mapa
    elif 'p_df' in locals() and p_df is not None and not p_df.empty:
        p_sel = p_df.iloc[0]
        dni_actual = p_sel['dni']
        seleccionado = f"{p_sel['nombres']} {p_sel['apellidos']} ({p_sel['dni']})"

    # --- 5. ÁREA DE TRABAJO (Dashboard Style) ---
    if dni_actual:
        st.markdown("<br>", unsafe_allow_html=True)
        # Encabezado de intervención estilo Perfil
        with st.container(border=True):
            st.markdown(f"### 🧑‍⚕️ Intervención: <span style='color: #00A896;'>{seleccionado}</span>", unsafe_allow_html=True)
        
        col_ficha, col_ruta = st.columns([1, 1], gap="large")

        with col_ficha:
            with st.container(border=True):
                st.subheader("📄 Resumen de Ficha")
                conn = db.get_connection()
                f_db = pd.read_sql_query(f"SELECT datos_json FROM fichas WHERE dni_paciente='{dni_actual}' ORDER BY id DESC LIMIT 1", conn)
                conn.close()

                if not f_db.empty:
                    try:
                        d = json.loads(f_db.iloc[0]['datos_json'])
                        with st.container(border=True):
                            st.write(f"**🩺 Diagnóstico:** {d.get('diagnostico', 'N/A')}")
                            st.write(f"**🧠 Conciencia:** {d.get('conciencia', 'N/A')}")
                        st.info(f"**📝 Antecedentes:** {d.get('antecedentes', 'N/A')}")
                        
                        st.markdown("**📈 Monitoreo de Adherencia**")
                        adh = d.get('adherencia', {})
                        m_c1, m_c2 = st.columns(2)
                        m_c1.metric("Asistencia", f"{adh.get('asistencia', 0)}/5")
                        m_c1.metric("Fármacos", f"{adh.get('farma', 0)}/5")
                        m_c2.metric("Dieta", f"{adh.get('dieta', 0)}/5")
                        m_c2.metric("Higiene", f"{adh.get('higiene', 0)}/5")
                    except: st.error("Error de lectura.")
                else: st.info("El paciente no tiene una ficha previa registrada.")

        with col_ruta:
            with st.container(border=True):
                st.subheader("✍️ Registro de Evolución")
                with st.form("form_ruta", clear_on_submit=True):
                    fecha_registro = st.date_input("Fecha de atención:", datetime.now().date())
                    tipo = st.selectbox("Tipo de Intervención", [
                        "Atención Psicológica", 
                        "Intervención Individual", 
                        "Intervención Familiar", 
                        "Evaluación Diagnóstica"
                    ])
                    obs = st.text_area("Notas clínicas:", height=200, placeholder="Escriba aquí la evolución...")
                    
                    if st.form_submit_button("✅ GUARDAR REGISTRO", use_container_width=True):
                        if obs:
                            db.guardar_actividad_ruta(dni_actual, fecha_registro, tipo, obs)
                            st.success(f"Atención registrada.")
                            st.rerun()
                        else: st.error("La nota no puede estar vacía.")

            # Mini-log de actividad hoy
            with st.container(border=True):
                st.markdown(f"**🕒 Registro del {fecha_registro}**")
                conn = db.get_connection()
                df_h = pd.read_sql_query(f"SELECT tipo_cita as Actividad, estado FROM agenda WHERE dni_paciente='{dni_actual}' AND fecha='{fecha_registro}'", conn)
                conn.close()
                if not df_h.empty:
                    st.dataframe(df_h, use_container_width=True, hide_index=True)
                else: st.caption("Sin registros hoy.")
    else:
        # Estado vacío estilizado
        st.markdown("""
            <div style="text-align: center; padding: 60px; background-color: white; border-radius: 20px; border: 1px dashed #BDC3C7;">
                <h2 style="color: #BDC3C7;">🛌</h2>
                <h4 style="color: #7F8C8D;">Seleccione una máquina ocupada para iniciar</h4>
            </div>
        """, unsafe_allow_html=True)

# =========================================================
# MÓDULO: 📂 HISTORIAL DEL PACIENTE (EXPEDIENTE INTEGRAL)
# =========================================================
elif modulo == "📂 Historia Clínica":
    st.title("📂 Expediente Clínico Integral")
    
    if 'p_df' in locals() and p_df is not None and not p_df.empty:
        p = p_df.iloc[0]
        dni_p = p['dni']
        
        # --- EXTRACCIÓN DE DATOS (Se movió arriba para alimentar el PDF) ---
        conn = db.get_connection()
        f_db = pd.read_sql_query(f"SELECT datos_json, fecha_entrevista FROM fichas WHERE dni_paciente='{dni_p}' ORDER BY id DESC LIMIT 1", conn)
        query_h = f"SELECT id, fecha, tipo_cita, observaciones FROM agenda WHERE dni_paciente='{dni_p}' AND estado='Atendido' ORDER BY fecha DESC"
        df_hist = pd.read_sql_query(query_h, conn)
        conn.close()

        # --- ENCABEZADO DE PERFIL ESTILO DASHBOARD ---
        with st.container(border=True):
            c_header1, c_header2 = st.columns([3, 1])
            with c_header1:
                st.markdown(f"## {p['nombres']} {p['apellidos']}")
                st.markdown(f"<p style='color: #00A896; font-size: 18px; font-weight: 600;'>DNI: {dni_p} | Servicio: {p.get('servicio', 'N/A')}</p>", unsafe_allow_html=True)
            with c_header2:
                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- LÓGICA FUNCIONAL DE EXPORTACIÓN PDF ---
                if not f_db.empty:
                    pdf_key = f"pdf_historial_{dni_p}"
                    
                    # 1. Si no se ha generado, mostramos el botón de preparar
                    if st.session_state.get(pdf_key) is None:
                        if st.button("📄 Preparar PDF", use_container_width=True):
                            with st.spinner("Procesando expediente..."):
                                datos_pdf = json.loads(f_db.iloc[0]['datos_json'])
                                
                                # Recreamos el gráfico silenciosamente para el PDF
                                df_mon_pdf = pd.DataFrame(datos_pdf.get('monitoreo', {}))
                                df_plot_pdf = df_mon_pdf.melt(id_vars='Área', var_name='Sesión', value_name='Puntaje')
                                fig_pdf = px.line(df_plot_pdf, x='Sesión', y='Puntaje', color='Área', markers=True,
                                                 color_discrete_sequence=["#FF4B4B", "#1C83E1", "#00C781", "#FFAA00"])
                                
                                img_path = f"temp_hist_{dni_p}.png"
                                try:
    # Intentamos generar la imagen en memoria
                                    img_bytes = fig_pdf.to_image(format="png", engine="kaleido")
    
    # Pasamos los bytes directamente a la función del PDF
                                    st.session_state[pdf_key] = logic.generar_pdf_ficha(p, datos_pdf, img_bytes)
                                except Exception as e:
                                    st.error(f"No se pudo generar el gráfico para el PDF. Error técnico: {e}")
    # Opcional: generar el PDF sin el gráfico para que al menos descargue algo
                                st.session_state[pdf_key] = logic.generar_pdf_ficha(p, datos_pdf, None)
                                
                                # Generamos y guardamos el PDF en memoria
                                st.session_state[pdf_key] = logic.generar_pdf_ficha(p, datos_pdf, img_path)
                                
                                if os.path.exists(img_path): 
                                    os.remove(img_path)
                                st.rerun()
                    
                    # 2. Si ya se generó, mostramos el botón de descarga Teal
                    else:
                        st.download_button(
                            label="📥 DESCARGAR PDF",
                            data=bytes(st.session_state[pdf_key]),
                            file_name=f"Expediente_{dni_p}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
                else:
                    st.button("📄 PDF No Disponible", disabled=True, use_container_width=True, help="El paciente no tiene una ficha virtual completada.")

        # --- PESTAÑAS ESTILO PINHOME ---
        tab_fil, tab_dipac, tab_mental, tab_mon, tab_evo = st.tabs([
            "👤 Filiación", "📄 Datos HD:DIPAC", "🧠 Examen Mental", "📊 Monitoreo S1-S9", "📈 Evolución Diaria"
        ])

        # 1. TAB: FILIACIÓN (Card View)
        with tab_fil:
            with st.container(border=True):
                st.markdown("#### I. Datos de Filiación")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"**Nombres:** {p['nombres']}")
                    st.write(f"**Apellidos:** {p['apellidos']}")
                    st.write(f"**DNI:** {p['dni']}")
                    st.write(f"**Sexo:** {p['sexo']}")
                with c2:
                    st.write(f"**Edad:** {p['edad']} años")
                    st.write(f"**F. Nac:** {p['fecha_nac']}")
                    st.write(f"**Lugar:** {p.get('lugar', 'N/A')}")
                    st.write(f"**Est. Civil:** {p.get('estado_civil', 'N/A')}")
                with c3:
                    st.write(f"**Hijos:** {p.get('hijos', 0)}")
                    st.write(f"**Instrucción:** {p.get('instruccion', 'N/A')}")
                    st.write(f"**Ocupación:** {p.get('trabajo', 'N/A')}")
                st.divider()
                st.markdown(f"📍 **Dirección:** {p.get('direccion', 'N/A')}  |  📞 **Teléfono:** {p.get('telefono', 'N/A')}")

        if not f_db.empty:
            datos = json.loads(f_db.iloc[0]['datos_json'])
            
            # 2. TAB: DATOS COMPLEMENTARIOS (Split View)
            with tab_dipac:
                col_clin, col_adh = st.columns([3, 2], gap="large")
                with col_clin:
                    with st.container(border=True):
                        st.markdown("#### 🏥 Datos Clínicos")
                        f_clin = datos.get('filiacion', {})
                        st.write(f"**Modalidad:** {f_clin.get('modalidad', 'N/A')}")
                        st.write(f"**Turno/TE:** {f_clin.get('turno', 'N/A')}")
                        st.write(f"**T. Diálisis:** {f_clin.get('t_dialisis', 'N/A')}")
                        st.write(f"**Acceso:** {f_clin.get('acceso', 'N/A')}")
                        st.info(f"**Antecedentes:** {datos.get('antecedentes', 'N/A')}")

                with col_adh:
                    with st.container(border=True):
                        st.markdown("#### 📈 Adherencia (1-5)")
                        adh = datos.get('adherencia', {})
                        st.metric("Asistencia", f"{adh.get('asistencia', 0)}/5")
                        st.metric("Dieta", f"{adh.get('dieta', 0)}/5")
                        st.metric("Fármacos", f"{adh.get('farma', 0)}/5")
                        st.metric("Higiene", f"{adh.get('higiene', 0)}/5")

                with st.container(border=True):
                    st.markdown("#### 👨‍👩‍👧‍👦 Entorno Familiar y Social")
                    st.dataframe(pd.DataFrame(datos.get('familia', {})), hide_index=True, use_container_width=True)
                    cf1, cf2 = st.columns(2)
                    cf1.write(f"**Dinámica:** {datos.get('dinamica', 'N/A')}")
                    cf2.write(f"**Indicador Hídrico:** {datos.get('hidrico', 'N/A')}")

            # 3. TAB: EXAMEN MENTAL (Grid Layout)
            with tab_mental:
                st.markdown("#### III. Examen Mental")
                ex = datos.get('examen_mental', {})
                m_c1, m_c2 = st.columns(2)
                with m_c1:
                    with st.container(border=True):
                        st.write("**1. Observaciones:**")
                        st.write(ex.get('obs', 'N/A'))
                    with st.container(border=True):
                        st.write("**3. Cognoscitivos:**")
                        st.write(ex.get('cog', 'N/A'))
                with m_c2:
                    with st.container(border=True):
                        st.write("**2. Estado afectivo:**")
                        st.write(ex.get('afe', 'N/A'))
                    with st.container(border=True):
                        st.write("**4. Actividad Voluntaria:**")
                        st.write(ex.get('vol', 'N/A'))

            # 4. TAB: MONITOREO (Visual Card)
            with tab_mon:
                with st.container(border=True):
                    st.markdown("#### V. Monitoreo Bio-conductual")
                    df_mon = pd.DataFrame(datos.get('monitoreo', {}))
                    df_plot = df_mon.melt(id_vars='Área', var_name='Sesión', value_name='Puntaje')
                    fig_mon = px.line(df_plot, x='Sesión', y='Puntaje', color='Área', markers=True,
                                     color_discrete_sequence=["#FF4B4B", "#1C83E1", "#00C781", "#FFAA00"])
                    fig_mon.update_layout(yaxis_range=[-0.5, 10.5], height=400)
                    st.plotly_chart(fig_mon, use_container_width=True)
                    st.success(f"**Diagnóstico Final:** {datos.get('diagnostico', 'N/A')}")

        # 5. TAB: EVOLUCIÓN (Dashboard Style)
        with tab_evo:
            if not df_hist.empty:
                col_graph, col_list = st.columns([2, 3], gap="large")
                
                with col_graph:
                    with st.container(border=True):
                        st.subheader("📊 Resumen por Tipo")
                        categorias_fijas = ["Atención Psicológica", "Intervención Individual", "Intervención Familiar", "Evaluación Diagnóstica"]
                        df_conteo = df_hist['tipo_cita'].value_counts().reindex(categorias_fijas, fill_value=0).reset_index()
                        df_conteo.columns = ['Tipo', 'Cantidad']
                        
                        fig_barras = px.bar(df_conteo, x='Cantidad', y='Tipo', orientation='h', text='Cantidad',
                                            color='Tipo', color_discrete_map={
                                                "Atención Psicológica": "#1C83E1", "Intervención Individual": "#00C781",
                                                "Intervención Familiar": "#FFAA00", "Evaluación Diagnóstica": "#FF4B4B"
                                            })
                        fig_barras.update_layout(showlegend=False, height=350, margin=dict(t=0, b=0))
                        st.plotly_chart(fig_barras, use_container_width=True)

                with col_list:
                    st.subheader("📝 Notas Cronológicas")
                    df_notas_disp = df_hist.sort_values(by="fecha", ascending=False)
                    for i, fila in df_notas_disp.reset_index(drop=True).iterrows():
                        es_ultima = "🟢" if i == 0 else "⚪"
                        with st.expander(f"{es_ultima} {fila['fecha']} — {fila['tipo_cita']}"):
                            st.info(fila['observaciones'] if fila['observaciones'] else "Sin notas.")
                            if st.button("🗑️ Eliminar", key=f"del_h_evo_{fila['id']}", use_container_width=True):
                                if db.eliminar_registro_agenda(fila['id']):
                                    st.rerun()
            else:
                st.info("No se registran evoluciones diarias.")
    else:
        st.error("❌ Seleccione un paciente en la barra lateral.")

# =========================================================
# MÓDULO: 📊 ADMINISTRACIÓN Y ESTADÍSTICA (ESTILO DASHBOARD)
# =========================================================
elif modulo == "📊 Administración":
    st.title("📊 Panel de Administración y Control Clínico")
    st.markdown("<p style='color: #616161;'>Resumen estadístico del servicio de psicología en la Unidad de Hemodiálisis.</p>", unsafe_allow_html=True)

    conn = db.get_connection()

    # --- EXTRACCIÓN DE DATOS PREVIA PARA KPIs ---
    query_kpi_at = "SELECT count(*) as total FROM agenda WHERE estado = 'Atendido'"
    total_at = pd.read_sql_query(query_kpi_at, conn).iloc[0]['total']
    
    query_kpi_pac = "SELECT count(*) as total FROM pacientes"
    total_pac = pd.read_sql_query(query_kpi_pac, conn).iloc[0]['total']

    # --- 1. TARJETAS DE MÉTRICAS (KPIs) ESTILO EDSMART ---
    st.markdown(f"""
    <div style="display: flex; gap: 20px; margin-bottom: 25px;">
        <div style="flex: 1; background: white; padding: 20px; border-radius: 20px; border-left: 8px solid #00A896; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="font-size: 14px; color: #616161; font-weight: 600;">Pacientes Registrados</div>
            <div style="font-size: 32px; font-weight: 700; color: #1A1A1A;">{total_pac}</div>
            <div style="font-size: 12px; color: #00A896;">Base de Datos Total</div>
        </div>
        <div style="flex: 1; background: white; padding: 20px; border-radius: 20px; border-left: 8px solid #1C83E1; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="font-size: 14px; color: #616161; font-weight: 600;">Atenciones Realizadas</div>
            <div style="font-size: 32px; font-weight: 700; color: #1A1A1A;">{total_at}</div>
            <div style="font-size: 12px; color: #1C83E1;">Productividad Acumulada</div>
        </div>
        <div style="flex: 1; background: white; padding: 20px; border-radius: 20px; border-left: 8px solid #FFAA00; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="font-size: 14px; color: #616161; font-weight: 600;">Estado del Sistema</div>
            <div style="font-size: 32px; font-weight: 700; color: #1A1A1A;">Activo</div>
            <div style="font-size: 12px; color: #FFAA00;">Sincronizado con DB</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- 2. GRID DE GRÁFICOS (PRODUCTIVIDAD Y TURNOS) ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        with st.container(border=True):
            st.subheader("👨‍⚕️ Productividad")
            query_atenciones = "SELECT tipo_cita FROM agenda WHERE estado = 'Atendido'"
            df_atenciones = pd.read_sql_query(query_atenciones, conn)
            
            if not df_atenciones.empty:
                cats = ["Atención Psicológica", "Intervención Individual", "Intervención Familiar", "Evaluación Diagnóstica"]
                conteo_at = df_atenciones['tipo_cita'].value_counts().reindex(cats, fill_value=0).reset_index()
                conteo_at.columns = ['Tipo', 'Cantidad']
                
                fig_at = px.bar(conteo_at, x='Tipo', y='Cantidad', text='Cantidad',
                                color='Tipo', color_discrete_map={
                                    "Atención Psicológica": "#1C83E1", "Intervención Individual": "#00C781",
                                    "Intervención Familiar": "#FFAA00", "Evaluación Diagnóstica": "#FF4B4B"
                                })
                fig_at.update_layout(showlegend=False, height=350, margin=dict(t=10, b=10))
                st.plotly_chart(fig_at, use_container_width=True)
            else:
                st.warning("No hay atenciones.")

    with col_der:
        with st.container(border=True):
            st.subheader("🕒 Turnos")
            query_turnos = "SELECT turno FROM mapeo_camas"
            df_turnos = pd.read_sql_query(query_turnos, conn)
            
            if not df_turnos.empty:
                conteo_turnos = df_turnos['turno'].value_counts().reset_index()
                conteo_turnos.columns = ['Turno', 'Pacientes']
                
                fig_dona = px.pie(conteo_turnos, values='Pacientes', names='Turno', hole=.5,
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_dona.update_layout(height=350, margin=dict(t=10, b=10))
                st.plotly_chart(fig_dona, use_container_width=True)
            else:
                st.info("Mapa de salas vacío.")

    st.divider()

    # --- 3. PROMEDIO DE ADHERENCIA ---
    with st.container(border=True):
        st.subheader("📈 Promedio Global de Adherencia Bioconductual")
        query_fichas = "SELECT datos_json FROM fichas"
        df_fichas = pd.read_sql_query(query_fichas, conn)
        
        if not df_fichas.empty:
            lista_adherencia = []
            for j in df_fichas['datos_json']:
                data = json.loads(j)
                adh = data.get('adherencia', {})
                if adh: lista_adherencia.append(adh)
            
            if lista_adherencia:
                df_adh_global = pd.DataFrame(lista_adherencia)
                promedios = df_adh_global.mean().reset_index()
                promedios.columns = ['Indicador', 'Promedio']
                nombres_map = {'asistencia': 'Asistencia', 'dieta': 'Dieta', 'farma': 'Fármacos', 'higiene': 'Higiene'}
                promedios['Indicador'] = promedios['Indicador'].map(nombres_map)

                fig_adh = px.bar(promedios, x='Indicador', y='Promedio', range_y=[0,5],
                                 text=promedios['Promedio'].apply(lambda x: f"{x:.2f}"),
                                 color='Indicador', color_discrete_sequence=["#00A896"])
                fig_adh.update_layout(height=350)
                st.plotly_chart(fig_adh, use_container_width=True)
                st.caption("Cálculo basado en la última ficha registrada de cada paciente.")
            else:
                st.warning("Sin datos de adherencia.")
        else:
            st.warning("Sin fichas clínicas registradas.")
    
    conn.close()

# =========================================================
# SECCIÓN: MODULO_EVOLUCION_BIOCONDUCTUAL (NEW)
# =========================================================
elif modulo == "📈 Evolución":
    st.title("📈 Evolución Bio-conductual")
    st.markdown("<p style='color: #616161; margin-top: -15px;'>Seguimiento de indicadores psicológicos por sesión</p>", unsafe_allow_html=True)

    if p_df is not None and not p_df.empty:
        p = p_df.iloc[0]
        dni_paciente = p['dni']

        # 1. Recuperar datos existentes de la ficha más reciente
        ficha_data = db.obtener_ultima_ficha(dni_paciente) # Función que debes tener en db.py
        
        # Estructura base si no existe ficha previa [cite: 44, 134]
        if ficha_data and 'monitoreo' in ficha_data:
            df_actual = pd.DataFrame(ficha_data['monitoreo'])
        else:
            mon_base = {"Área": ["A (Afectivo)", "X (Ansioso)", "D (Adherencia)", "S (Sueño)"]}
            for i in range(1, 10): mon_base[f"S{i}"] = [0, 0, 0, 0]
            df_actual = pd.DataFrame(mon_base)

        # --- PANEL DE ACTUALIZACIÓN ---
        col_input, col_graph = st.columns([1, 1.5], gap="large")

        with col_input:
            with st.container(border=True):
                st.subheader("📝 Registrar Sesión")
                fecha_sesion = st.date_input("Fecha de hoy", datetime.now().date())
                
                st.markdown("##### Ajustar Puntajes (S1 - S9)")
                st.info("Modifique los valores en la tabla según la sesión correspondiente.")
                
                # Editor de datos para las sesiones [cite: 44, 124-132]
                df_evolucion = st.data_editor(
                    df_actual, 
                    hide_index=True, 
                    use_container_width=True,
                    key="editor_evolucion"
                )

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 ACTUALIZAR EVOLUCIÓN", type="primary", use_container_width=True):
                    # Actualizamos solo el nodo de monitoreo en la base de datos
                    if db.actualizar_monitoreo(dni_paciente, df_evolucion.to_dict()):
                        st.success("Evolución actualizada correctamente.")
                        st.rerun()

        with col_graph:
            with st.container(border=True):
                st.subheader("📊 Gráfico de Evolución")
                
                # Preparar datos para Plotly 
                df_plot = df_evolucion.melt(id_vars='Área', var_name='Sesión', value_name='Puntaje')
                
                fig_evol = px.line(
                    df_plot, 
                    x='Sesión', 
                    y='Puntaje', 
                    color='Área', 
                    markers=True,
                    color_discrete_sequence=["#FF4B4B", "#1C83E1", "#00C781", "#FFAA00"]
                )
                
                fig_evol.update_layout(
                    yaxis_range=[-0.5, 10.5], 
                    height=450,
                    margin=dict(t=20, b=20, l=10, r=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(245,245,245,0.5)'
                )
                
                st.plotly_chart(fig_evol, use_container_width=True)

    else:
        st.info("Seleccione un paciente en la barra lateral para ver su evolución.")

# =========================================================
# SECCIÓN: ADMINISTRACIÓN (MANTENIMIENTO)
# =========================================================
elif modulo == "⚙️ Mantenimiento": # O el nombre que uses para tu sección de admin
    st.title("⚙️ Panel de Mantenimiento")
    st.warning("Zona de mantenimiento crítico. Proceda con precaución.")

    # --- FUNCIÓN DE DIÁLOGO (POPUP DE SEGURIDAD) ---
    @st.dialog("⚠️ CONFIRMAR ELIMINACIÓN TOTAL")
    def popup_borrado_total():
        st.error("Esta acción eliminará todos los pacientes, fichas, evoluciones y mapas de salas de forma permanente.")
        st.write("Por favor, ingrese sus credenciales de super-usuario para continuar:")
        
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        
        if st.button("BORRAR TODA LA BASE DE DATOS", type="primary", use_container_width=True):
            # Validación de credenciales específicas
            if user_input == "73101004" and pass_input == "131429":
                if db.vaciar_base_de_datos():
                    st.success("Base de datos vaciada con éxito. Reiniciando...")
                    # Limpiamos estados de sesión para evitar conflictos
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error("Error técnico al intentar vaciar las tablas.")
            else:
                st.error("Credenciales incorrectas. Acceso denegado.")

    # --- BOTÓN AL FINAL DE LA PÁGINA ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.divider()
    st.subheader("🗑️ Gestión de Datos")
    
    if st.button("🔥 VACIAR TODA LA BASE DE DATOS", type="secondary", use_container_width=True):
        popup_borrado_total()

# =========================================================
# SECCIÓN: MODULO_REGISTRO_ATENCION (VERSIÓN FINAL CON WORD)
# =========================================================
elif modulo == "📊 Registro de Atención":
    st.title("📊 Registro de Atención Diaria")
    st.markdown("<p style='color: #616161; margin-top: -15px;'>Gestión de producción y redacción de evoluciones clínicas</p>", unsafe_allow_html=True)

    # --- A. DIÁLOGO PARA REGISTRO RÁPIDO ---
    @st.dialog("➕ Registrar Nuevo Paciente")
    def popup_nuevo_paciente():
        st.write("Complete los datos para habilitar al paciente en el sistema.")
        with st.form("form_nuevo_atencion_popup"):
            c1, c2 = st.columns(2)
            new_dni = c1.text_input("DNI *")
            new_ape = c2.text_input("Apellidos *") 
            new_nom = st.text_input("Nombres *")
            c3, c4 = st.columns(2)
            new_eda = c3.number_input("Edad", 0, 110, 30)
            new_sex = c4.radio("Sexo *", ["M", "F"], horizontal=True)
            
            if st.form_submit_button("Cargar al Sistema"):
                if new_dni and new_nom and new_ape:
                    if db.guardar_paciente(new_dni, new_nom, new_ape, new_eda, new_sex, 
                                          "N/R", "N/R", "N/R", 0, "N/R", "N/R", "N/R", "N/R", "Externo"):
                        st.success(f"Paciente {new_ape} cargado correctamente."); st.rerun()
                    else: st.error("Error: El DNI ya existe.")
                else: st.warning("Datos obligatorios faltantes.")

    # --- B. CABECERA DE CONTROL ---
    with st.container(border=True):
        col_f, col_p, col_g = st.columns([1.5, 1.5, 2])
        with col_f:
            q_fecha_trabajo = st.date_input("📅 Fecha de Trabajo", datetime.now().date(), key="fecha_reg_v4")
        with col_p:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ NUEVO PACIENTE", use_container_width=True, key="btn_add_v4"):
                popup_nuevo_paciente()
        with col_g:
            st.markdown("<br>", unsafe_allow_html=True)
            btn_finalizar = st.button("🚀 GUARDAR Y FINALIZAR JORNADA", type="primary", use_container_width=True, key="btn_save_v4")

    st.divider()

    # --- C. CARGA DE DATOS ---
    conn = db.get_connection()
    full_p_df = pd.read_sql("SELECT dni, nombres, apellidos FROM pacientes", conn)
    conn.close()
    
    mapa_nombres = {row['dni']: f"{row['apellidos']} {row['nombres']}" for _, row in full_p_df.iterrows()}
    lista_opciones = [f"{dni} - {nombre}" for dni, nombre in mapa_nombres.items()]
    df_existentes = db.obtener_registros_por_fecha(str(q_fecha_trabajo))

    # --- D. PANEL DE ACTIVIDADES (TABS) ---
    actividades = ["Atención Psicológica", "Intervención Individual", "Intervención Familiar", "Evaluación Diagnóstica"]
    tabs = st.tabs(actividades)
    datos_jornada = {}

    for i, tab in enumerate(tabs):
        nombre_act = actividades[i]
        with tab:
            st.markdown(f"### {nombre_act}")
            
            pre_seleccionados = []
            if not df_existentes.empty:
                dnis_hoy = df_existentes[df_existentes['tipo_cita'] == nombre_act]['dni_paciente'].tolist()
                pre_seleccionados = [f"{dni} - {mapa_nombres[dni]}" for dni in dnis_hoy if dni in mapa_nombres]

            seleccionados = st.multiselect(
                f"Pacientes para {nombre_act}:", 
                options=list(set(lista_opciones)), 
                default=list(set(pre_seleccionados)), 
                key=f"msel_v4_{i}_{str(q_fecha_trabajo)}"
            )
            
            datos_jornada[nombre_act] = []
            if seleccionados:
                st.write("---")
                for p_idx, p_label in enumerate(seleccionados):
                    dni_p = p_label.split(" - ")[0]
                    
                    texto_previo = ""
                    if not df_existentes.empty:
                        match = df_existentes[(df_existentes['dni_paciente'] == dni_p) & (df_existentes['tipo_cita'] == nombre_act)]
                        if not match.empty: texto_previo = match.iloc[0]['observaciones']

                    # Clave blindada para evitar el DuplicateKeyError
                    key_area = f"evol_v4_{i}_{dni_p}_{str(q_fecha_trabajo)}_{p_idx}"
                    
                    txt_evol = st.text_area(f"Evolución: {p_label}", value=texto_previo, key=key_area, height=100)
                    datos_jornada[nombre_act].append({"dni": dni_p, "nombre": mapa_nombres.get(dni_p, "N/R"), "texto": txt_evol})

    # --- E. LÓGICA DE CIERRE Y DESCARGAS RECUPERADA ---
    if btn_finalizar:
        if any(datos_jornada.values()):
            contador = 0
            with st.status("Sincronizando producción mensual...", expanded=True) as status:
                for act, pacientes in datos_jornada.items():
                    for p in pacientes:
                        db.guardar_actividad_ruta(p['dni'], q_fecha_trabajo, act, p['texto'])
                        contador += 1
                status.update(label=f"✅ {contador} atenciones guardadas exitosamente.", state="complete")
            
            st.balloons()
            st.markdown("### 📥 Descargar Documentos de la Jornada")
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                # REPORTE PDF ADMINISTRATIVO
                pdf_bytes = logic.generar_reporte_administrativo_limpio(q_fecha_trabajo, datos_jornada)
                st.download_button(
                    label="📄 REPORTE PDF (ADMIN)", 
                    data=pdf_bytes, 
                    file_name=f"Reporte_{q_fecha_trabajo}.pdf", 
                    mime="application/pdf", 
                    use_container_width=True
                )
            
            with col_d2:
                # EVOLUCIONES EN WORD (PARA EDITAR Y PEGAR)
                word_buffer = logic.generar_word_evoluciones(q_fecha_trabajo, datos_jornada)
                st.download_button(
                    label="📝 EVOLUCIONES WORD (CLÍNICO)", 
                    data=word_buffer, 
                    file_name=f"Evoluciones_{q_fecha_trabajo}.docx", 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                    use_container_width=True, 
                    type="primary"
                )
        else:
            st.error("No hay pacientes seleccionados para guardar.")
# =========================================================
# SECCIÓN: INFORME MENSUAL (CONSOLIDADO Y LIMPIEZA)
# =========================================================
elif modulo == "📅 Informe Mensual":
    st.title("📅 Gestión de Informe Mensual")
    db.actualizar_esquema_diagnostico()

    with st.sidebar:
        st.divider()
        st.subheader("Periodo del Informe")
        mes_sel = st.selectbox("Mes", range(1, 13), index=datetime.now().month - 1)
        anio_sel = st.selectbox("Año", [2025, 2026, 2027], index=1)
        
        # HERRAMIENTA DE LIMPIEZA PROFUNDA
        if st.button("🧹 LIMPIAR DUPLICADOS ANTIGUOS"):
            conn = db.get_connection()
            conn.execute("""
                DELETE FROM agenda 
                WHERE id NOT IN (
                    SELECT MAX(id) FROM agenda 
                    GROUP BY dni_paciente, fecha, tipo_cita
                )
            """)
            conn.commit()
            conn.close()
            st.success("Limpieza completada.")

    st.markdown("### 🗓️ 1. Registro por Fecha de Atención")
    fecha_rev = st.date_input("Seleccione el día para registrar diagnósticos:", datetime.now().date())
    
    df_mes = db.obtener_atenciones_mensuales_completas(mes_sel, anio_sel)
    df_dia = df_mes[df_mes['fecha'] == str(fecha_rev)]

    if not df_dia.empty:
        st.info(f"Atenciones del día: {len(df_dia)}")
        cambios_finales = {}
        for tipo in ["Atención Psicológica", "Intervención Individual", "Intervención Familiar", "Evaluación Diagnóstica"]:
            sub_df = df_dia[df_dia['tipo_cita'] == tipo]
            if not sub_df.empty:
                st.subheader(f"🔹 {tipo}")
                df_editado = st.data_editor(
                    sub_df[['id', 'dni', 'apellidos', 'nombres', 'edad', 'sexo', 'diagnostico']],
                    column_config={"id": None, "diagnostico": st.column_config.TextColumn("DIAGNÓSTICO", width="large")},
                    hide_index=True, use_container_width=True, key=f"ed_inf_{fecha_rev}_{tipo}"
                )
                cambios_finales[tipo] = df_editado

        # --- BOTONES DE ACCIÓN ---
        col_acc1, col_acc2 = st.columns([3, 1])
        
        with col_acc1:
            if st.button("✅ GUARDAR REGISTROS DEL DÍA", type="primary", use_container_width=True):
                for _, df_tipo in cambios_finales.items():
                    for _, row in df_tipo.iterrows():
                        db.guardar_diagnostico_administrativo(row['id'], row['diagnostico'])
                st.success("Guardado."); st.rerun()
        
        with col_acc2:
            # Popover para evitar borrados accidentales
            with st.popover("⚠️ Borrar Día"):
                st.warning("Esta acción eliminará todas las atenciones de esta fecha.")
                confirmar = st.checkbox("Confirmar eliminación")
                if st.button("🗑️ ELIMINAR TODO", disabled=not confirmar, use_container_width=True):
                    if db.eliminar_atenciones_por_fecha(fecha_rev):
                        st.success("Jornada eliminada."); st.rerun()
                    else:
                        st.error("Error al borrar.")

    else:
        st.warning(f"No hay registros el {fecha_rev}.")

    # --- 3. CIERRE Y GENERACIÓN DE REPORTES ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    st.subheader(f"🚀 2. Cierre Mensual Consolidado ({mes_sel}/{anio_sel})")
    
    if st.button("📂 PROCESAR INFORME MENSUAL", use_container_width=True):
        df_final_mes = db.obtener_atenciones_mensuales_completas(mes_sel, anio_sel)
        if not df_final_mes.empty:
            pdf_bytes = logic.generar_informe_mensual_secuencial(mes_sel, anio_sel, df_final_mes)
            c_d1, c_d2 = st.columns(2)
            with c_d1: 
                st.download_button("📥 DESCARGAR PDF", data=pdf_bytes, file_name=f"Informe_{mes_sel}.pdf", use_container_width=True)
            with c_d2:
                output = io.BytesIO()
                df_final_mes.to_excel(output, index=False)
                st.download_button("📥 EXCEL TOTAL", data=output.getvalue(), file_name=f"Data_{mes_sel}.xlsx", use_container_width=True)
