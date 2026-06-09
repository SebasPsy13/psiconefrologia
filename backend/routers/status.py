"""
routers/status.py
GET /api/status  – estado del servidor y base de datos
"""

import os
from fastapi import APIRouter
from database import get_client, SUPABASE_URL

router = APIRouter(tags=["Sistema"])

TABLAS = ["pacientes", "agenda", "fichas", "sala_maquinas", "atenciones", "evolucion"]


@router.get("/status")
async def get_status():
    db_ok      = False
    tablas_ok  = []
    db_version = "Desconocida"

    try:
        db = get_client()
        # ping simple
        r = db.table("pacientes").select("id", count="exact").limit(0).execute()
        db_ok = True

        for tabla in TABLAS:
            try:
                db.table(tabla).select("id", count="exact").limit(0).execute()
                tablas_ok.append(tabla)
            except Exception:
                pass
    except Exception as e:
        pass

    return {
        "db":      f"Supabase PostgreSQL – {SUPABASE_URL[:30]}..." if SUPABASE_URL else "No configurada",
        "db_ok":   db_ok,
        "tablas":  tablas_ok,
        "version": "2.0.0",
        "modo":    "Producción" if os.getenv("RENDER") else "Desarrollo",
        "env":     os.getenv("ENVIRONMENT", "local"),
    }
