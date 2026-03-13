import pandas as pd
from supabase import create_client, Client
import os

# Configuración de Supabase
SUPABASE_URL = "https://miikjrfqmmkzknyngwen.supabase.co"
SUPABASE_KEY = "sb_publishable_tixCrY6poQrVDEzeRuDhow_ND7tvVCQ" # Usamos la key pública
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ruta del archivo Excel
file_path = r"G:\Otros ordenadores\Mi portátil\Trabajo\Riegos Siracusa Semana 9.xlsx"

def upload_riego_data():
    print(f"Cargando datos desde: {file_path}")
    
    # 1. Leer Excel
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error al leer el Excel: {e}")
        return

    # 2. Obtener Maestros de Supabase para mapeo
    print("Obteniendo maestros de Supabase...")
    fundos_resp = supabase.table("fundos").select("id, nombre").execute()
    equipos_resp = supabase.table("equipos").select("id, nombre").execute()
    # Obtenemos sectores incluyendo el nombre del jefe de campo (via relación FK)
    sectores_resp = supabase.table("sectores").select("id, nombre, personas(nombre)").execute()

    fundo_map = {f['nombre']: f['id'] for f in fundos_resp.data}
    equipo_map = {e['nombre']: e['id'] for e in equipos_resp.data}
    
    # Mapeo de nombre -> (id, jefe)
    sector_map = {}
    for s in sectores_resp.data:
        jefe = s['personas']['nombre'] if s.get('personas') else "Sin Jefe"
        sector_map[s['nombre']] = (s['id'], jefe)

    # 3. Procesar filas
    registros_a_subir = []
    print("Procesando filas...")
    
    for index, row in df.iterrows():
        # Limpiar datos básicos
        fundo_nombre = str(row['Fundo']).strip()
        equipo_num = str(row['Equipo']).strip()
        sector_num = str(row['Sector']).strip()
        
        # Lógica de identificación
        fundo_id = fundo_map.get(fundo_nombre)
        equipo_nombre_busqueda = f"Equipo {equipo_num}"
        equipo_id = equipo_map.get(equipo_nombre_busqueda)
        
        # Construir nombre del sector (E1S3)
        sector_nombre_busqueda = f"E{equipo_num}S{sector_num}"
        sector_info = sector_map.get(sector_nombre_busqueda)

        # Validaciones
        if not fundo_id or not sector_info:
            print(f"Aviso: Fila {index+2} omitida. No se encontró Fundo '{fundo_nombre}' o Sector '{sector_nombre_busqueda}'")
            continue
        
        sector_id, jefe_nombre = sector_info

        # Preparar registro
        registro = {
            "fundo_id": fundo_id,
            "equipo_id": equipo_id, # Aunque la vista lo ignore, lo guardamos por integridad
            "sector_id": sector_id,
            "fecha_solicitado": str(row['Fecha']).split(' ')[0], # Solo la parte de la fecha
            "horas_solicitadas": float(row['Horas']) if pd.notna(row['Horas']) else 0,
            "m3_estimados": float(row['M3']) if pd.notna(row['M3']) else 0,
            "con_fertilizante": True if str(row['Con Fertilizante']).lower() == 'si' else False,
            "estado": "pendiente"
        }
        registros_a_subir.append(registro)

    # 4. Subir a Supabase con control de duplicados
    if registros_a_subir:
        print(f"Subiendo {len(registros_a_subir)} registros (saltando duplicados)...")
        try:
            # Usamos upsert con on_conflict para que si ya existe la combinación 
            # Fecha + Sector + Horas, no lo inserte de nuevo.
            result = supabase.table("riegos_solicitados").upsert(
                registros_a_subir, 
                on_conflict="fecha_solicitado, sector_id, horas_solicitadas"
            ).execute()
            print("¡Carga completada con éxito! (Los duplicados fueron ignorados o actualizados)")
        except Exception as e:
            print(f"Error al subir a Supabase: {e}")
    else:
        print("No se encontraron registros válidos para subir.")

if __name__ == "__main__":
    # Puedes cambiar la ruta aquí para el archivo más grande
    # file_path = r"G:\Otros ordenadores\Mi portátil\Trabajo\Historial_Octubre.xlsx" 
    upload_riego_data()
