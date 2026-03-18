# 🔒 SEGURIDAD - Riego Extractor

## Configuración de Secrets

### 1. Crear archivo de secrets

```bash
cd streamlit_app/.streamlit
cp secrets.toml.example secrets.toml
```

### 2. Completar credenciales

Editar `secrets.toml`:

```toml
SUPABASE_URL = "https://tu_proyecto.supabase.co"
SUPABASE_KEY = "tu_anon_key"
```

### 3. Obtener credenciales de Supabase

1. Ir a: https://supabase.com/dashboard/project/_/settings/api
2. Copiar "Project URL" y "anon public" key

---

## ⚠️ IMPORTANTE

- **NUNCA** commitear `secrets.toml` al repositorio
- El archivo `.gitignore` ya excluye este archivo
- Si exponés las credenciales, **rotarlas inmediatamente** desde Supabase

---

## Variables de Entorno (Producción)

Para producción, usar variables de entorno en lugar de secrets.toml:

```bash
export SUPABASE_URL="https://tu_proyecto.supabase.co"
export SUPABASE_KEY="tu_anon_key"
export ENVIRONMENT="production"
```

---

## Validación de Inputs

El sistema valida:
- ✅ Formato de email (regex)
- ✅ Longitud mínima de contraseña (6 caracteres)
- ✅ Sanitización de inputs (trim, lowercase)
- ✅ Errores genéricos en producción (no exponen detalles internos)

---

## Manejo de Errores

| Entorno | Comportamiento |
|---------|---------------|
| Desarrollo | Muestra errores detallados |
| Producción | Mensajes genéricos |

Para activar modo producción:
```bash
export ENVIRONMENT=production
```

---

## Checklist de Seguridad

- [ ] secrets.toml creado y configurado
- [ ] Credenciales no commitadas
- [ ] .gitignore incluye secrets
- [ ] ENVIRONMENT=production en producción
