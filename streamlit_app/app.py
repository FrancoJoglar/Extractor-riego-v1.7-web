"""
Riego Extractor - Streamlit Web App
"""
import streamlit as st
import importlib.util
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.auth import login_user, logout_user


def main():
    st.set_page_config(page_title="Riego Extractor", page_icon="💧", layout="wide")
    
    # Inicializar estado
    if 'page' not in st.session_state:
        st.session_state.page = 'Extraer'
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Logout
    if st.query_params.get("logout") == "1":
        logout_user()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.page = 'Extraer'
        st.query_params.clear()
        st.rerun()
    
    # Mostrar login o app
    if not st.session_state.authenticated:
        show_login()
    else:
        show_app()


def show_login():
    st.markdown("# 🌱 RIEGO EXTRACTOR")
    st.markdown("### Sistema de Gestión de Riego")
    
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if email and password:
                result = login_user(email, password)
                if result.get("success"):
                    st.session_state.authenticated = True
                    st.session_state.user = result.get("user")
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")
            else:
                st.warning("Completa todos los campos")


def show_app():
    # SIDEBAR SIMPLE
    with st.sidebar:
        st.markdown("### RIEGO EXTRACTOR")
        st.markdown(f"**{st.session_state.user.get('email', 'Usuario')}**")
        st.markdown("---")
        
        # Botones navegación
        if st.button("📋 Extraer Riegos", use_container_width=True):
            st.session_state.page = 'Extraer'
            st.rerun()
        
        if st.button("📅 Programar Horarios", use_container_width=True):
            st.session_state.page = 'Programar'
            st.rerun()
        
        if st.button("🔧 Mantenimiento", use_container_width=True):
            st.session_state.page = 'Mantenimiento'
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.query_params["logout"] = "1"
            st.rerun()
    
    # CONTENIDO
    page = st.session_state.page
    
    if page == "Extraer":
        spec = importlib.util.spec_from_file_location("p", "pages/_extraer.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.show()
    elif page == "Programar":
        spec = importlib.util.spec_from_file_location("p", "pages/_programar.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.show()
    elif page == "Mantenimiento":
        spec = importlib.util.spec_from_file_location("p", "pages/_mantenimiento.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.show()


if __name__ == "__main__":
    main()
