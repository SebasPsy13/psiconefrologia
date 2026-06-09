"""
database.py – cliente Supabase + helpers de query

Variables de entorno requeridas (Render → Environment):
  SUPABASE_URL          https://xxxxx.supabase.co
  SUPABASE_SERVICE_KEY  service_role key (solo backend, nunca exponer al frontend)
"""

import os
from supabase import create_client, Client

SUPABASE_URL         = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


def get_client() -> Client:
    """Devuelve un cliente Supabase autenticado con la service key."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError(
            "Variables SUPABASE_URL y SUPABASE_SERVICE_KEY no configuradas. "
            "Agrégalas en Render → Environment."
        )
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# ─── Tablas de referencia ────────────────────────────────
TABLA_PACIENTES   = "pacientes"
TABLA_AGENDA      = "agenda"
TABLA_FICHAS      = "fichas"
TABLA_SALA        = "sala_maquinas"
TABLA_ATENCIONES  = "atenciones"
TABLA_EVOLUCION   = "evolucion"
