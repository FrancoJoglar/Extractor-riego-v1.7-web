"""
Módulo de Autenticación con Supabase.
Provee funciones helper para login/logout usando Supabase Auth.
"""
import streamlit as st
from supabase import create_client, Client
import os

# Configuración desde secrets o variables de entorno
def get_supabase_client() -> Client:
    """Crea cliente Supabase desde st.secrets o entorno."""
    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas en secrets.toml")
    
    return create_client(url, key)


def login_user(email: str, password: str) -> dict:
    """
    Intenta iniciar sesión con email y password.
    Retorna dict con 'success' (bool), 'user' (user data), 'error' (message).
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "success": True,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "email_confirmed_at": response.user.email_confirmed_at
                },
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }
            }
        else:
            return {"success": False, "error": "Credenciales inválidas"}
            
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return {"success": False, "error": "Credenciales inválidas"}
        return {"success": False, "error": f"Error de conexión: {error_msg}"}


def logout_user() -> None:
    """Cierra la sesión actual."""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except:
        pass  # Ignorar errores al logout


def get_current_user() -> dict | None:
    """
    Retorna el usuario actual desde la sesión activa.
    None si no hay sesión.
    """
    if "supabase_session" not in st.session_state:
        return None
    
    try:
        supabase = get_supabase_client()
        # El token está en session_state
        session = st.session_state.supabase_session
        user = supabase.auth.get_user(session.get("access_token"))
        return user.user if user else None
    except:
        return None


def init_session_state():
    """Inicializa el session_state para autenticación."""
    if "supabase_session" not in st.session_state:
        st.session_state.supabase_session = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False


def require_auth():
    """
    Decorator/función que verifica autenticación.
    Si no está autenticado, muestra login y detiene ejecución.
    """
    init_session_state()
    
    if not st.session_state.authenticated:
        st.warning("Por favor, inicia sesión para acceder a esta página.")
        st.stop()
