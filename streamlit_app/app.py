"""
Riego Extractor - Streamlit Web App
====================================
Punto de entrada principal con autenticación.
"""
import streamlit as st
import sys
import os

# Agregar path para imports de módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.auth import (
    login_user, logout_user, init_session_state, require_auth
)


def main():
    """Función principal."""
    st.set_page_config(
        page_title="Riego Extractor",
        page_icon="💧",
        layout="wide"
    )
    
    init_session_state()
    
    # Verificar si hay query params para logout
    query_params = st.query_params
    if query_params.get("logout") == "1":
        logout_user()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.supabase_session = None
        st.query_params.clear()
        st.rerun()
    
    # Si no está autenticado, mostrar login
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()


def show_login_page():
    """Muestra la página de login."""
    st.title("💧 Riego Extractor")
    st.markdown("### Iniciar Sesión")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="tu@email.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Iniciar Sesión", type="primary")
        
        if submit:
            if not email or not password:
                st.error("Por favor, completa todos los campos")
            else:
                result = login_user(email, password)
                
                if result.get("success"):
                    st.session_state.authenticated = True
                    st.session_state.user = result.get("user")
                    st.session_state.supabase_session = result.get("session")
                    st.rerun()
                else:
                    st.error(result.get("error", "Error de autenticación"))
    
    st.markdown("---")
    st.markdown("**Nota:** Usa las credenciales de Supabase Auth.")
    st.markdown("Contacta al administrador si no tienes acceso.")


def show_main_app():
    """Muestra la aplicación principal con sidebar."""
    # Sidebar
    st.sidebar.title("💧 Riego Extractor")
    st.sidebar.markdown(f"**Usuario:** {st.session_state.user.get('email')}")
    
    # Navigation
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navegación",
        ["Extraer Riegos", "Programar Horarios", "Mantenimiento"]
    )
    
    # Logout button
    if st.sidebar.button("Cerrar Sesión"):
        st.query_params["logout"] = "1"
        st.rerun()
    
    # Route to pages
    if page == "Extraer Riegos":
        from pages import extraer
        extraer.show()
    elif page == "Programar Horarios":
        from pages import programar
        programar.show()
    elif page == "Mantenimiento":
        from pages import mantenimiento
        mantenimiento.show()


if __name__ == "__main__":
    main()
