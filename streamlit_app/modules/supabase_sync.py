"""
Módulo de Sincronización con Supabase.
Funciones para upload y clear de la tabla riegos_solicitados.
"""
import streamlit as st
from supabase import create_client, Client
import pandas as pd


def get_supabase_client() -> Client:
    """Crea cliente Supabase desde st.secrets."""
    import os
    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas")
    
    return create_client(url, key)


def sync_to_supabase(df: pd.DataFrame, log_callback=print) -> dict:
    """
    Sincroniza DataFrame a Supabase (tabla riegos_solicitados).
    
    Args:
        df: DataFrame con columnas: Fundo, Nombre Sector, Fecha, Horas, M3, Con Fertilizante
        log_callback: Función para logs
    
    Returns:
        dict con keys: success (bool), count (int), errors (list)
    """
    try:
        supabase = get_supabase_client()
        log_callback("Conectando con Supabase...")
        
        # 1. Obtener Maestros para mapeo
        fundos_resp = supabase.table("fundos").select("id, nombre").execute()
        sectores_resp = supabase.table("sectores").select("id, nombre, equipo_id").execute()
        
        fundo_map = {f['nombre']: f['id'] for f in fundos_resp.data}
        sector_map = {s['nombre']: s['id'] for s in sectores_resp.data}
        sector_to_eq = {s['nombre']: s['equipo_id'] for s in sectores_resp.data}
        
        # 2. Preparar registros
        registros = []
        errors = []
        
        for _, row in df.iterrows():
            fundo_id = fundo_map.get(row.get('Fundo'))
            nom_sector = row.get('Nombre Sector')
            sector_id = sector_map.get(nom_sector)
            equipo_id = sector_to_eq.get(nom_sector)
            
            if fundo_id and sector_id:
                registros.append({
                    "fundo_id": fundo_id,
                    "equipo_id": equipo_id,
                    "sector_id": sector_id,
                    "fecha_solicitado": str(row.get('Fecha')),
                    "horas_solicitadas": float(row.get('Horas', 0)),
                    "m3_estimados": float(row.get('M3', 0)) if pd.notna(row.get('M3')) else 0,
                    "con_fertilizante": True if row.get('Con Fertilizante') == "Si" else False,
                    "estado": "pendiente"
                })
            else:
                errors.append(f"Falta mapeo para: {nom_sector} ({row.get('Fundo')})")
        
        if not registros:
            return {
                "success": False,
                "count": 0,
                "errors": errors or ["No hay registros válidos para sincronizar"]
            }
        
        # 3. Subir a Supabase
        log_callback(f"Sincronizando {len(registros)} registros...")
        supabase.table("riegos_solicitados").upsert(
            registros,
            on_conflict="fecha_solicitado, sector_id, horas_solicitadas"
        ).execute()
        
        return {
            "success": True,
            "count": len(registros),
            "errors": errors
        }
        
    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "errors": [f"Error de conexión: {str(e)}"]
        }


def clear_supabase_table(log_callback=print) -> dict:
    """
    Borra todos los registros de la tabla riegos_solicitados.
    
    Returns:
        dict con keys: success (bool), count (int), error (str)
    """
    try:
        supabase = get_supabase_client()
        log_callback("Conectando a Supabase para limpieza...")
        
        # Primero contar cuántos hay
        count_resp = supabase.table("riegos_solicitados").select("*", count="exact").execute()
        count = count_resp.count or 0
        
        if count == 0:
            return {
                "success": True,
                "count": 0,
                "error": None
            }
        
        # Borrar todos los registros
        resp = supabase.table("riegos_solicitados").delete().neq("id", -1).execute()
        
        deleted_count = len(resp.data) if hasattr(resp, 'data') and resp.data else count
        
        log_callback(f"✅ Eliminados {deleted_count} registros")
        
        return {
            "success": True,
            "count": deleted_count,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "error": str(e)
        }
