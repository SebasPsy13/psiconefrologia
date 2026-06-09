"""
utils/pdf_generator.py
Genera PDFs clínicos con ReportLab.
  - Ficha psicológica virtual
  - Expediente clínico (historia)
  - Informe mensual
"""

from __future__ import annotations
import io
from datetime import datetime
from typing import Any, Dict, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether
)

# ─── Paleta institucional ─────────────────────────────────
TEAL   = colors.HexColor("#00695C")
TEAL_L = colors.HexColor("#E0F2F1")
TEAL_M = colors.HexColor("#00897B")
AMBER  = colors.HexColor("#FFB300")
RED    = colors.HexColor("#EF5350")
GRAY   = colors.HexColor("#6B7280")
DARK   = colors.HexColor("#1A1A1A")
WHITE  = colors.white

PAGE_W, PAGE_H = A4


def _base_styles():
    ss = getSampleStyleSheet()
    extra = {
        "Title": ParagraphStyle("Title", fontSize=18, textColor=TEAL,
                                fontName="Helvetica-Bold", spaceAfter=4),
        "SubTitle": ParagraphStyle("SubTitle", fontSize=10, textColor=GRAY,
                                   fontName="Helvetica", spaceAfter=14),
        "SectionHead": ParagraphStyle("SectionHead", fontSize=11, textColor=WHITE,
                                      fontName="Helvetica-Bold", spaceAfter=0,
                                      leading=16),
        "Body": ParagraphStyle("Body", fontSize=9, textColor=DARK,
                               fontName="Helvetica", leading=14, spaceAfter=4),
        "Label": ParagraphStyle("Label", fontSize=8, textColor=GRAY,
                                fontName="Helvetica-Bold", spaceAfter=2,
                                textTransform="uppercase"),
        "Value": ParagraphStyle("Value", fontSize=9, textColor=DARK,
                                fontName="Helvetica", leading=13),
        "FooterStyle": ParagraphStyle("FooterStyle", fontSize=7, textColor=GRAY,
                                      fontName="Helvetica", alignment=TA_CENTER),
    }
    ss.add(extra["Title"])
    ss.add(extra["SubTitle"])
    ss.add(extra["SectionHead"])
    ss.add(extra["Body"])
    ss.add(extra["Label"])
    ss.add(extra["Value"])
    ss.add(extra["FooterStyle"])
    return ss


def _header_block(ss, titulo: str, subtitulo: str) -> list:
    """Bloque de encabezado institucional común."""
    logo_text = "🧠 PSICONEFROLOGÍA"
    hospital  = "Hospital Nacional Ramiro Prialé Prialé – EsSalud · Huancayo, Perú"
    fecha     = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Tabla encabezado: logo izq | título centro | fecha der
    header_table = Table(
        [[
            Paragraph(f"<b>{logo_text}</b>", ParagraphStyle("lp", fontSize=11,
                      textColor=TEAL, fontName="Helvetica-Bold")),
            Paragraph(f"<b>{titulo}</b><br/><font size=8 color='#6B7280'>{subtitulo}</font>",
                      ParagraphStyle("cp", fontSize=13, textColor=DARK,
                                     fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph(f"Fecha: {fecha}", ParagraphStyle("rp", fontSize=8,
                      textColor=GRAY, alignment=TA_RIGHT)),
        ]],
        colWidths=[4*cm, 10*cm, 4*cm]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
    ]))

    return [
        header_table,
        HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=8),
        Paragraph(hospital, ParagraphStyle("h2", fontSize=8, textColor=GRAY,
                  alignment=TA_CENTER, spaceAfter=10)),
    ]


def _section_title(ss, text: str) -> list:
    """Barra de sección con fondo teal."""
    t = Table([[Paragraph(text, ss["SectionHead"])]],
              colWidths=[18*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), TEAL),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [4,4,4,4]),
    ]))
    return [Spacer(1, 8), t, Spacer(1, 6)]


