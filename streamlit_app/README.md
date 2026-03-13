# Riego Extractor - Streamlit Web App

Aplicación web para extraer, programar y sincronizar riegos con Supabase.

## Estructura

```
streamlit_app/
├── app.py                    # Entry point + autenticación
├── pages/
│   ├── 1_extraer.py          # Extraer riegos desde Excel
│   ├── 2_programar.py       # Programar horarios
│   └── 3_mantenimiento.py    # Limpieza de tabla
├── modules/
│   ├── auth.py               # Autenticación Supabase
│   ├── extract_logic.py       # Lógica de extracción
│   ├── supabase_sync.py      # Upload/clear a Supabase
│   └── schedule_logic.py     # Cálculo de horarios
├── requirements.txt          # Dependencias Python
└── .streamlit/
    ├── config.toml           # Configuración de Streamlit
    └── secrets.toml          # Credenciales (NO commitear!)
```

## Instalación

```bash
# 1. Instalar dependencias
cd streamlit_app
pip install -r requirements.txt

# 2. Configurar credenciales
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Editar secrets.toml con tus credenciales de Supabase

# 3. Ejecutar localmente
streamlit run app.py
```

## Configuración de Supabase

1. Ve a **Supabase Dashboard** → tu proyecto
2. **Settings** → **API**
3. Copia:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`

## Deployment

### Streamlit Cloud (Recomendado)

1. Sube el código a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Configura los secrets en Settings:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

### Docker

```dockerfile
FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

## Funcionalidades

| Página | Descripción |
|--------|-------------|
| **Login** | Autenticación con Supabase Auth |
| **Extraer** | Upload Excel M3 → Preview → Sync a Supabase → Download |
| **Programar** | Obtener datos de Supabase → Calcular horarios → Download |
| **Mantenimiento** | Limpiar tabla riegos_solicitados |

## Notas

- La lógica de extracción fue refactorizada de la app desktop original
- La autenticación usa Supabase Auth (mismo provider que la DB)
- Los archivos se procesan en memoria (no se guardan en servidor)
