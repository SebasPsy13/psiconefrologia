"""
routers/admin.py
GET /api/admin/stats
"""

from datetime import date
from fastapi import APIRouter, Query

from database import get_client, TABLA_ATENCIONES, TABLA_PACIENTES
from models.schemas import AdminStatsOut

router = APIRouter(tags=["Admin"])


@router.get("/admin/stats", response_model=AdminStatsOut)
async def get_admin_stats(
    mes:  int = Query(default=date.today().month,  ge=1,    le=12),
    anio: int = Query(default=date.today().year,   ge=2020),
):
    import calendar
    db         = get_client()
    fecha_ini  = f"{anio}-{mes:02d}-01"
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_fin  = f"{anio}-{mes:02d}-{ultimo_dia}"

    # total atenciones del mes
    resp_at = (
        db.table(TABLA_ATENCIONES)
        .select("id", count="exact")
        .gte("fecha", fecha_ini)
        .lte("fecha", fecha_fin)
        .execute()
    )
    total_atenciones = resp_at.count or 0

    # pacientes activos totales
    resp_pa = db.table(TABLA_PACIENTES).select("id", count="exact").execute()
    activos  = resp_pa.count or 0

    # HD / DIPAC
    resp_hd = (
        db.table(TABLA_PACIENTES)
        .select("id", count="exact")
        .eq("servicio", "HD")
        .execute()
    )
    resp_dp = (
        db.table(TABLA_PACIENTES)
        .select("id", count="exact")
        .eq("servicio", "DIPAC")
        .execute()
    )
    hd_count   = resp_hd.count or 0
    dipac_count = resp_dp.count or 0

    # distribución por tipo de atención (del mes)
    resp_tipos = (
        db.table(TABLA_ATENCIONES)
        .select("tipo_cita")
        .gte("fecha", fecha_ini)
        .lte("fecha", fecha_fin)
        .execute()
    )
    tipo_counts: dict = {}
    for row in (resp_tipos.data or []):
        t = row.get("tipo_cita", "Otro")
        tipo_counts[t] = tipo_counts.get(t, 0) + 1

    tipos  = list(tipo_counts.keys())  or ["Sin datos"]
    counts = list(tipo_counts.values()) or [0]

    return AdminStatsOut(
        atenciones=total_atenciones,
        activos=activos,
        hd=hd_count,
        dipac=dipac_count,
        tipos=tipos,
        counts=counts,
    )
