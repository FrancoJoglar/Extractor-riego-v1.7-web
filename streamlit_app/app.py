"""
Riego Extractor - Streamlit Web App
Siracusa-inspired Design
"""
import streamlit as st
import importlib.util
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.auth import login_user, logout_user

# CSS is now injected inside main() after set_page_config()


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700&display=swap');
    :root {
        --primary: #22c55e;
        --primary-dark: #16a34a;
        --primary-deep: #14532d;
        --text-primary: #292524;
        --text-secondary: #78716c;
        --bg-main: #f8fafc;
    }
    * { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #14532d 0%, #166534 50%, #15803d 100%) !important; padding: 12px !important; }
    .sidebar-title { font-family: 'Outfit', sans-serif; font-size: 18px !important; font-weight: 700; color: #ffffff; text-align: center; padding: 8px 0 24px 0; margin: 0; border-bottom: 1px solid rgba(255,255,255,0.15); letter-spacing: 0.02em; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] { margin: 8px 0 !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div { background: rgba(255,255,255,0.12) !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 10px !important; color: #ffffff !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label { color: #ffffff !important; font-family: 'DM Sans', sans-serif !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] option { background: #14532d !important; color: #ffffff !important; }
    [data-testid="stSidebar"] [data-testid="stButton"] > button { width: 100%; background: rgba(239,68,68,0.2) !important; color: #fca5a5 !important; border: 1px solid rgba(239,68,68,0.3) !important; border-radius: 10px !important; padding: 10px 16px !important; font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
    [data-testid="stSidebar"] [data-testid="stButton"] > button:hover { background: rgba(239,68,68,0.3) !important; color: #ffffff !important; }
    .sidebar-bottom { margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.15); }
    [data-testid="stSidebar"] .sidebar-bottom { margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.15); }
    [data-testid="stSidebar"] .sidebar-bottom [data-testid="stButton"] > button { background: rgba(239,68,68,0.2) !important; color: #fca5a5 !important; border: 1px solid rgba(239,68,68,0.3) !important; border-radius: 10px !important; padding: 10px 16px !important; font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
    [data-testid="stSidebar"] .sidebar-bottom [data-testid="stButton"] > button:hover { background: rgba(239,68,68,0.3) !important; color: #ffffff !important; }
    .login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 20px; margin: 0; position: fixed; top: 0; left: 0; right: 0; bottom: 0; }
    .login-card { background: #ffffff; border-radius: 24px; padding: 40px 36px; width: 100%; max-width: 380px; box-shadow: 0 25px 80px -15px rgba(34,197,94,0.2), 0 10px 30px -10px rgba(0,0,0,0.1); border: 1px solid rgba(34,197,94,0.1); text-align: center; margin: auto; }
    .login-logo { width: 64px; height: 64px; background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 20px; box-shadow: 0 10px 28px rgba(34,197,94,0.35); text-align: center; }
    .login-title { font-family: 'Outfit', sans-serif; font-size: 26px; font-weight: 700; color: #14532d; margin: 0 0 6px 0; letter-spacing: -0.02em; }
    .login-subtitle { font-size: 13px; color: #78716c; margin: 0 0 28px 0; }
    .stTextInput > div { border-radius: 12px !important; border: 2px solid #e2e8f0 !important; transition: all 0.2s ease !important; }
    .stTextInput input { border: none !important; padding: 14px 16px !important; font-size: 14px !important; }
    .stTextInput > div:focus-within { border-color: #22c55e !important; box-shadow: 0 0 0 4px rgba(34,197,94,0.1) !important; }
    .stFormSubmitButton { display: flex !important; justify-content: center !important; }
    .stFormSubmitButton > button { width: auto !important; min-width: 140px; background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important; color: #ffffff !important; border: none !important; border-radius: 12px !important; padding: 14px !important; font-family: 'Outfit', sans-serif !important; font-weight: 600 !important; font-size: 15px !important; box-shadow: 0 8px 24px rgba(34,197,94,0.35) !important; transition: all 0.2s ease !important; margin-top: 8px; }
    .stFormSubmitButton > button:hover { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(34,197,94,0.45) !important; }
    .page-header { background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-radius: 16px; padding: 24px 32px; margin-bottom: 24px; box-shadow: 0 4px 20px -2px rgba(34,197,94,0.08); border: 1px solid #e2e8f0; }
    .page-title { font-family: 'Outfit', sans-serif; font-size: 26px; font-weight: 700; color: #14532d; margin: 0; }
    .page-subtitle { font-size: 14px; color: #78716c; margin: 6px 0 0 0; }
    .stCard { background: #ffffff; border-radius: 16px; box-shadow: 0 4px 20px -2px rgba(34,197,94,0.08); border: 1px solid #e2e8f0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    [data-testid="stMetricValue"] { font-family: 'Outfit', sans-serif; font-weight: 700; color: #22c55e; font-size: 30px !important; }
    [data-testid="stMetricLabel"] { font-weight: 500; color: #78716c; }
    </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Riego Extractor", page_icon="💧", layout="wide")
    inject_css()
    
    if 'page' not in st.session_state:
        st.session_state.page = 'Extraer'
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if st.query_params.get("logout") == "1":
        logout_user()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.page = 'Extraer'
        st.query_params.clear()
        st.rerun()
    
    if not st.session_state.authenticated:
        show_login()
    else:
        show_app()


def show_login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="login-card">
        <div class="login-logo">💧</div>
        <h1 class="login-title">RIEGO EXTRACTOR</h1>
        <p class="login-subtitle">Sistema de Gestión de Riego</p>
    """, unsafe_allow_html=True)
    
    with st.form("login", clear_on_submit=False):
        email = st.text_input("Email", placeholder="tu@email.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
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
    
    st.markdown('</div></div>', unsafe_allow_html=True)


def show_app():
    # Handle logout first
    if st.query_params.get("logout") == "1":
        logout_user()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.page = 'Extraer'
        st.query_params.clear()
        st.rerun()
    
    current = st.session_state.page
    
    with st.sidebar:
        st.markdown('<p class="sidebar-title">RIEGO EXTRACTOR v1.7</p>', unsafe_allow_html=True)
        
        # Navigation using selectbox
        selected = st.selectbox(
            "Navegación",
            options=["Extraer", "Programar", "Mantenimiento"],
            index=["Extraer", "Programar", "Mantenimiento"].index(current),
            format_func=lambda x: {"Extraer": "📋  Extraer Riegos", "Programar": "🗓️  Programar Horarios", "Mantenimiento": "🔧  Mantenimiento"}[x],
            label_visibility="collapsed",
            key="nav_select"
        )
        
        if selected != st.session_state.page:
            st.session_state.page = selected
            st.rerun()
        
        st.markdown('<div class="sidebar-bottom">', unsafe_allow_html=True)
        
        if st.button("🚪  Cerrar Sesión", key="logout_btn"):
            st.query_params["logout"] = "1"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
