"""
Página de Programar Horarios.
Permite obtener datos de Supabase y calcular horarios de riego.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# Importar módulos de lógica
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.schedule_logic import generate_schedule


def show():
    """Muestra la página de programar horarios."""
    st.title("📅 Programar Horarios")
    st.markdown("Calcula horarios de inicio para los riegos pendientes.")
    
    # Inicializar estado
    if 'schedule_df' not in st.session_state:
        st.session_state.schedule_df = None
    
    # Selector de fecha
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**Fecha de Programación:**")
        date_option = st.radio(
            "Seleccionar",
            ["Hoy", "Mañana", "Fecha específica"]
        )
        
        if date_option == "Hoy":
            selected_date = datetime.now().strftime("%Y-%m-%d")
        elif date_option == "Mañana":
            tomorrow = datetime.now() + timedelta(days=1)
            selected_date = tomorrow.strftime("%Y-%m-%d")
        else:
            selected_date_obj = st.date_input("Seleccionar fecha", datetime.now() + timedelta(days=1))
            selected_date = selected_date_obj.strftime("%Y-%m-%d")
        
        st.info(f"Fecha seleccionada: **{selected_date}**")
    
    with col2:
        st.markdown("**Acciones:**")
        
        col_bt1, col_bt2 = st.columns(2)
        
        with col_bt1:
            if st.button("📥 Obtener Datos de Supabase", type="primary"):
                with st.spinner("Obteniendo datos..."):
                    try:
                        from modules.schedule_logic import get_schedule_data
                        df = get_schedule_data(selected_date, log_callback=st.info)
                        
                        if not df.empty:
                            st.session_state.schedule_df = df
                            st.success(f"✅ {len(df)} registros obtenidos")
                        else:
                            st.warning(f"No hay riegos pendientes para {selected_date}")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col_bt2:
            if st.button("📅 Calcular Horarios", type="primary"):
                if st.session_state.schedule_df is None or st.session_state.schedule_df.empty:
                    st.error("Primero debes obtener los datos de Supabase")
                else:
                    with st.spinner("Calculando horarios..."):
                        try:
                            df = generate_schedule(selected_date, log_callback=st.info)
                            st.session_state.schedule_df = df
                            st.success("✅ Horarios calculados")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    # Mostrar resultados
    if st.session_state.schedule_df is not None:
        df = st.session_state.schedule_df
        
        # Filtrar solo los que tienen hora calculada
        if 'Hora Inicio' in df.columns:
            df_with_hours = df[df['Hora Inicio'].notna() & (df['Hora Inicio'] != '')]
        else:
            df_with_hours = df
        
        st.markdown("---")
        
        if df_with_hours.empty:
            st.subheader(f"📊 Datos Obtenidos ({len(df)} registros sin horarios)")
            st.dataframe(df, use_container_width=True, height=300)
        else:
            st.subheader(f"📊 Programación ({len(df_with_hours)} registros)")
            
            # Mostrar preview con columnas importantes
            display_cols = ['fecha_solicitado', 'equipo_nombre', 'sector_nombre', 
                          'jefe_campo', 'horas_solicitadas', 'm3_estimados', 
                          'con_fertilizante', 'Hora Inicio', 'Tipo Programación']
            
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(
                df_with_hours[available_cols],
                use_container_width=True,
                height=400
            )
            
            # Métricas
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Riegos", len(df_with_hours))
            with col_b:
                total_hrs = df_with_hours['horas_solicitadas'].sum()
                st.metric("Horas Totales", f"{total_hrs:.1f}")
            with col_c:
                equipos = df_with_hours['equipo_nombre'].nunique()
                st.metric("Equipos", equipos)
            
            # Descarga
            st.markdown("---")
            
            # Preparar Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_with_hours.to_excel(writer, index=False, sheet_name='Programación')
            
            st.download_button(
                label="📥 Descargar Programación",
                data=buffer.getvalue(),
                file_name=f"programacion_{selected_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        
        # Botón limpiar
        if st.button("🗑️ Limpiar"):
            st.session_state.schedule_df = None
            st.rerun()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    show()
