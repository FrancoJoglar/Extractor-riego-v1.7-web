"""
Módulo de Estado Global
Gestiona el estado de la aplicación de forma centralizada.
"""
import streamlit as st


class AppState:
    """Gestor de estado de la aplicación."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._init_session_state()
    
    def _init_session_state(self):
        """Inicializa el estado de la sesión."""
        defaults = {
            'current_page': 'Extraer',
            'authenticated': False,
            'user': None,
            'supabase_session': None,
            'extracted_data': None,
            'schedule_data': None,
            'cache_loaded': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @property
    def current_page(self) -> str:
        return st.session_state.current_page
    
    @current_page.setter
    def current_page(self, value: str):
        st.session_state.current_page = value
    
    @property
    def is_authenticated(self) -> bool:
        return st.session_state.authenticated
    
    @property
    def user(self) -> dict:
        return st.session_state.user
    
    @property
    def extracted_data(self):
        return st.session_state.extracted_data
    
    @extracted_data.setter
    def extracted_data(self, value):
        st.session_state.extracted_data = value
    
    @property
    def schedule_data(self):
        return st.session_state.schedule_data
    
    @schedule_data.setter
    def schedule_data(self, value):
        st.session_state.schedule_data = value
    
    def clear_data(self):
        """Limpia los datos en caché."""
        st.session_state.extracted_data = None
        st.session_state.schedule_data = None


# Instancia global
app_state = AppState()
