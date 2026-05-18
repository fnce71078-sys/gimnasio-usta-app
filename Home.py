import streamlit as st
from PIL import Image
# Importamos timedelta y timezone para fijar la hora exacta de Colombia
from datetime import datetime, timedelta, timezone
# Importamos el conector de la base de datos (Fase 2)
from google_connector import conectar_sheets

# =========================================================
# CONFIGURACIÓN DE LA ZONA HORARIA DE COLOMBIA (UTC-5)
# =========================================================
ZONA_HORARIA_COLOMBIA = timezone(timedelta(hours=-5))

# =========================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y DISEÑO MÓVIL
# =========================================================
st.set_page_config(
    page_title="Gimnasio USTA",
    page_icon="🏋️‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Ocultar visualmente el menú lateral por defecto en dispositivos móviles
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. ENCABEZADO INSTITUCIONAL (LOGO)
# =========================================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        logo = Image.open("assets/usta.jpg")
        st.image(logo, use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ No se encontró el logo. Verifique que el archivo se llame usta.jpg dentro de la carpeta assets")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Gimnasio USTA Villavicencio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555; font-size: 16px; font-weight: bold;'>Departamento de Bienestar Universitario</p>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================
# 3. INSTRUCTIVO DE USO DETALLADO Y FORMAL
# =========================================================
st.markdown("""
### 📋 Guía de Orientación al Usuario

Para garantizar un control de acceso eficiente, por favor lea atentamente las indicaciones antes de proceder:

* 🔑 **Documento de Identificación:** * Si es **Estudiante, Docente, Egresado o Administrativo**, debe ingresar su **Código Institucional**.
  * Si es **Visitante Externo**, debe ingresar su **Número de Cédula de Ciudadanía**.
* 🏫 **Personal de Áreas Transversales:** Si pertenece a dependencias académicas generales como *Campus Virtual, CILCE, Dirección de Ciencias Básicas o Dirección CRAI*, elija la opción **"Dependencias Académicas"** en el campo de adscripción.

---
### 🔄 Flujo Lógico de Acceso (¿Qué debe hacer hoy?)
1. **¿Es su primera visita al gimnasio en este periodo académico?**
   Seleccione la pestaña **"📝 Registro Nuevo"** en el menú de abajo, diligencie el formulario maestro por única vez en el semestre y acepte el tratamiento de datos.
2. **¿Ya realizó el registro maestro anteriormente?**
   Seleccione la pestaña **"📲 Registrar Asistencia"** en el menú de abajo e ingrese su número de identificación. *¡Este es el único paso requerido para sus futuras visitas diarias!*
""")

st.markdown("---")

# =========================================================
# 4. MENÚ DE SELECCIÓN DE ACCIÓN
# =========================================================
st.markdown("<p style='text-align: center; font-weight: bold; color: #1E3A8A;'>Por favor, seleccione la acción que va a realizar:</p>", unsafe_allow_html=True)

opcion = st.radio(
    "Menú principal",
    ["📲 Registrar Asistencia", "📝 Registro Nuevo"],
    horizontal=True, 
    label_visibility="collapsed" 
)

st.markdown("---")

# =========================================================
# 5. EJECUCIÓN DE MÓDULOS ACTIVOS
# =========================================================

# ---------------------------------------------------------
# MÓDULO A: REGISTRAR ASISTENCIA (Control QR Diario)
# ---------------------------------------------------------
if opcion == "📲 Registrar Asistencia":
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Control de Acceso</h2>", unsafe_allow_html=True)
    
    with st.form("form_asistencia", clear_on_submit=True):
        codigo_input = st.text_input("Ingrese su Código Institucional o Cédula (Solo números):", placeholder="Ej. 2195000 o 10102020")
        btn_ingreso = st.form_submit_button("Registrar Ingreso 🏃‍♂️")
        
        if btn_ingreso:
            codigo_clean = codigo_input.strip()
            
            if not codigo_clean:
                st.error("⚠️ El campo de identificación no puede estar vacío.")
            elif not codigo_clean.isdigit():
                st.error("⚠️ El documento o código debe ser estrictamente numérico.")
            else:
                with st.spinner("Validando credenciales en el sistema..."):
                    db = conectar_sheets()
                    
                    if db is not None:
                        try:
                            sheet_usuarios = db.worksheet("Usuarios")
                            sheet_asistencias = db.worksheet("Asistencias")
                            
                            datos_usuarios = sheet_usuarios.get_all_values()
                            codigos_existentes = [fila[0] for fila in datos_usuarios[1:] if len(fila) > 0]
                            
                            if codigo_clean not in codigos_existentes:
                                st.error("❌ El número ingresado no se encuentra registrado en el sistema. Por favor, seleccione la pestaña superior '📝 Registro Nuevo' para diligenciar su inscripción maestro antes de ingresar.")
                            else:
                                nombre_usuario = "Usuario"
                                for fila in datos_usuarios[1:]:
                                    if len(fila) >= 2 and fila[0] == codigo_clean:
                                        nombre_usuario = fila[1]
                                        break
                                
                                # Ajuste de zona horaria para garantizar la hora exacta de Colombia
                                ahora = datetime.now(ZONA_HORARIA_COLOMBIA)
                                fecha_actual = ahora.strftime("%Y-%m-%d")
                                hora_actual = ahora.strftime("%H:%M:%S")
                                
                                sheet_asistencias.append_row([codigo_clean, fecha_actual, hora_actual])
                                
                                st.success(f"✅ ¡Ingreso registrado con éxito! Bienvenido(a), **{nombre_usuario}**. Que tenga una excelente jornada de entrenamiento.")
                        except Exception as e:
                            st.error(f"❌ Error interno al conectar con la base de datos: {e}")

# ---------------------------------------------------------
# MÓDULO B: REGISTRO NUEVO MAESTRO (Única Vez)
# ---------------------------------------------------------
elif opcion == "📝 Registro Nuevo":
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Formulario de Registro Maestro</h2>", unsafe_allow_html=True)
    
    ROLES = ["Estudiante", "Docente", "Egresado", "Administrativo", "Externo"]
    FACULTADES = [
        "Administración de Empresas Agropecuarias",
        "Arquitectura",
        "Arte y Cultura",
        "Contaduría Pública",
        "Cultura Física, Deporte y Recreación",
        "Derecho",
        "Dependencias Académicas", 
        "Ingeniería Ambiental",
        "Ingeniería Civil",
        "Ingeniería de Sistemas",
        "Ingeniería Industrial",
        "Ingeniería Mecánica",
        "Ingeniería Mecatrónica",
        "Lenguas Extranjeras",
        "Negocios Internacionales",
        "Psicología",
        "Posgrados"
    ]
    TIPOS_SANGRE = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    GENEROS = ["Hombre", "Mujer", "Otro"]

    st.markdown("#### 1. Identificación de Perfil")
    rol_seleccionado = st.selectbox("Rol Institucional:", options=ROLES)
    
    st.markdown("#### 2. Datos Personales")
    with st.form("formulario_registro", clear_on_submit=False):
        nombre = st.text_input("Nombre Completo:", placeholder="Ej. Juan Pérez")
        codigo = st.text_input("Código Institucional o Cédula (Solo números):", placeholder="Ej. 2195000 o 10102020")
        
        facultad_seleccionada = None
        if rol_seleccionado in ["Estudiante", "Docente", "Egresado"]:
            facultad_seleccionada = st.selectbox("Facultad o Dependencia Académica:", options=FACULTADES)
            
        col_rh, col_edad = st.columns(2)
        with col_rh:
            rh = st.selectbox("Factor RH / Grupo Sanguíneo:", options=TIPOS_SANGRE)
        with col_edad:
            edad = st.number_input("Edad Cronológica:", min_value=15, max_value=90, value=18, step=1)
            
        genero = st.selectbox("Género:", options=GENEROS)
        
        genero_especifico = ""
        if genero == "Otro":
            genero_especifico = st.text_input("Por favor, especifique:")
            
        contacto_emergencia = st.text_input("Nombre del Contacto de Emergencia:", placeholder="Ej. María Gómez (Madre)")
        telefono_emergencia = st.text_input("Teléfono de Emergencia (Solo números):", placeholder="Ej. 3101234567")
        
        st.markdown("#### Protección de Datos Personales")
        habeas_data = st.checkbox(
            "Acepto el tratamiento de datos por parte del departamento de bienestar universitario de la Universidad Santo Tomás seccional Villavicencio"
        )
        
        btn_enviar = st.form_submit_button("Finalizar Registro Maestro 💾")
        
        if btn_enviar:
            nombre_c = nombre.strip()
            codigo_c = codigo.strip()
            contacto_c = contacto_emergencia.strip()
            tel_c = telefono_emergencia.strip()
            genero_final = genero_especifico.strip() if genero == "Otro" else genero
            
            if rol_seleccionado == "Administrativo":
                facultad_final = "Área Administrativa"
            elif rol_seleccionado == "Externo":
                facultad_final = "No Aplica - Externo"
            else:
                facultad_final = facultad_seleccionada
            
            if not nombre_c or not codigo_c or not contacto_c or not tel_c:
                st.error("⚠️ Todos los campos de texto son obligatorios para el registro de seguridad.")
            elif not codigo_c.isdigit():
                st.error("⚠️ El documento de identidad o código debe ser estrictamente numérico.")
            elif not tel_c.isdigit():
                st.error("⚠️ El teléfono de emergencia debe ser estrictamente numérico.")
            elif genero == "Otro" and not genero_final:
                st.error("⚠️ Debe especificar el campo de género al haber seleccionado la opción 'Otro'.")
            elif not habeas_data:
                st.error("❌ Proceso denegado. Debe aceptar la cláusula de Habeas Data para almacenar su registro.")
            else:
                with st.spinner("Conectando con el servidor maestro..."):
                    db = conectar_sheets()
                    
                    if db is not None:
                        try:
                            sheet_usuarios = db.worksheet("Usuarios")
                            codigos_existentes = sheet_usuarios.col_values(1)
                            
                            if codigo_c in codigos_existentes:
                                st.warning(f"⚠️ Operación cancelada. La identificación o código {codigo_c} ya se encuentra registrada en el sistema.")
                            else:
                                # Ajuste de zona horaria para garantizar la hora exacta de Colombia en el Timestamp maestro
                                fecha_registro = datetime.now(ZONA_HORARIA_COLOMBIA).strftime("%Y-%m-%d %H:%M:%S")
                                
                                nueva_fila = [
                                    codigo_c,
                                    nombre_c,
                                    rol_seleccionado,
                                    facultad_final,
                                    rh,
                                    int(edad),
                                    genero_final,
                                    contacto_c,
                                    tel_c,
                                    fecha_registro
                                ]
                                
                                sheet_usuarios.append_row(nueva_fila)
                                
                                st.success("🎉 ¡Felicitaciones! Su registro ha sido exitoso en el sistema. "
                                           "Ahora, por favor seleccione la opción '📲 Registrar Asistencia' "
                                           "en el menú de arriba para marcar su ingreso correspondiente a hoy. "
                                           "Recuerde que este formulario maestro no lo debe volver a diligenciar.")
                                st.balloons()
                        except Exception as e:
                            st.error(f"❌ Error interno al conectar con la base de datos: {e}")