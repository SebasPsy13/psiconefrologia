"""
routers/informes.py
GET /api/informe?mes=&anio=
GET /api/informe/pdf?mes=&anio=
GET /api/informe/word?mes=&anio=
"""

import calendar
import io
from datetime import date
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from database import get_client, TABLA_ATENCIONES, TABLA_PACIENTES
from utils.pdf_generator  import generar_pdf_informe
from utils.word_generator import generar_word_informe

router = APIRouter(tags=["Informes"])

MESES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]


async def _obtener_stats(mes: int, anio: int) -> dict:
    db        = get_client()
    fecha_ini = f"{anio}-{mes:02d}-01"
    fecha_fin = f"{anio}-{mes:02d}-{calendar.monthrange(anio,mes)[1]}"

    resp_at = (
        db.table(TABLA_ATENCIONES)
        .select("tipo_cita", count="exact")
        .gte("fecha", fecha_ini)
        .lte("fecha", fecha_fin)
        .execute()
    )
    total_atenciones = resp_at.count or 0

    resp_pa = db.table(TABLA_PACIENTES).select("servicio", count="exact").execute()
    activos = resp_pa.count or 0

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

    return {
        "atenciones": total_atenciones,
        "activos":    activos,
        "hd":         resp_hd.count or 0,
        "dipac":      resp_dp.count or 0,
        "tipos":      list(tipo_counts.keys())  or ["Sin datos"],
        "counts":     list(tipo_counts.values()) or [0],
        "mes_nombre": MESES[mes],
        "anio":       anio,
    }


# ── GET /api/informe ──────────────────────────────────────
@router.get("/informe")
async def get_informe(
    mes:  int = Query(default=date.today().month,  ge=1,    le=12),
    anio: int = Query(default=date.today().year,   ge=2020),
):
    return await _obtener_stats(mes, anio)


# ── GET /api/informe/pdf ──────────────────────────────────
@router.get("/informe/pdf")
async def informe_pdf(
    mes:  int = Query(..., ge=1,    le=12),
    anio: int = Query(..., ge=2020),
):
    stats     = await _obtener_stats(mes, anio)
    pdf_bytes = generar_pdf_informe(mes, anio, stats)
    nombre    = f"Informe_{MESES[mes]}_{anio}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


# ── GET /api/informe/word ─────────────────────────────────
@router.get("/informe/word")
async def informe_word(
    mes:  int = Query(..., ge=1,    le=12),
    anio: int = Query(..., ge=2020),
):
    stats      = await _obtener_stats(mes, anio)
    word_bytes = generar_word_informe(mes, anio, stats)
    nombre     = f"Informe_{MESES[mes]}_{anio}.docx"
    return StreamingResponse(
        io.BytesIO(word_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Content-Length": str(len(word_bytes)),
        },
    )
