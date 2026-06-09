"""
routers/pacientes.py
GET  /api/pacientes/buscar?q=...
GET  /api/pacientes/{dni}
POST /api/pacientes
PUT  /api/pacientes/{dni}
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query

from database import get_client, TABLA_PACIENTES
from models.schemas import PacienteCreate, PacienteOut

router = APIRouter(tags=["Pacientes"])


# ── GET /api/pacientes/buscar ─────────────────────────────
@router.get("/pacientes/buscar", response_model=List[PacienteOut])
async def buscar_paciente(q: str = Query(..., min_length=1)):
    db = get_client()

    # búsqueda por DNI exacto
    if q.isdigit():
        resp = (
            db.table(TABLA_PACIENTES)
            .select("*")
            .eq("dni", q)
            .execute()
        )
    else:
        # búsqueda por apellidos (ilike = case-insensitive)
        resp = (
            db.table(TABLA_PACIENTES)
            .select("*")
            .ilike("apellidos", f"%{q}%")
            .limit(10)
            .execute()
        )

    return [PacienteOut(**row) for row in (resp.data or [])]


# ── GET /api/pacientes/{dni} ──────────────────────────────
@router.get("/pacientes/{dni}", response_model=PacienteOut)
async def get_paciente(dni: str):
    db   = get_client()
    resp = (
        db.table(TABLA_PACIENTES)
        .select("*")
        .eq("dni", dni)
        .single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return PacienteOut(**resp.data)


# ── POST /api/pacientes ───────────────────────────────────
@router.post("/pacientes", response_model=PacienteOut, status_code=201)
async def crear_paciente(paciente: PacienteCreate):
    db = get_client()

    # verificar duplicado
    existe = (
        db.table(TABLA_PACIENTES)
        .select("dni")
        .eq("dni", paciente.dni)
        .execute()
    )
    if existe.data:
        raise HTTPException(status_code=409,
                            detail=f"Ya existe un paciente con DNI {paciente.dni}")

    resp = db.table(TABLA_PACIENTES).insert(paciente.model_dump()).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Error al registrar paciente")
    return PacienteOut(**resp.data[0])


# ── PUT /api/pacientes/{dni} ──────────────────────────────
@router.put("/pacientes/{dni}", response_model=PacienteOut)
async def actualizar_paciente(dni: str, paciente: PacienteCreate):
    db = get_client()
    payload = {k: v for k, v in paciente.model_dump().items()
               if v is not None and k != "dni"}
    resp = (
        db.table(TABLA_PACIENTES)
        .update(payload)
        .eq("dni", dni)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return PacienteOut(**resp.data[0])
