"""
Componente Sidebar.
Solo maneja navegación - SIN lógica de negocio.
"""
import streamlit as st


class Sidebar:
    """Componente Sidebar - Solo Navegación."""
    
    def __init__(self):
        self.pages = {
            "Extraer": {"icon": "📋", "label": "Extraer Riegos"},
            "Programar": {"icon": "📅", "label": "Programar Horarios"},
            "Mantenimiento": {"icon": "⚙️", "label": "Mantenimiento"}
        }
    
    def render(self):
        """Renderiza el sidebar."""
        with st.sidebar:
            # Título
            st.markdown("""
            <div style="text-align: center; padding: 10px; background: #1B5E20; border-radius: 10px; margin-bottom: 20px;">
                <span style="font-size: 30px;">🌱</span><br>
                <span style="color: white; font-weight: bold; font-size: 18px;">RIEGO EXTRACTOR</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Usuario
            if st.session_state.user:
                email = st.session_state.user.get('email', 'Usuario')
                st.markdown(f"""
                <div style="text-align: center; background: white; padding: 10px; border-radius: 10px; margin-bottom: 15px;">
                    <div style="font-size: 24px;">👤</div>
                    <div style="font-size: 11px; color: #1B5E20;">{email}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navegación
            st.markdown("### NAVEGACIÓN")
            
            current = st.session_state.get('current_page', 'Extraer')
            
            for key, info in self.pages.items():
                icon = info["icon"]
                label = info["label"]
                
                # Resaltar página actual
                is_active = (key == current)
                
                btn_style = """
                background: #4CAF50; 
                color: white; 
                border: none;
                padding: 12px;
                border-radius: 8px;
                width: 100%;
                font-weight: bold;
                cursor: pointer;
                """ if is_active else """
                background: transparent;
                color: white;
                border: 1px solid white;
                padding: 12px;
                border-radius: 8px;
                width: 100%;
                cursor: pointer;
                """
                
                if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.current_page = key
                    st.rerun()
            
            st.markdown("---")
            
            # Cerrar sesión
            if st.button("🚪 Cerrar Sesión", use_container_width=True, key="logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.current_page = 'Extraer'
                st.rerun()


# Instancia global
sidebar = Sidebar()
