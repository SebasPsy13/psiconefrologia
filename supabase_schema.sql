-- ═══════════════════════════════════════════════════════════════
--  PSICONEFROLOGÍA – HNRPP EsSalud
--  Supabase SQL: creación de tablas + RLS + índices
--
--  Instrucciones:
--  1. Entra a tu proyecto Supabase → SQL Editor → New query
--  2. Pega este script completo y haz clic en "Run"
--  3. Verifica en Table Editor que todas las tablas aparecen
-- ═══════════════════════════════════════════════════════════════


-- ── 1. PACIENTES ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pacientes (
    id           SERIAL PRIMARY KEY,
    dni          VARCHAR(8)  NOT NULL UNIQUE,
    nombres      VARCHAR(100) NOT NULL,
    apellidos    VARCHAR(100) NOT NULL,
    edad         SMALLINT,
    sexo         CHAR(1),                  -- 'M' | 'F'
    fecha_nac    DATE,
    lugar        VARCHAR(100),
    estado_civil VARCHAR(30),
    hijos        SMALLINT DEFAULT 0,
    instruccion  VARCHAR(60),
    trabajo      VARCHAR(100),
    direccion    TEXT,
    telefono     VARCHAR(20),
    servicio     VARCHAR(10),              -- 'HD' | 'DIPAC' | 'ERCA'
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ── 2. AGENDA (CITAS) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agenda (
    id              SERIAL PRIMARY KEY,
    dni_paciente    VARCHAR(8)  NOT NULL REFERENCES pacientes(dni) ON DELETE CASCADE,
    fecha           DATE        NOT NULL,
    hora            TIME        DEFAULT '08:00',
    tipo_cita       VARCHAR(60) NOT NULL,
    estado          VARCHAR(20) DEFAULT 'Pendiente',  -- Pendiente | Atendido | Programado | Cancelado
    observaciones   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── 3. FICHAS PSICOLÓGICAS ────────────────────────────────────
CREATE TABLE IF NOT EXISTS fichas (
    id               SERIAL PRIMARY KEY,
    dni_paciente     VARCHAR(8)  NOT NULL REFERENCES pacientes(dni) ON DELETE CASCADE,
    fecha_entrevista DATE        NOT NULL,
    datos_json       JSONB       NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ── 4. SALA DE MÁQUINAS ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS sala_maquinas (
    id           SERIAL PRIMARY KEY,
    sala         VARCHAR(10)  NOT NULL,   -- 'Sala 1' | 'Sala 2'
    maquina      SMALLINT     NOT NULL CHECK (maquina BETWEEN 1 AND 8),
    turno        VARCHAR(20)  NOT NULL,
    dia          VARCHAR(12)  NOT NULL,
    dni_paciente VARCHAR(8)   REFERENCES pacientes(dni) ON DELETE SET NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (sala, maquina, turno, dia)
);

-- ── 5. ATENCIONES ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS atenciones (
    id              SERIAL PRIMARY KEY,
    dni_paciente    VARCHAR(8)  NOT NULL REFERENCES pacientes(dni) ON DELETE CASCADE,
    fecha           DATE        NOT NULL,
    tipo_cita       VARCHAR(60) NOT NULL,
    estado          VARCHAR(20) DEFAULT 'Atendido',
    observaciones   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── 6. EVOLUCIÓN / NOTAS ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS evolucion (
    id           SERIAL PRIMARY KEY,
    dni_paciente VARCHAR(8)  NOT NULL REFERENCES pacientes(dni) ON DELETE CASCADE,
    fecha        DATE        NOT NULL,
    tipo         VARCHAR(60) NOT NULL,
    nota         TEXT        NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════
--  ÍNDICES (mejoran velocidad de búsqueda)
-- ═══════════════════════════════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_agenda_fecha        ON agenda (fecha);
CREATE INDEX IF NOT EXISTS idx_agenda_estado       ON agenda (estado);
CREATE INDEX IF NOT EXISTS idx_agenda_dni          ON agenda (dni_paciente);
CREATE INDEX IF NOT EXISTS idx_fichas_dni          ON fichas (dni_paciente);
CREATE INDEX IF NOT EXISTS idx_atenciones_fecha    ON atenciones (fecha);
CREATE INDEX IF NOT EXISTS idx_atenciones_dni      ON atenciones (dni_paciente);
CREATE INDEX IF NOT EXISTS idx_evolucion_dni       ON evolucion (dni_paciente);
CREATE INDEX IF NOT EXISTS idx_pacientes_apellidos ON pacientes USING gin (apellidos gin_trgm_ops);


-- ═══════════════════════════════════════════════════════════════
--  EXTENSIÓN para búsqueda de texto (ilike rápido)
-- ═══════════════════════════════════════════════════════════════
CREATE EXTENSION IF NOT EXISTS pg_trgm;


-- ═══════════════════════════════════════════════════════════════
--  ROW LEVEL SECURITY (RLS)
--  Con la service_key del backend las políticas se bypasean;
--  sirven para proteger accesos directos desde el frontend.
-- ═══════════════════════════════════════════════════════════════
ALTER TABLE pacientes    ENABLE ROW LEVEL SECURITY;
ALTER TABLE agenda       ENABLE ROW LEVEL SECURITY;
ALTER TABLE fichas       ENABLE ROW LEVEL SECURITY;
ALTER TABLE sala_maquinas ENABLE ROW LEVEL SECURITY;
ALTER TABLE atenciones   ENABLE ROW LEVEL SECURITY;
ALTER TABLE evolucion    ENABLE ROW LEVEL SECURITY;

-- Política: solo usuarios autenticados pueden ver y modificar datos
CREATE POLICY "auth_select" ON pacientes     FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "auth_insert" ON pacientes     FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "auth_update" ON pacientes     FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "auth_select" ON agenda        FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "auth_insert" ON agenda        FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "auth_update" ON agenda        FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "auth_select" ON fichas        FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "auth_insert" ON fichas        FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "auth_select" ON sala_maquinas FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "auth_insert" ON sala_maquinas FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "auth_update" ON sala_maquinas FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "auth_delete" ON sala_maquinas FOR DELETE USING (auth.role() = 'authenticated');

CREATE POLICY "auth_select" ON atenciones    FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "auth_insert" ON atenciones    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "auth_select" ON evolucion     FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "auth_insert" ON evolucion     FOR INSERT WITH CHECK (auth.role() = 'authenticated');


-- ═══════════════════════════════════════════════════════════════
--  DATOS DE PRUEBA (eliminar antes de producción real)
-- ═══════════════════════════════════════════════════════════════
INSERT INTO pacientes (dni, nombres, apellidos, edad, sexo, servicio, estado_civil, lugar, telefono)
VALUES
  ('40123456','María',   'Ríos Castillo',    62, 'F', 'HD',    'Casada',    'Huancayo', '987654321'),
  ('44921837','Ana',     'Vargas Lima',      58, 'F', 'DIPAC', 'Casada',    'Junín',    '987123456'),
  ('47234512','Juan',    'Ccoya Huamán',     67, 'M', 'HD',    'Viudo',     'Huancayo', '912345678'),
  ('44453298','Luis',    'Palomino Quispe',  71, 'M', 'HD',    'Casado',    'Chupaca',  '923456789'),
  ('44001122','Gonzalo', 'Torres Mendoza',   55, 'M', 'DIPAC', 'Casado',    'Huancayo', '934567890'),
  ('43219876','Rosa',    'Quispe Huanca',    69, 'F', 'HD',    'Divorciada','Concepción','945678901')
ON CONFLICT (dni) DO NOTHING;

INSERT INTO agenda (dni_paciente, fecha, hora, tipo_cita, estado)
VALUES
  ('40123456', CURRENT_DATE, '07:00', 'Atención Psicológica',  'Atendido'),
  ('44921837', CURRENT_DATE, '09:30', 'Intervención Familiar', 'Pendiente'),
  ('47234512', CURRENT_DATE, '10:00', 'Evaluación Diagnóstica','Pendiente'),
  ('44453298', CURRENT_DATE, '14:00', 'Intervención Individual','Programado'),
  ('44001122', CURRENT_DATE, '15:30', 'Atención Psicológica',  'Programado')
ON CONFLICT DO NOTHING;

INSERT INTO sala_maquinas (sala, maquina, turno, dia, dni_paciente)
VALUES
  ('Sala 1', 1, '07:00–12:00', 'Lunes', '40123456'),
  ('Sala 1', 2, '07:00–12:00', 'Lunes', '47234512'),
  ('Sala 1', 4, '07:00–12:00', 'Lunes', '44001122'),
  ('Sala 1', 6, '07:00–12:00', 'Lunes', '44453298'),
  ('Sala 1', 7, '07:00–12:00', 'Lunes', '43219876')
ON CONFLICT (sala, maquina, turno, dia) DO NOTHING;
