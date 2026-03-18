"""
Módulo de Autenticación con Supabase.
Provee funciones helper para login/logout usando Supabase Auth.

MEJORAS DE SEGURIDAD FASE 1:
- Validación de email con regex
- Errores genéricos en producción (no exponer detalles internos)
- Soporte para variables de entorno
- Detección de modo producción
"""
import re
import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional


# Patrones de validación
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


class AuthError(Exception):
    """Excepción personalizada para errores de autenticación."""
    pass


class ValidationError(Exception):
    """Excepción para errores de validación de inputs."""
    pass


def is_production() -> bool:
    """Detecta si la app está en producción."""
    return os.getenv("ENVIRONMENT", "development") == "production"


def validate_email(email: str) -> bool:
    """
    Valida el formato de un email.
    
    Args:
        email: Email a validar
    
    Returns:
        True si es válido, False si no
    """
    if not email:
        return False
    return EMAIL_PATTERN.match(email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """
    Valida que la contraseña cumpla requisitos mínimos.
    
    Args:
        password: Contraseña a validar
    
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not password:
        return False, "La contraseña no puede estar vacía"
    
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    return True, ""


def sanitize_email(email: str) -> str:
    """
    Sanitiza el email eliminando espacios en blanco extra.
    
    Args:
        email: Email a sanitizar
    
    Returns:
        Email sanitizado
    """
    return email.strip().lower()


def get_supabase_client() -> Client:
    """
    Crea cliente Supabase desde st.secrets o variables de entorno.
    
    Order de precedencia:
    1. st.secrets (para Streamlit Cloud)
    2. Variables de entorno (para producción)
    
    Raises:
        ValueError: Si no encuentra configuración
    """
    # Intentar desde st.secrets primero
    try:
        url = st.secrets.get("SUPABASE_URL") if hasattr(st, 'secrets') else None
        key = st.secrets.get("SUPABASE_KEY") if hasattr(st, 'secrets') else None
    except Exception:
        url = None
        key = None
    
    # Fallback a variables de entorno
    if not url:
        url = os.getenv("SUPABASE_URL")
    if not key:
        key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise AuthError(
            "Configuración de Supabase no encontrada. "
            "Verifica secrets.toml o variables de entorno."
        )
    
    return create_client(url, key)


def login_user(email: str, password: str) -> dict:
    """
    Intenta iniciar sesión con email y password.
    
    Validaciones:
    - Formato de email
    - Longitud de contraseña
    
    Args:
        email: Email del usuario
        password: Contraseña
    
    Returns:
        dict con 'success' (bool), 'user' (user data), 'error' (message).
    
    Errores genéricos (producción):
    - "Email inválido" para emails mal formateados
    - "Credenciales inválidas" para login fallido
    - "Error de conexión" para problemas de red
    """
    # Sanitizar inputs
    email = sanitize_email(email) if email else ""
    
    # Validar email
    if not validate_email(email):
        return {
            "success": False,
            "error": "El formato del email es inválido"
        }
    
    # Validar contraseña
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return {
            "success": False,
            "error": error_msg
        }
    
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
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
            return {
                "success": False,
                "error": "Credenciales inválidas"
            }
            
    except Exception as e:
        error_msg = str(e).lower()
        
        # Detectar tipo de error sin exponer detalles internos
        if "invalid login credentials" in error_msg:
            return {"success": False, "error": "Credenciales inválidas"}
        
        if "email not confirmed" in error_msg:
            return {"success": False, "error": "Email no confirmado. Revisa tu bandeja de entrada."}
        
        if "too many requests" in error_msg:
            return {"success": False, "error": "Demasiados intentos. Espera unos minutos."}
        
        # En producción, no exponer el error real
        if is_production():
            return {"success": False, "error": "Error de autenticación. Intenta de nuevo."}
        
        # En desarrollo, mostrar error detallado
        return {"success": False, "error": f"Error de conexión: {error_msg}"}


def logout_user() -> None:
    """
    Cierra la sesión actual.
    Los errores se ignoran silenciosamente.
    """
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception:
        # Silenciosamente ignorar errores de logout
        pass


def get_current_user() -> Optional[dict]:
    """
    Retorna el usuario actual desde la sesión activa.
    
    Returns:
        dict con datos del usuario o None si no hay sesión.
    """
    if "supabase_session" not in st.session_state:
        return None
    
    session = st.session_state.get("supabase_session")
    if not session:
        return None
    
    try:
        supabase = get_supabase_client()
        access_token = session.get("access_token")
        if not access_token:
            return None
        
        user_response = supabase.auth.get_user(access_token)
        return user_response.user if user_response else None
    except Exception:
        return None


def init_session_state() -> None:
    """
    Inicializa el session_state para autenticación.
    Debe llamarse al inicio de la aplicación.
    """
    defaults = {
        "supabase_session": None,
        "user": None,
        "authenticated": False,
        "page": "Extraer"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def require_auth() -> None:
    """
    Verifica que el usuario esté autenticado.
    Si no lo está, muestra warning y detiene la ejecución.
    
    Uso:
        require_auth()  # Si no está auth, se detiene aquí
        # Continuar con el resto de la función
    """
    init_session_state()
    
    if not st.session_state.get("authenticated", False):
        st.warning("Por favor, inicia sesión para acceder a esta página.")
        st.stop()


def is_authenticated() -> bool:
    """
    Retorna True si el usuario está autenticado.
    
    Returns:
        True si hay sesión válida, False si no
    """
    return st.session_state.get("authenticated", False) and st.session_state.get("user") is not None
