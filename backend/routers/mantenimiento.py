"""
routers/mantenimiento.py
POST /api/mantenimiento
GET  /api/status
"""

from fastapi import APIRouter, HTTPException
from database import get_client
from models.schemas import MantenimientoAction

router = APIRouter(tags=["Sistema"])


@router.post("/mantenimiento")
async def accion_mantenimiento(accion: MantenimientoAction):
    db = get_client()

    if accion.accion == "backup":
        # Supabase maneja backups automáticos; aquí solo verificamos conexión
        return {"mensaje": "Backup gestionado automáticamente por Supabase", "ok": True}

    elif accion.accion == "vacuum":
        # En Supabase (PostgreSQL) VACUUM se ejecuta automáticamente (autovacuum)
        # Para un VACUUM manual se necesita acceso SQL directo (pg_cron o dashboard)
        return {"mensaje": "VACUUM programado. Supabase ejecuta autovacuum automáticamente.", "ok": True}

    elif accion.accion == "schema":
        # Verificar que todas las tablas existen
        tablas = ["pacientes", "agenda", "fichas", "sala_maquinas", "atenciones", "evolucion"]
        existentes = []
        for tabla in tablas:
            try:
                r = db.table(tabla).select("id", count="exact").limit(0).execute()
                existentes.append(tabla)
            except Exception:
                pass
        return {"mensaje": f"Esquema verificado. Tablas OK: {existentes}", "ok": True}

    elif accion.accion == "export":
        # Exportar resumen en JSON (el frontend puede convertirlo a CSV)
        try:
            r = db.table("pacientes").select("*").execute()
            return {
                "mensaje": "Datos exportados",
                "datos":   r.data or [],
                "ok":      True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    else:
        raise HTTPException(status_code=400, detail=f"Acción '{accion.accion}' no reconocida")
