"""
models/schemas.py – Pydantic schemas para validación de entrada/salida
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ── Paciente ─────────────────────────────────────────────
class PacienteBase(BaseModel):
    dni:          str = Field(..., min_length=8, max_length=8)
    nombres:      str
    apellidos:    str
    edad:         Optional[int] = None
    sexo:         Optional[str] = None          # "M" | "F"
    fecha_nac:    Optional[str] = None
    lugar:        Optional[str] = None
    estado_civil: Optional[str] = None
    hijos:        Optional[int] = None
    instruccion:  Optional[str] = None
    trabajo:      Optional[str] = None
    direccion:    Optional[str] = None
    telefono:     Optional[str] = None
    servicio:     Optional[str] = None          # HD | DIPAC | ERCA

class PacienteCreate(PacienteBase):
    pass

class PacienteOut(PacienteBase):
    id: Optional[int] = None


# ── Agenda / Cita ────────────────────────────────────────
class CitaCreate(BaseModel):
    dni:           str
    fecha:         str                          # ISO YYYY-MM-DD
    tipo_cita:     str
    observaciones: Optional[str] = ""
    hora:          Optional[str] = None

class CitaOut(CitaCreate):
    id:       int
    estado:   str = "Pendiente"
    paciente: Optional[str] = None
    servicio: Optional[str] = None


# ── Sala de máquinas ─────────────────────────────────────
class AsignarMaquina(BaseModel):
    sala:    str
    maquina: int = Field(..., ge=1, le=8)
    turno:   str
    dia:     str
    dni:     str

class MaquinaOut(BaseModel):
    maquina:  int
    paciente: Optional[str] = None
    dni:      Optional[str] = None


# ── Ficha virtual ────────────────────────────────────────
class Filiacion(BaseModel):
    modalidad:  Optional[str] = None
    turno:      Optional[str] = None
    te:         Optional[str] = None
    t_dialisis: Optional[str] = None
    acceso:     Optional[str] = None

class Adherencia(BaseModel):
    asistencia: int = Field(3, ge=1, le=5)
    dieta:      int = Field(3, ge=1, le=5)
    farma:      int = Field(3, ge=1, le=5)
    higiene:    int = Field(3, ge=1, le=5)

class ExamenMental(BaseModel):
    obs: Optional[str] = None
    afe: Optional[str] = None
    cog: Optional[str] = None
    vol: Optional[str] = None

class FichaCreate(BaseModel):
    dni:              str
    fecha_entrevista: str
    filiacion:        Optional[Filiacion]    = None
    antecedentes:     Optional[str]          = None
    conciencia:       Optional[str]          = None
    dinamica:         Optional[str]          = None
    det_dinamica:     Optional[str]          = None
    nombre_cuidador:  Optional[str]          = None
    instruccion:      Optional[str]          = None
    exp_laboral:      Optional[str]          = None
    adherencia:       Optional[Adherencia]   = None
    examen_mental:    Optional[ExamenMental] = None
    diagnostico:      Optional[str]          = None
    eval_p:           Optional[str]          = None
    det_interv:       Optional[str]          = None
    tipo_interv:      Optional[str]          = None
    monitoreo:        Optional[Dict[str, Any]] = None

class FichaOut(FichaCreate):
    id: Optional[int] = None


# ── Atención ─────────────────────────────────────────────
class AtencionCreate(BaseModel):
    dni:           str
    fecha:         str
    tipo_cita:     str
    observaciones: Optional[str] = ""
    estado:        Optional[str] = "Atendido"

class AtencionOut(AtencionCreate):
    id:       int
    paciente: Optional[str] = None


# ── Nota de evolución ────────────────────────────────────
class NotaEvolucion(BaseModel):
    dni:   str
    fecha: str
    tipo:  str
    nota:  str

class NotaOut(NotaEvolucion):
    id: int


# ── KPI ──────────────────────────────────────────────────
class KpiOut(BaseModel):
    atendidos:  int
    pendientes: int
    activos:    int
    alertas:    int


# ── Admin stats ──────────────────────────────────────────
class AdminStatsOut(BaseModel):
    atenciones: int
    activos:    int
    hd:         int
    dipac:      int
    tipos:      List[str]
    counts:     List[int]


# ── Mantenimiento ────────────────────────────────────────
class MantenimientoAction(BaseModel):
    accion: str   # backup | vacuum | schema | export
