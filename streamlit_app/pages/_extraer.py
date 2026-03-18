"""
Página de Extraer Riegos.
Permite upload de Excel, extracción, sincronización y descarga.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# Importar módulos de lógica
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.extract_logic import process_extraction_streamlit
from modules.supabase_sync import sync_to_supabase


def show():
    """Muestra la página de extraer riegos."""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <span style="font-size: 2.5rem;">📋</span>
    </div>
    <h1 style="text-align: center; color: #2E7D32 !important;">Extraer Riegos desde Excel</h1>
    <p style="text-align: center; color: #388E3C; font-size: 1.1rem;">
        Sube la planilla M3 reales y extrae los datos de riego
    </p>
    """, unsafe_allow_html=True)
    
    # Inicializar estado
    if 'extracted_df' not in st.session_state:
        st.session_state.extracted_df = None
    
    # Columnas para layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Upload de archivo
        uploaded_file = st.file_uploader(
            "Seleccionar planilla Excel (.xlsx)",
            type=["xlsx"],
            help="Archivo de planilla M3 reales de riego"
        )
    
    with col2:
        # Selector de fecha
        st.markdown("**Rango de Fechas:**")
        date_option = st.radio(
            "Seleccionar",
            ["Hoy", "Mañana", "Rango personalizado"]
        )
        
        if date_option == "Hoy":
            date_str = datetime.now().strftime("%Y-%m-%d")
        elif date_option == "Mañana":
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime("%Y-%m-%d")
        else:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_date = st.date_input("Desde", datetime.now())
            with col_d2:
                end_date = st.date_input("Hasta", datetime.now())
            date_str = f"{start_date}:{end_date}"
    
    # Botón procesar
    if uploaded_file and st.button("🔍 Procesar Planilla", type="primary"):
        with st.spinner("Procesando..."):
            try:
                # Leer archivo
                file_bytes = uploaded_file.getvalue()
                
                # Procesar
                df = process_extraction_streamlit(
                    file_bytes,
                    date_str,
                    log_callback=st.info
                )
                
                if not df.empty:
                    st.session_state.extracted_df = df
                    st.success(f"✅ {len(df)} registros extraídos")
                else:
                    st.warning("No se encontraron datos para las fechas especificadas.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Mostrar resultados
    if st.session_state.extracted_df is not None:
        df = st.session_state.extracted_df
        
        st.markdown("---")
        st.subheader(f"📊 Resultados ({len(df)} registros)")
        
        # Preview
        st.dataframe(
            df[['Fecha', 'Fundo', 'Nombre Sector', 'equipo', 'sector', 'horas', 'M3', 'Con Fertilizante']],
            use_container_width=True,
            height=300
        )
        
        # Métricas
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Riegos", len(df))
        with col_b:
            total_hrs = df['horas'].sum()
            st.metric("Horas Totales", f"{total_hrs:.1f}")
        with col_c:
            total_m3 = df['M3'].sum()
            st.metric("M3 Totales", f"{total_m3:.0f}")
        
        # Acciones
        st.markdown("---")
        st.subheader("Acciones")
        
        col_sync, col_dl = st.columns(2)
        
        with col_sync:
            if st.button("☁️ Sincronizar a Supabase", type="primary"):
                with st.spinner("Sincronizando..."):
                    result = sync_to_supabase(df, log_callback=st.info)
                    
                    if result['success']:
                        st.success(f"✅ {result['count']} registros subidos a Supabase")
                        if result['errors']:
                            st.warning(f"⚠️ {len(result['errors'])} registros omitidos")
                    else:
                        st.error(f"❌ Error: {result['errors']}")
        
        with col_dl:
            # Convertir a Excel para download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Riegos Extraidos')
            
            st.download_button(
                label="📥 Descargar Excel",
                data=buffer.getvalue(),
                file_name=f"riegos_extraidos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="secondary"
            )
        
        # Botón limpiar
        if st.button("🗑️ Limpiar Resultados"):
            st.session_state.extracted_df = None
            st.rerun()


# Allow running as standalone for testing
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    show()
