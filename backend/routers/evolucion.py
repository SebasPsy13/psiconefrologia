"""
routers/evolucion.py
GET  /api/evolucion/{dni}   – datos de monitoreo + notas
POST /api/evolucion         – guardar nueva nota
GET  /api/historia/{dni}/pdf
"""

import json
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from database import get_client, TABLA_EVOLUCION, TABLA_FICHAS, TABLA_PACIENTES
from models.schemas import NotaEvolucion, NotaOut
from utils.pdf_generator import generar_pdf_ficha

router = APIRouter(tags=["Evolución"])


# ── GET /api/evolucion/{dni} ──────────────────────────────
@router.get("/evolucion/{dni}")
async def get_evolucion(dni: str):
    db = get_client()

    # notas de evolución
    resp_n = (
        db.table(TABLA_EVOLUCION)
        .select("id, fecha, tipo, nota")
        .eq("dni_paciente", dni)
        .order("fecha", desc=True)
        .execute()
    )

    # monitoreo desde la última ficha
    resp_f = (
        db.table(TABLA_FICHAS)
        .select("datos_json")
        .eq("dni_paciente", dni)
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    monitoreo = [[5,4,6,5,7,6,7,8,8], [7,6,5,5,4,4,3,3,2],
                 [3,4,4,5,5,6,6,7,7], [4,4,5,5,6,6,7,7,8]]

    if resp_f.data:
        datos = json.loads(resp_f.data[0]["datos_json"])
        mon   = datos.get("monitoreo")
        if mon:
            areas_order = ["A – Afectivo","X – Afectivo","X – Ansioso",
                           "D – Adherencia","S – Sueño"]
            # intentar extraer valores de la estructura del monitoreo
            sesiones = [f"S{i}" for i in range(1,10)]
            extracted = []
            if isinstance(mon, dict):
                for area_key in ["A – Afectivo","X – Ansioso","D – Adherencia","S – Sueño"]:
                    if area_key in mon:
                        extracted.append([mon[area_key].get(s, 0) for s in sesiones])
            if len(extracted) == 4:
                monitoreo = extracted

    return {
        "notas":     resp_n.data or [],
        "monitoreo": monitoreo,
    }


# ── POST /api/evolucion ───────────────────────────────────
@router.post("/evolucion", response_model=NotaOut, status_code=201)
async def guardar_nota(nota: NotaEvolucion):
    db = get_client()

    resp_p = (
        db.table(TABLA_PACIENTES)
        .select("dni")
        .eq("dni", nota.dni)
        .execute()
    )
    if not resp_p.data:
        raise HTTPException(status_code=404,
                            detail=f"Paciente {nota.dni} no encontrado")

    payload = {
        "dni_paciente": nota.dni,
        "fecha":        nota.fecha,
        "tipo":         nota.tipo,
        "nota":         nota.nota,
    }
    resp = db.table(TABLA_EVOLUCION).insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Error al guardar nota")

    row = resp.data[0]
    return NotaOut(id=row["id"], dni=row["dni_paciente"],
                   fecha=row["fecha"], tipo=row["tipo"], nota=row["nota"])


# ── GET /api/historia/{dni}/pdf ───────────────────────────
@router.get("/historia/{dni}/pdf")
async def historia_pdf(dni: str):
    db = get_client()

    resp_p = (
        db.table(TABLA_PACIENTES)
        .select("*")
        .eq("dni", dni)
        .single()
        .execute()
    )
    if not resp_p.data:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    resp_f = (
        db.table(TABLA_FICHAS)
        .select("datos_json, fecha_entrevista")
        .eq("dni_paciente", dni)
        .order("id", desc=True)
        .limit(1)
        .execute()
    )
    if not resp_f.data:
        raise HTTPException(status_code=404, detail="Sin ficha registrada")

    datos = json.loads(resp_f.data[0]["datos_json"])
    datos["fecha_entrevista"] = resp_f.data[0].get("fecha_entrevista", "")

    pdf_bytes = generar_pdf_ficha(resp_p.data, datos)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Historia_{dni}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )
