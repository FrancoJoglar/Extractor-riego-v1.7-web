"""
Navegación de la aplicación.
Define las rutas y maneja la navegación.
"""
import streamlit as st
from typing import Dict, Callable, Any


class Navigation:
    """Gestor de navegación."""
    
    PAGES = {
        "Extraer": {
            "title": "Extraer Riegos",
            "icon": "📋",
            "module": "pages/_extraer.py"
        },
        "Programar": {
            "title": "Programar Horarios", 
            "icon": "📅",
            "module": "pages/_programar.py"
        },
        "Mantenimiento": {
            "title": "Mantenimiento",
            "icon": "⚙️",
            "module": "pages/_mantenimiento.py"
        }
    }
    
    @staticmethod
    def get_current_page() -> str:
        """Obtiene la página actual."""
        return st.session_state.get('current_page', 'Extraer')
    
    @staticmethod
    def set_page(page_key: str):
        """Cambia a una página específica."""
        st.session_state.current_page = page_key
        st.rerun()
    
    @staticmethod
    def get_pages() -> Dict[str, Dict[str, str]]:
        """Retorna las páginas disponibles."""
        return Navigation.PAGES
