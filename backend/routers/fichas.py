"""
routers/fichas.py
GET  /api/fichas/{dni}          – última ficha del paciente
POST /api/fichas                – crear / actualizar ficha
GET  /api/fichas/{dni}/pdf      – descargar ficha como PDF
"""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io

from database import get_client, TABLA_FICHAS, TABLA_PACIENTES
from models.schemas import FichaCreate, FichaOut
from utils.pdf_generator import generar_pdf_ficha

router = APIRouter(tags=["Fichas"])


# ── GET /api/fichas/{dni} ─────────────────────────────────
@router.get("/fichas/{dni}", response_model=FichaOut)
async def get_ficha(dni: str):
    db = get_client()
    resp = (
        db.table(TABLA_FICHAS)
        .select("*")
        .eq("dni_paciente", dni)
        .order("id", desc=True)
        .limit(1)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Sin ficha registrada para este paciente")

    row = resp.data[0]
    # datos_json almacenado como texto JSON en Supabase
    datos = json.loads(row["datos_json"]) if isinstance(row["datos_json"], str) else row["datos_json"]
    return FichaOut(
        id=row["id"],
        dni=row["dni_paciente"],
        fecha_entrevista=row.get("fecha_entrevista", ""),
        **datos,
    )


# ── POST /api/fichas ──────────────────────────────────────
@router.post("/fichas", status_code=201)
async def guardar_ficha(ficha: FichaCreate):
    db = get_client()

    # verificar paciente
    resp_p = (
        db.table(TABLA_PACIENTES)
        .select("dni")
        .eq("dni", ficha.dni)
        .execute()
    )
    if not resp_p.data:
        raise HTTPException(status_code=404,
                            detail=f"Paciente {ficha.dni} no encontrado")

    datos_dict = ficha.model_dump(exclude={"dni", "fecha_entrevista"})

    payload = {
        "dni_paciente":    ficha.dni,
        "fecha_entrevista": ficha.fecha_entrevista,
        "datos_json":      json.dumps(datos_dict, ensure_ascii=False),
    }
    resp = db.table(TABLA_FICHAS).insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Error al guardar la ficha")

    return {"id": resp.data[0]["id"], "mensaje": "Ficha guardada correctamente"}


# ── GET /api/fichas/{dni}/pdf ─────────────────────────────
@router.get("/fichas/{dni}/pdf")
async def descargar_ficha_pdf(dni: str):
    db = get_client()

    # datos del paciente
    resp_p = (
        db.table(TABLA_PACIENTES)
        .select("*")
        .eq("dni", dni)
        .single()
        .execute()
    )
    if not resp_p.data:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    paciente = resp_p.data

    # última ficha
    resp_f = (
        db.table(TABLA_FICHAS)
        .select("datos_json, fecha_entrevista")
        .eq("dni_paciente", dni)
        .order("id", desc=True)
        .limit(1)
        .execute()
    )
    if not resp_f.data:
        raise HTTPException(status_code=404, detail="Sin ficha para este paciente")

    row   = resp_f.data[0]
    datos = json.loads(row["datos_json"]) if isinstance(row["datos_json"], str) else row["datos_json"]
    datos["fecha_entrevista"] = row.get("fecha_entrevista", "")

    pdf_bytes = generar_pdf_ficha(paciente, datos)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Ficha_{dni}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )
