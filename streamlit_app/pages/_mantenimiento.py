"""
Página de Mantenimiento.
Permite limpiar la tabla de riegos_solicitados.
"""
import streamlit as st

# Importar módulos de lógica
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.supabase_sync import clear_supabase_table


def show():
    """Muestra la página de mantenimiento."""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <span style="font-size: 2.5rem;">⚙️</span>
    </div>
    <h1 style="text-align: center; color: #2E7D32 !important;">Mantenimiento</h1>
    <p style="text-align: center; color: #388E3C; font-size: 1.1rem;">
        Herramientas de administración de la base de datos
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sección de limpieza
    st.subheader("🗑️ Limpiar Tabla Riegos Solicitados")
    
    st.warning("⚠️ **Esta acción es IRREVERSIBLE**")
    st.markdown("""
    Al presionar el botón se eliminarán **todos** los registros de la tabla 
    `riegos_solicitados` en Supabase. Esto incluye:
    - Todos los riegos pendientes
    - Todos los riegos ya programados
    - Historial completo
    """)
    
    # Primera confirmación
    if 'first_confirm' not in st.session_state:
        st.session_state.first_confirm = False
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if not st.session_state.first_confirm:
            if st.button("🗑️ Iniciar Limpieza", type="secondary"):
                st.session_state.first_confirm = True
                st.rerun()
        else:
            st.error("⚠️ ¿Estás seguro?")
            
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Sí, quiero borrar todo", type="primary"):
                    with st.spinner("Eliminando registros..."):
                        result = clear_supabase_table(log_callback=st.info)
                        
                        if result['success']:
                            st.success(f"✅ {result['count']} registros eliminados")
                        else:
                            st.error(f"❌ Error: {result['error']}")
                        
                        st.session_state.first_confirm = False
                        st.rerun()
            
            with col_no:
                if st.button("❌ Cancelar", type="secondary"):
                    st.session_state.first_confirm = False
                    st.rerun()
    
    with col2:
        st.markdown("""
        ### Alternativas recomendadas
        
        En lugar de borrar todo, considera:
        
        1. **Filtrar por fecha** - Borra solo registros antiguos
        2. **Cambiar estado** - Marca como "cancelado" en lugar de borrar
        3. **Exportar primero** - Haz backup antes de limpiar
        
        Contacta al administrador para estas opciones.
        """)
    
    st.markdown("---")
    
    # Información del sistema
    st.subheader("ℹ️ Información del Sistema")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("**Versión de la App:**")
        st.code("Riego Extractor v1.5 - Web (Streamlit)")
        
        st.markdown("**Tablas en Supabase:**")
        st.code("- riegos_solicitados\n- vista_riegos_solicitados\n- fundos\n- equipos\n- sectores\n- personas")
    
    with col_info2:
        st.markdown("**Configuración actual:**")
        
        try:
            st.markdown("- **Supabase URL:** Configurada ✅")
            st.markdown("- **Auth:** Habilitado ✅")
        except:
            st.markdown("- **Supabase URL:** Revisar secrets.toml ❌")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    show()
