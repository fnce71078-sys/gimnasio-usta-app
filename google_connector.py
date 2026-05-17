import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

@st.cache_resource
def conectar_sheets():
    """
    Función para establecer la conexión con Google Sheets.
    Usa cache_resource para no recargar la conexión cada vez que el usuario hace clic.
    """
    # 1. Definir los permisos (scopes) a los que la app tendrá acceso
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # 2. Cargar las credenciales desde el archivo JSON local
        credenciales = Credentials.from_service_account_file(
            "credenciales.json", 
            scopes=scopes
        )
        
        # 3. Autorizar el cliente con Google
        cliente = gspread.authorize(credenciales)
        
        # 4. Abrir el documento exacto por su nombre
        # Asegúrate de que tu Excel se llame exactamente así
        documento = cliente.open("Gimnasio_USTA_DB")
        
        return documento
        
    except FileNotFoundError:
        st.error("❌ Error: No se encontró el archivo 'credenciales.json'. Verifica que esté en la carpeta principal.")
        return None
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        return None