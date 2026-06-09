"""
routers/agenda.py
GET  /api/agenda?fecha=YYYY-MM-DD
POST /api/agenda
GET  /api/kpi?fecha=YYYY-MM-DD
"""

from datetime import date
from typing import List
from fastapi import APIRouter, HTTPException, Query

from database import get_client, TABLA_AGENDA, TABLA_PACIENTES
from models.schemas import CitaCreate, CitaOut, KpiOut

router = APIRouter(tags=["Agenda"])


# ── GET /api/kpi ─────────────────────────────────────────
@router.get("/kpi", response_model=KpiOut)
async def get_kpi(fecha: str = Query(default=str(date.today()))):
    db = get_client()

    # atendidos hoy
    resp_at = (
        db.table(TABLA_AGENDA)
        .select("id", count="exact")
        .eq("fecha",  fecha)
        .eq("estado", "Atendido")
        .execute()
    )
    atendidos = resp_at.count or 0

    # pendientes hoy
    resp_pe = (
        db.table(TABLA_AGENDA)
        .select("id", count="exact")
        .eq("fecha",  fecha)
        .eq("estado", "Pendiente")
        .execute()
    )
    pendientes = resp_pe.count or 0

    # pacientes activos (total en tabla pacientes)
    resp_ac = db.table(TABLA_PACIENTES).select("id", count="exact").execute()
    activos  = resp_ac.count or 0

    # alertas: adherencia promedio < 3 (fichas recientes)
    alertas = 0  # calculado opcionalmente desde tabla fichas

    return KpiOut(
        atendidos=atendidos,
        pendientes=pendientes,
        activos=activos,
        alertas=alertas,
    )


# ── GET /api/agenda ───────────────────────────────────────
@router.get("/agenda", response_model=List[CitaOut])
async def get_agenda(fecha: str = Query(default=str(date.today()))):
    db = get_client()

    resp = (
        db.table(TABLA_AGENDA)
        .select(
            "id, dni_paciente, tipo_cita, hora, estado, observaciones, fecha, "
            f"{TABLA_PACIENTES}(nombres, apellidos, servicio)"
        )
        .eq("fecha", fecha)
        .order("hora")
        .execute()
    )

    items = []
    for row in (resp.data or []):
        p       = row.get("pacientes") or {}
        nombre  = f"{p.get('apellidos','')}, {p.get('nombres','')}".strip(", ")
        items.append(CitaOut(
            id=row["id"],
            dni=row["dni_paciente"],
            fecha=row["fecha"],
            tipo_cita=row["tipo_cita"],
            observaciones=row.get("observaciones"),
            hora=row.get("hora", "08:00"),
            estado=row.get("estado", "Pendiente"),
            paciente=nombre,
            servicio=p.get("servicio"),
        ))
    return items


# ── POST /api/agenda ──────────────────────────────────────
@router.post("/agenda", response_model=CitaOut, status_code=201)
async def crear_cita(cita: CitaCreate):
    db = get_client()

    # verificar que el paciente existe
    resp_p = (
        db.table(TABLA_PACIENTES)
        .select("dni")
        .eq("dni", cita.dni)
        .execute()
    )
    if not resp_p.data:
        raise HTTPException(status_code=404,
                            detail=f"Paciente con DNI {cita.dni} no encontrado")

    payload = {
        "dni_paciente":  cita.dni,
        "fecha":         cita.fecha,
        "tipo_cita":     cita.tipo_cita,
        "observaciones": cita.observaciones or "",
        "hora":          cita.hora or "08:00",
        "estado":        "Pendiente",
    }
    resp = db.table(TABLA_AGENDA).insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Error al crear la cita")

    row = resp.data[0]
    return CitaOut(id=row["id"], **{k: row[k] for k in payload},
                   dni=row["dni_paciente"])


# ── PUT /api/agenda/{id}/estado ───────────────────────────
@router.put("/agenda/{cita_id}/estado")
async def actualizar_estado(cita_id: int, estado: str = Query(...)):
    db = get_client()
    estados_validos = {"Pendiente", "Atendido", "Programado", "Cancelado"}
    if estado not in estados_validos:
        raise HTTPException(status_code=400,
                            detail=f"Estado inválido. Usa: {estados_validos}")

    resp = (
        db.table(TABLA_AGENDA)
        .update({"estado": estado})
        .eq("id", cita_id)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return {"id": cita_id, "estado": estado}
