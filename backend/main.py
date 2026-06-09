"""
Psiconefrología – HNRPP EsSalud
Backend FastAPI · Deploy: Render · DB: Supabase (PostgreSQL)

Estructura de endpoints:
  GET  /api/kpi
  GET  /api/agenda
  POST /api/agenda
  GET  /api/pacientes/buscar
  GET  /api/sala
  POST /api/sala/asignar
  GET  /api/fichas/{dni}
  POST /api/fichas
  GET  /api/atenciones
  POST /api/atenciones
  GET  /api/evolucion/{dni}
  POST /api/evolucion
  GET  /api/admin/stats
  GET  /api/informe
  GET  /api/informe/pdf
  GET  /api/informe/word
  GET  /api/historia/{dni}/pdf
  GET  /api/fichas/{dni}/pdf
  POST /api/mantenimiento
  GET  /api/status
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers import (
    agenda, pacientes, fichas,
    sala, atenciones, evolucion,
    admin, informes, mantenimiento, status
)

# ── Inicialización ────────────────────────────────────────
app = FastAPI(
    title="Psiconefrología API",
    description="Sistema de gestión clínica – HNRPP EsSalud",
    version="2.0.0",
)

# ── CORS (permite llamadas desde el HTML en el mismo dominio o localhost) ──
ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # en producción reemplaza por ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────
app.include_router(agenda.router,        prefix="/api")
app.include_router(pacientes.router,     prefix="/api")
app.include_router(fichas.router,        prefix="/api")
app.include_router(sala.router,          prefix="/api")
app.include_router(atenciones.router,    prefix="/api")
app.include_router(evolucion.router,     prefix="/api")
app.include_router(admin.router,         prefix="/api")
app.include_router(informes.router,      prefix="/api")
app.include_router(mantenimiento.router, prefix="/api")
app.include_router(status.router,        prefix="/api")

# ── Sirve el frontend HTML (mismo servidor) ───────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# ── Health check raíz ─────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "psiconefrologia-api"}
