"""
routers/atenciones.py
GET  /api/atenciones?mes=&anio=
POST /api/atenciones
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query

from database import get_client, TABLA_ATENCIONES, TABLA_PACIENTES
from models.schemas import AtencionCreate, AtencionOut

router = APIRouter(tags=["Atenciones"])


# ── GET /api/atenciones ───────────────────────────────────
@router.get("/atenciones", response_model=List[AtencionOut])
async def get_atenciones(
    mes:  int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2020),
):
    db = get_client()
    # filtra por mes: Supabase permite usar gte/lte sobre fechas ISO
    fecha_inicio = f"{anio}-{mes:02d}-01"
    # último día del mes
    import calendar
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_fin  = f"{anio}-{mes:02d}-{ultimo_dia}"

    resp = (
        db.table(TABLA_ATENCIONES)
        .select(
            f"id, dni_paciente, tipo_cita, fecha, estado, observaciones, "
            f"{TABLA_PACIENTES}(nombres, apellidos)"
        )
        .gte("fecha", fecha_inicio)
        .lte("fecha", fecha_fin)
        .order("fecha", desc=True)
        .execute()
    )

    items = []
    for row in (resp.data or []):
        p = row.get("pacientes") or {}
        nombre = f"{p.get('apellidos','')}, {p.get('nombres','')}".strip(", ")
        items.append(AtencionOut(
            id=row["id"],
            dni=row["dni_paciente"],
            fecha=row["fecha"],
            tipo_cita=row["tipo_cita"],
            observaciones=row.get("observaciones"),
            estado=row.get("estado", "Atendido"),
            paciente=nombre,
        ))
    return items


# ── POST /api/atenciones ──────────────────────────────────
@router.post("/atenciones", response_model=AtencionOut, status_code=201)
async def registrar_atencion(atencion: AtencionCreate):
    db = get_client()

    resp_p = (
        db.table(TABLA_PACIENTES)
        .select("dni")
        .eq("dni", atencion.dni)
        .execute()
    )
    if not resp_p.data:
        raise HTTPException(status_code=404,
                            detail=f"Paciente {atencion.dni} no encontrado")

    payload = {
        "dni_paciente":  atencion.dni,
        "fecha":         atencion.fecha,
        "tipo_cita":     atencion.tipo_cita,
        "observaciones": atencion.observaciones or "",
        "estado":        atencion.estado or "Atendido",
    }
    resp = db.table(TABLA_ATENCIONES).insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Error al registrar atención")

    row = resp.data[0]
    return AtencionOut(id=row["id"], **{k: row[k] for k in payload},
                       dni=row["dni_paciente"])
