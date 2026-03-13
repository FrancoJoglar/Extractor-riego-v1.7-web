"""
Módulo de Programación de Horarios.
Wrapper de la lógica de programar_horarios.py para uso en Streamlit.
"""
import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime


def get_supabase_client() -> Client:
    """Crea cliente Supabase desde st.secrets."""
    import os
    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas")
    
    return create_client(url, key)


def formatear_hora(hora_float: float) -> str:
    """Convierte hora float (6.5) a string HH:MM."""
    horas = int(hora_float)
    minutos = int(round((hora_float - horas) * 60))
    if horas >= 24:
        horas = horas - 24
    if horas == 0 and minutos == 0:
        minutos = 1
    return f"{horas:02d}:{minutos:02d}"


def es_fertilizante(val) -> bool:
    """Convierte valor a booleano."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.upper() in ['TRUE', 'VERDADERO', '1', 'YES', 'S', 'SI']
    return bool(val)


def calcular_horario(equipo_df: pd.DataFrame) -> dict:
    """
    Calcula horarios para un equipo con la lógica:
    1. Sectores CON fert: 06:00 - 16:00 (SECUENCIAL)
    2. Sectores SIN fert: después de CON fert
    3. Si total > 14h: cálculo hacia atrás desde 06:00 para SIN fert
    """
    resultados = {}
    hora_termino_fert = 6.0
    
    equipo_df = equipo_df.copy()
    equipo_df['con_fertilizante'] = equipo_df['con_fertilizante'].apply(es_fertilizante)
    
    total_horas = equipo_df['horas_solicitadas'].sum()
    
    # Extraer número de sector
    if 'sector_nombre' in equipo_df.columns:
        equipo_df['sector_num'] = equipo_df['sector_nombre'].str.extract(r'S(\d+)').astype(float)
    else:
        equipo_df['sector_num'] = 1
    
    sectores_con_fert = equipo_df[equipo_df['con_fertilizante'] == True].sort_values('sector_num')
    sectores_sin_fert = equipo_df[equipo_df['con_fertilizante'] == False].sort_values('sector_num')
    
    tiene_fertilizante = len(sectores_con_fert) > 0
    
    # 1. PROGRAMAR CON FERTILIZACIÓN
    if len(sectores_con_fert) > 0:
        horas_por_sector = []
        for idx, row in sectores_con_fert.iterrows():
            horas_por_sector.append({'idx': idx, 'horas': row['horas_solicitadas'], 'sector': row.get('sector_nombre', f'S{row.get("sector_num", "?")}')})
        
        hora_actual = 6.0
        for item in horas_por_sector:
            hora_fin = hora_actual + item['horas']
            resultados[item['idx']] = {
                'Hora Inicio': formatear_hora(hora_actual),
                'Tipo': "Horario Inicio" if hora_actual == 6.0 else "Secuencial"
            }
            hora_actual += item['horas']
        
        hora_termino_fert = hora_actual
    
    # 2. PROGRAMAR SIN FERTILIZACIÓN
    if len(sectores_sin_fert) > 0:
        if tiene_fertilizante:
            hora_actual = hora_termino_fert
        elif total_horas > 14:
            primera_hora = sectores_sin_fert['horas_solicitadas'].iloc[0]
            hora_actual = 6.0 - primera_hora
            if hora_actual < 0:
                hora_actual = 0
        else:
            hora_actual = 6.0
        
        primer_sector = len(resultados) == 0
        
        for idx, row in sectores_sin_fert.iterrows():
            horas_req = row['horas_solicitadas']
            resultados[idx] = {
                'Hora Inicio': formatear_hora(hora_actual),
                'Tipo': 'Horario Inicio' if primer_sector else 'Secuencial'
            }
            hora_actual += horas_req
            primer_sector = False
    
    return resultados


def get_schedule_data(fecha: str, log_callback=print) -> pd.DataFrame:
    """
    Obtiene datos de riegos pendientes de Supabase para una fecha.
    
    Args:
        fecha: Fecha en formato YYYY-MM-DD
        log_callback: Función para logs
    
    Returns:
        DataFrame con los datos
    """
    try:
        supabase = get_supabase_client()
        log_callback(f"Obteniendo datos para fecha: {fecha}")
        
        response = supabase.table("vista_riegos_solicitados").select("*").eq("estado", "pendiente").eq("fecha_solicitado", fecha).execute()
        
        if not response.data:
            log_callback(f"No hay riegos para la fecha {fecha}")
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        log_callback(f"Encontrados {len(df)} registros")
        return df
        
    except Exception as e:
        log_callback(f"Error al obtener datos: {e}")
        raise


def generate_schedule(fecha: str, log_callback=print) -> pd.DataFrame:
    """
    Genera programación de horarios para una fecha.
    
    Args:
        fecha: Fecha en formato YYYY-MM-DD
        log_callback: Función para logs
    
    Returns:
        DataFrame con la programación calculada
    """
    # Obtener datos
    df = get_schedule_data(fecha, log_callback)
    
    if df.empty:
        return df
    
    df = df.copy()
    df['Hora Inicio'] = ""
    df['Tipo Programación'] = ""
    
    # Extraer números de equipo y sector
    if 'equipo_nombre' in df.columns:
        df['equipo_num'] = df['equipo_nombre'].str.extract(r'(\d+)').astype(float)
    if 'sector_nombre' in df.columns:
        df['sector_num'] = df['sector_nombre'].str.extract(r'S(\d+)').astype(float)
    
    # Procesar por equipo
    equipos = df['equipo_num'].unique()
    
    for equipo in sorted(equipos):
        equipo_df = df[df['equipo_num'] == equipo]
        resultados = calcular_horario(equipo_df)
        
        for idx, row in equipo_df.iterrows():
            if idx in resultados:
                df.loc[idx, 'Hora Inicio'] = resultados[idx]['Hora Inicio']
                df.loc[idx, 'Tipo Programación'] = resultados[idx]['Tipo']
    
    # Ordenar por hora de inicio
    df = df.sort_values(by=['equipo_num', 'sector_num'])
    
    return df
