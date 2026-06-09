"""
routers/sala.py
GET  /api/sala?sala=...&turno=...&dia=...
POST /api/sala/asignar
DELETE /api/sala/quitar/{sala}/{maquina}
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query

from database import get_client, TABLA_SALA, TABLA_PACIENTES
from models.schemas import AsignarMaquina, MaquinaOut

router = APIRouter(tags=["Sala"])


# ── GET /api/sala ─────────────────────────────────────────
@router.get("/sala", response_model=List[MaquinaOut])
async def get_sala(
    sala:  str = Query(...),
    turno: str = Query(...),
    dia:   str = Query(...),
):
    db = get_client()
    resp = (
        db.table(TABLA_SALA)
        .select(
            f"maquina, dni_paciente, {TABLA_PACIENTES}(nombres, apellidos)"
        )
        .eq("sala",  sala)
        .eq("turno", turno)
        .eq("dia",   dia)
        .order("maquina")
        .execute()
    )

    # Construimos lista de 8 máquinas (libres o con paciente)
    ocupadas: dict = {}
    for row in (resp.data or []):
        p = row.get("pacientes") or {}
        ocupadas[row["maquina"]] = MaquinaOut(
            maquina=row["maquina"],
            paciente=f"{p.get('nombres','')} {p.get('apellidos','')}".strip() or None,
            dni=row.get("dni_paciente"),
        )

    resultado = []
    for i in range(1, 9):
        resultado.append(ocupadas.get(i, MaquinaOut(maquina=i)))
    return resultado


# ── POST /api/sala/asignar ────────────────────────────────
@router.post("/sala/asignar", status_code=201)
async def asignar_maquina(data: AsignarMaquina):
    db = get_client()

    # verificar paciente
    resp_p = (
        db.table(TABLA_PACIENTES)
        .select("dni")
        .eq("dni", data.dni)
        .execute()
    )
    if not resp_p.data:
        raise HTTPException(status_code=404,
                            detail=f"Paciente {data.dni} no encontrado")

    # upsert (si ya existe esa posición la actualiza)
    payload = {
        "sala":         data.sala,
        "maquina":      data.maquina,
        "turno":        data.turno,
        "dia":          data.dia,
        "dni_paciente": data.dni,
    }
    resp = (
        db.table(TABLA_SALA)
        .upsert(payload, on_conflict="sala,maquina,turno,dia")
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=500, detail="Error al asignar máquina")
    return {"mensaje": f"Paciente asignado a M-{data.maquina:02d}"}


# ── DELETE /api/sala/quitar ───────────────────────────────
@router.delete("/sala/quitar/{sala}/{maquina}")
async def quitar_paciente(
    sala:    str,
    maquina: int,
    turno:   str = Query(...),
    dia:     str = Query(...),
):
    db = get_client()
    resp = (
        db.table(TABLA_SALA)
        .delete()
        .eq("sala",    sala)
        .eq("maquina", maquina)
        .eq("turno",   turno)
        .eq("dia",     dia)
        .execute()
    )
    return {"mensaje": f"Máquina M-{maquina:02d} liberada"}
