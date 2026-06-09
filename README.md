# 🧠 Psiconefrología – Sistema de Gestión Clínica

**Hospital Nacional Ramiro Prialé Prialé – EsSalud, Huancayo**  
Stack: **FastAPI** · **Supabase (PostgreSQL)** · **Render** · **HTML/JS vanilla**

---

## Estructura del Proyecto

```
psiconefrologia/
├── backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── database.py              ← Cliente Supabase
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py           ← Pydantic models
│   ├── routers/
│   │   ├── agenda.py            ← GET/POST /api/agenda, /api/kpi
│   │   ├── pacientes.py         ← GET /api/pacientes/buscar, CRUD
│   │   ├── fichas.py            ← GET/POST /api/fichas, PDF
│   │   ├── sala.py              ← GET/POST /api/sala
│   │   ├── atenciones.py        ← GET/POST /api/atenciones
│   │   ├── evolucion.py         ← GET/POST /api/evolucion, PDF historia
│   │   ├── admin.py             ← GET /api/admin/stats
│   │   ├── informes.py          ← GET /api/informe, /pdf, /word
│   │   ├── mantenimiento.py     ← POST /api/mantenimiento
│   │   └── status.py            ← GET /api/status
│   └── utils/
│       ├── pdf_generator.py     ← ReportLab: ficha + informe PDF
│       └── word_generator.py    ← python-docx: informe Word
├── frontend/
│   └── index.html               ← psiconefrologia_v2.html (renombrado)
├── supabase_schema.sql          ← SQL para crear las tablas
├── render.yaml                  ← Configuración de deploy
└── .gitignore
```

---

## Guía de Deploy Paso a Paso

### 1 · Supabase (base de datos)

1. Crea una cuenta en [supabase.com](https://supabase.com) y un nuevo proyecto.
2. Ve a **SQL Editor → New query**, pega el contenido de `supabase_schema.sql` y ejecuta.
3. Verifica en **Table Editor** que aparecen las 6 tablas:  
   `pacientes`, `agenda`, `fichas`, `sala_maquinas`, `atenciones`, `evolucion`
4. Ve a **Settings → API** y copia:
   - `Project URL` → esto es tu `SUPABASE_URL`
   - `service_role` key → esto es tu `SUPABASE_SERVICE_KEY` (¡nunca expongas esto en el frontend!)
   - `anon public` key → esto es tu `SUPABASE_ANON` para el frontend HTML

5. Ve a **Authentication → Users → Add user** y crea el usuario:
   - Email: `psiconefro@essalud.gob.pe`
   - Password: el que elijas (actualiza también en el HTML)

---

### 2 · Preparar el repositorio GitHub

```bash
git init
git add .
git commit -m "feat: psiconefrología v2 full stack"
git remote add origin https://github.com/SebasPsy13/psiconefrologia.git
git push -u origin main
```

> ⚠️ **Antes de hacer push**: asegúrate de que `.gitignore` incluye `.env` y que  
> el `index.html` tiene `SUPABASE_URL` y `SUPABASE_ANON` correctos (anon key, no service key).

---

### 3 · Actualizar el HTML con tus claves reales

En `frontend/index.html`, reemplaza al inicio del `<script>`:

```javascript
const SUPABASE_URL  = 'https://XXXXXXXXXXXXXX.supabase.co';  // ← tu URL
const SUPABASE_ANON = 'eyJhbGciOi...';                        // ← tu anon key
const API_BASE      = 'https://psiconefrologia-api.onrender.com/api';
```

---

### 4 · Render (backend + frontend)

1. Ve a [render.com](https://render.com) → **New → Web Service**
2. Conecta tu repositorio de GitHub (`SebasPsy13/psiconefrologia`)
3. Configura:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. En **Environment Variables**, agrega:
   ```
   SUPABASE_URL          = https://XXXXXX.supabase.co
   SUPABASE_SERVICE_KEY  = eyJhbGciOi...  (service_role key)
   CORS_ORIGINS          = *
   ENVIRONMENT           = production
   RENDER                = true
   ```
5. Haz clic en **Create Web Service** → el deploy tarda ~3 minutos.
6. El backend quedará disponible en:  
   `https://psiconefrologia-api.onrender.com`

#### Servir el frontend

Tienes dos opciones:

**Opción A (recomendada – mismo servidor):**  
Pon `index.html` en la carpeta `frontend/` del repo.  
FastAPI lo sirve automáticamente en la raíz `/`.  
URL final: `https://psiconefrologia-api.onrender.com`

**Opción B (Render Static Site separado):**  
New → Static Site → apunta a la carpeta `frontend/`.  
Publish directory: `frontend`.

---

### 5 · Verificar que todo funciona

```bash
# Health check
curl https://psiconefrologia-api.onrender.com/health

# Estado del sistema
curl https://psiconefrologia-api.onrender.com/api/status

# KPI del día
curl "https://psiconefrologia-api.onrender.com/api/kpi?fecha=2026-06-09"

# Buscar paciente
curl "https://psiconefrologia-api.onrender.com/api/pacientes/buscar?q=40123456"
```

---

## Variables de Entorno Requeridas

| Variable              | Descripción                          | Dónde configurar |
|-----------------------|--------------------------------------|------------------|
| `SUPABASE_URL`        | URL del proyecto Supabase            | Render → Env     |
| `SUPABASE_SERVICE_KEY`| service_role key (solo backend)      | Render → Env     |
| `CORS_ORIGINS`        | Orígenes permitidos (usar `*` o URL) | Render → Env     |

---

## API Endpoints

| Método | Endpoint                    | Descripción                    |
|--------|-----------------------------|--------------------------------|
| GET    | `/api/kpi`                  | KPIs del día                   |
| GET    | `/api/agenda`               | Citas del día                  |
| POST   | `/api/agenda`               | Nueva cita                     |
| GET    | `/api/pacientes/buscar`     | Búsqueda por DNI o apellido    |
| GET    | `/api/pacientes/{dni}`      | Datos de un paciente           |
| POST   | `/api/pacientes`            | Registrar paciente             |
| GET    | `/api/sala`                 | Mapa de máquinas               |
| POST   | `/api/sala/asignar`         | Asignar paciente a máquina     |
| GET    | `/api/fichas/{dni}`         | Última ficha del paciente      |
| POST   | `/api/fichas`               | Guardar ficha                  |
| GET    | `/api/fichas/{dni}/pdf`     | Descargar ficha como PDF       |
| GET    | `/api/atenciones`           | Atenciones del mes             |
| POST   | `/api/atenciones`           | Registrar atención             |
| GET    | `/api/evolucion/{dni}`      | Notas y monitoreo              |
| POST   | `/api/evolucion`            | Nueva nota de evolución        |
| GET    | `/api/historia/{dni}/pdf`   | PDF del expediente             |
| GET    | `/api/admin/stats`          | Estadísticas del servicio      |
| GET    | `/api/informe`              | Datos del informe mensual      |
| GET    | `/api/informe/pdf`          | Informe mensual en PDF         |
| GET    | `/api/informe/word`         | Informe mensual en Word (.docx)|
| POST   | `/api/mantenimiento`        | Acciones de sistema            |
| GET    | `/api/status`               | Estado del servidor            |

---

## Seguridad

- Las credenciales de BD (`SUPABASE_SERVICE_KEY`) **solo** viven en Render como variables de entorno.
- El frontend usa únicamente la `anon key` de Supabase para autenticación.
- Row Level Security (RLS) habilitado en todas las tablas: solo usuarios autenticados acceden.
- Los `.db` files locales están en `.gitignore` — no subir datos reales al repo.

---

## Desarrollo Local

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Crear archivo .env (NO subir al repo)
echo "SUPABASE_URL=https://XXXX.supabase.co" > .env
echo "SUPABASE_SERVICE_KEY=eyJhbGciOi..." >> .env

# Iniciar servidor
uvicorn main:app --reload --port 8000
```

Swagger UI disponible en: `http://localhost:8000/docs`

---

*Sistema desarrollado para el Servicio de Psicología – Unidad de Hemodiálisis y DIPAC*  
*Hospital Nacional Ramiro Prialé Prialé · EsSalud · Huancayo, Perú*