def _kv_table(rows: list[tuple[str, str]], ss) -> Table:
    """Tabla de clave–valor de dos columnas."""
    data = [[Paragraph(k, ss["Label"]), Paragraph(str(v or "–"), ss["Value"])]
            for k, v in rows]
    t = Table(data, colWidths=[4.5*cm, 13.5*cm])
    t.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [TEAL_L, WHITE]),
        ("LEFTPADDING",   (0,0), (0,-1), 6),
    ]))
    return t


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(2*cm, 1.2*cm,
                      "Sistema de Gestión Clínica – Psiconefrología HNRPP EsSalud")
    canvas.drawRightString(PAGE_W - 2*cm, 1.2*cm,
                           f"Página {doc.page}")
    canvas.restoreState()


# ─────────────────────────────────────────────────────────
#  PDF: FICHA PSICOLÓGICA
# ─────────────────────────────────────────────────────────
def generar_pdf_ficha(paciente: dict, datos: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    ss    = _base_styles()
    story = []

    p_nombre = f"{paciente.get('nombres','')} {paciente.get('apellidos','')}"
    story += _header_block(ss, "FICHA PSICOLÓGICA VIRTUAL",
                           f"Paciente: {p_nombre} · DNI: {paciente.get('dni','')}")

    # I. Filiación
    story += _section_title(ss, "I. Datos de Filiación y Estado Clínico")
    fil = datos.get("filiacion") or {}
    story.append(_kv_table([
        ("Nombres completos", p_nombre),
        ("DNI",               paciente.get("dni")),
        ("Edad / Sexo",       f"{paciente.get('edad','')} años / {paciente.get('sexo','')}"),
        ("Servicio",          paciente.get("servicio")),
        ("Modalidad",         fil.get("modalidad")),
        ("Turno",             fil.get("turno")),
        ("Acceso Vascular",   fil.get("acceso")),
        ("Tiempo Enfermedad", fil.get("te")),
        ("Tiempo Diálisis",   fil.get("t_dialisis")),
        ("Fecha entrevista",  datos.get("fecha_entrevista")),
    ], ss))

    # II. Antecedentes y conciencia
    story += _section_title(ss, "II. Antecedentes Clínicos y Conciencia de Enfermedad")
    story.append(_kv_table([
        ("Antecedentes Clínicos",     datos.get("antecedentes")),
        ("Conciencia de Enfermedad",  datos.get("conciencia")),
    ], ss))

    # III. Datos Familiares
    story += _section_title(ss, "III. Datos Complementarios y Sociales")
    story.append(_kv_table([
        ("Dinámica Familiar", datos.get("dinamica")),
        ("Det. Dinámica",     datos.get("det_dinamica")),
        ("Cuidador/Responsable", datos.get("nombre_cuidador")),
        ("Instrucción",       datos.get("instruccion")),
        ("Exp. Laboral",      datos.get("exp_laboral")),
    ], ss))

    adh = datos.get("adherencia") or {}
    story += _section_title(ss, "Escala de Adherencia al Tratamiento")
    adh_data = [["Dimensión", "Puntaje (1–5)", "Nivel"]]
    for dim, key in [("Asistencia","asistencia"),("Dieta","dieta"),
                     ("Farmacológica","farma"),("Higiene","higiene")]:
        v   = adh.get(key, 0)
        niv = "Bajo" if v <= 2 else ("Medio" if v == 3 else "Alto")
        adh_data.append([dim, str(v), niv])
    t = Table(adh_data, colWidths=[6*cm, 6*cm, 6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), TEAL),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [TEAL_L, WHITE]),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#E5E9E8")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(t)

    # IV. Examen mental
    story += _section_title(ss, "IV. Examen del Estado Mental")
    em = datos.get("examen_mental") or {}
    story.append(_kv_table([
        ("1. Observaciones Generales", em.get("obs")),
        ("2. Estado Afectivo",         em.get("afe")),
        ("3. Aspectos Cognoscitivos",  em.get("cog")),
        ("4. Actividad Voluntaria",    em.get("vol")),
    ], ss))

    # V. Diagnóstico e intervención
    story += _section_title(ss, "V. Diagnóstico e Intervención Psicológica")
    story.append(_kv_table([
        ("Diagnóstico Psicológico",    datos.get("diagnostico")),
        ("Tests Aplicados",            datos.get("eval_p")),
        ("Tipo de Intervención",       datos.get("tipo_interv")),
        ("Estrategia de Intervención", datos.get("det_interv")),
    ], ss))

    # Firma
    story.append(Spacer(1, 24))
    firma_table = Table(
        [["_____________________________", ""],
         [Paragraph("Psicólogo/a Internista", ParagraphStyle("f", fontSize=9,
           textColor=GRAY, alignment=TA_CENTER)), ""]],
        colWidths=[9*cm, 9*cm]
    )
    firma_table.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(firma_table)

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────
#  PDF: INFORME MENSUAL
# ─────────────────────────────────────────────────────────
MESES = ["", "Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

def generar_pdf_informe(mes: int, anio: int, stats: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    ss    = _base_styles()
    story = []

    story += _header_block(ss, "INFORME MENSUAL DE ACTIVIDADES",
                           f"Período: {MESES[mes]} {anio}")

    # KPIs resumen
    story += _section_title(ss, "Resumen de Actividades")
    kpi_data = [
        ["Indicador", "Valor"],
        ["Total de Atenciones", str(stats.get("atenciones", 0))],
        ["Pacientes Atendidos",  str(stats.get("activos", 0))],
        ["Pacientes HD",         str(stats.get("hd", 0))],
        ["Pacientes DIPAC/ERCA", str(stats.get("dipac", 0))],
    ]
    t = Table(kpi_data, colWidths=[10*cm, 8*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), TEAL),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [TEAL_L, WHITE]),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#E5E9E8")),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(t)

    # Distribución por tipo
    story += _section_title(ss, "Distribución por Tipo de Intervención")
    tipos  = stats.get("tipos",  [])
    counts = stats.get("counts", [])
    total  = sum(counts) or 1
    tipo_data = [["Tipo de Atención", "N°", "%"]]
    for t_nom, cnt in zip(tipos, counts):
        tipo_data.append([t_nom, str(cnt), f"{cnt/total*100:.1f}%"])
    tipo_data.append(["TOTAL", str(total), "100%"])
    t2 = Table(tipo_data, colWidths=[9*cm, 4*cm, 5*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),  (-1,0),  TEAL),
        ("BACKGROUND",    (0,-1), (-1,-1), TEAL_L),
        ("TEXTCOLOR",     (0,0),  (-1,0),  WHITE),
        ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),  (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),  (-1,-2), [WHITE, TEAL_L]),
        ("ALIGN",         (1,0),  (-1,-1), "CENTER"),
        ("GRID",          (0,0),  (-1,-1), 0.3, colors.HexColor("#E5E9E8")),
        ("TOPPADDING",    (0,0),  (-1,-1), 6),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 6),
    ]))
    story.append(t2)

    # Conclusiones
    story += _section_title(ss, "Conclusiones y Recomendaciones")
    conclusiones = (
        f"Durante el mes de {MESES[mes]} {anio}, el servicio de Psiconefrología del "
        f"Hospital Nacional Ramiro Prialé Prialé atendió un total de {stats.get('atenciones',0)} "
        f"pacientes, de los cuales {stats.get('hd',0)} pertenecen al programa de Hemodiálisis y "
        f"{stats.get('dipac',0)} al programa DIPAC/ERCA. Se recomienda continuar con el seguimiento "
        f"psicológico individualizado, enfatizando la adherencia al tratamiento y el soporte "
        f"familiar como factores protectores en la población con enfermedad renal crónica."
    )
    story.append(Paragraph(conclusiones, ss["Body"]))
    story.append(Spacer(1, 30))

    # Firma
    story.append(Paragraph("_____________________________", ParagraphStyle("f2",
                            fontSize=9, alignment=TA_LEFT)))
    story.append(Paragraph("Psicólogo/a – Servicio de Psiconefrología",
                            ParagraphStyle("f3", fontSize=9, textColor=GRAY)))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
