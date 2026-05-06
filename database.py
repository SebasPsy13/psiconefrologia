import sqlite3
import pandas as pd
import json

def get_connection():
    """Establece la conexión con la base de datos SQLite."""
    return sqlite3.connect('psiconefrologia.db', check_same_thread=False)

def create_tables():
    """Crea la estructura de tablas necesaria para el hospital."""
    conn = get_connection()
    c = conn.cursor()
    
    # 1. TABLA PACIENTES: 14 campos obligatorios (Filiación EsSalud)
    c.execute('''CREATE TABLE IF NOT EXISTS pacientes
                 (dni TEXT PRIMARY KEY, 
                  nombres TEXT, 
                  apellidos TEXT, 
                  edad INTEGER, 
                  sexo TEXT, 
                  fecha_nac TEXT, 
                  lugar TEXT, 
                  estado_civil TEXT, 
                  hijos INTEGER, 
                  instruccion TEXT, 
                  trabajo TEXT, 
                  direccion TEXT, 
                  telefono TEXT, 
                  servicio TEXT)''')
    
    # 2. TABLA AGENDA: Incluye 'observaciones' para redacción clínica
    c.execute('''CREATE TABLE IF NOT EXISTS agenda
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  dni_paciente TEXT, 
                  fecha TEXT, 
                  tipo_cita TEXT, 
                  estado TEXT DEFAULT 'Pendiente',
                  observaciones TEXT, 
                  FOREIGN KEY(dni_paciente) REFERENCES pacientes(dni))''')
    
    # 3. TABLA FICHAS: Formato HD:DIPAC completo en JSON
    c.execute('''CREATE TABLE IF NOT EXISTS fichas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  dni_paciente TEXT, 
                  fecha_entrevista TEXT, 
                  datos_json TEXT,
                  FOREIGN KEY(dni_paciente) REFERENCES pacientes(dni))''')

    # 4. TABLA MAPEO_CAMAS: Mapa digital de salas (2 salas, 8 camas c/u)
    c.execute('''CREATE TABLE IF NOT EXISTS mapeo_camas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sala TEXT,
                  cama INTEGER,
                  turno TEXT,
                  dia TEXT,
                  dni_paciente TEXT,
                  UNIQUE(sala, cama, turno, dia),
                  FOREIGN KEY(dni_paciente) REFERENCES pacientes(dni))''')
    
    conn.commit()
    conn.close()

# --- FUNCIONES DE PACIENTES ---

def guardar_paciente(dni, nom, ape, eda, sex, fnac, lug, civ, hij, ins, tra, dire, tel, ser):
    conn = get_connection()
    try:
        # Al nombrar las columnas (dni, nombres, etc.), ignoramos cualquier columna extra 
        # que se haya creado por error en la base de datos física.
        query = """
            INSERT INTO pacientes (
                dni, nombres, apellidos, edad, sexo, fecha_nac, 
                lugar, estado_civil, hijos, instruccion, trabajo, 
                direccion, telefono, servicio
            ) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        conn.execute(query, (dni, nom, ape, eda, sex, fnac, lug, civ, hij, ins, tra, dire, tel, ser))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    finally:
        conn.close()

# --- FUNCIONES DE AGENDA E INTERVENCIÓN ---

def agendar_cita(dni, fecha, tipo):
    conn = get_connection()
    conn.execute("INSERT INTO agenda (dni_paciente, fecha, tipo_cita) VALUES (?,?,?)", 
                 (dni, str(fecha), tipo))
    conn.commit()
    conn.close()

def guardar_actividad_ruta(dni, fecha, actividad, observaciones):
    conn = get_connection()
    try:
        # 1. Eliminamos cualquier registro previo idéntico para evitar duplicidad
        conn.execute("""
            DELETE FROM agenda 
            WHERE dni_paciente = ? AND fecha = ? AND tipo_cita = ?
        """, (dni, str(fecha), actividad))
        
        # 2. Insertamos la versión actualizada
        conn.execute("""
            INSERT INTO agenda (dni_paciente, fecha, tipo_cita, estado, observaciones)
            VALUES (?, ?, ?, 'Atendido', ?)
        """, (dni, str(fecha), actividad, observaciones))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def obtener_registros_por_fecha(fecha):
    conn = get_connection()
    query = f"SELECT dni_paciente, tipo_cita, observaciones FROM agenda WHERE fecha = '{fecha}'"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def eliminar_registro_agenda(id_registro):
    """Elimina permanentemente un registro del historial."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM agenda WHERE id = ?", (id_registro,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# --- FUNCIONES DE FICHAS ---

def guardar_ficha(dni, fecha, datos_dict):
    conn = get_connection()
    try:
        datos_json = json.dumps(datos_dict)
        conn.execute("INSERT INTO fichas (dni_paciente, fecha_entrevista, datos_json) VALUES (?,?,?)", 
                     (dni, str(fecha), datos_json))
        conn.commit()
    finally:
        conn.close()

def obtener_ultima_ficha(dni):
    """Recupera los datos de la ficha más reciente de un paciente para cargarlos en la evolución."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT datos_json FROM fichas WHERE dni_paciente = ? ORDER BY id DESC LIMIT 1", (dni,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    except Exception as e:
        print(f"Error al obtener ficha: {e}")
        return None
    finally:
        conn.close()

def actualizar_monitoreo(dni, nuevo_monitoreo):
    """Actualiza solo el monitoreo bio-conductual en la última ficha del paciente."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1. Obtener el ID y los datos de la ficha más reciente
        cursor.execute("SELECT id, datos_json FROM fichas WHERE dni_paciente = ? ORDER BY id DESC LIMIT 1", (dni,))
        row = cursor.fetchone()
        
        if row:
            id_ficha = row[0]
            datos = json.loads(row[1])
            datos['monitoreo'] = nuevo_monitoreo 
            
            # 2. Guardar de nuevo usando el ID específico
            cursor.execute("UPDATE fichas SET datos_json = ? WHERE id = ?", 
                           (json.dumps(datos), id_ficha))
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Error al actualizar monitoreo: {e}")
        return False
    finally:
        conn.close()

# --- FUNCIONES DEL MAPA DE SALAS ---

def asignar_paciente_cama(sala, cama, turno, dia, dni):
    """Asigna o actualiza a un paciente en una máquina específica."""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO mapeo_camas (sala, cama, turno, dia, dni_paciente)
            VALUES (?, ?, ?, ?, ?)
        """, (sala, cama, turno, dia, dni))
        conn.commit()
    finally:
        conn.close()

def obtener_mapa_sala(sala, turno, dia):
    """Obtiene la distribución de pacientes para una sala, turno y día específicos."""
    conn = get_connection()
    query = f"""
        SELECT m.cama, p.dni, p.nombres, p.apellidos 
        FROM mapeo_camas m
        JOIN pacientes p ON m.dni_paciente = p.dni
        WHERE m.sala = '{sala}' AND m.turno = '{turno}' AND m.dia = '{dia}'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def quitar_paciente_cama(sala, cama, turno, dia):
    """Elimina la asignación de un paciente en un slot específico."""
    conn = get_connection()
    conn.execute("""
        DELETE FROM mapeo_camas 
        WHERE sala = ? AND cama = ? AND turno = ? AND dia = ?
    """, (sala, cama, turno, dia))
    conn.commit()
    conn.close()

def vaciar_base_de_datos():
    """Elimina todos los registros de todas las tablas manteniendo la estructura."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Lista de todas tus tablas
        tablas = ['pacientes', 'agenda', 'fichas', 'mapeo_camas']
        for tabla in tablas:
            cursor.execute(f"DELETE FROM {tabla}")
        
        # Reiniciar los contadores de ID (autoincrementales)
        cursor.execute("DELETE FROM sqlite_sequence")
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al vaciar base de datos: {e}")
        return False
    finally:
        conn.close()

def obtener_produccion_mensual(mes, anio):
    """Obtiene todas las atenciones del mes y año seleccionados con nombres estandarizados."""
    conn = get_connection()
    mes_str = str(mes).zfill(2)
    # Importante: 'dni_paciente AS dni' para que el resto del código lo reconozca
    query = f"""
        SELECT a.id, a.dni_paciente AS dni, p.nombres, p.apellidos, a.fecha, a.tipo_cita, a.observaciones
        FROM agenda a
        JOIN pacientes p ON a.dni_paciente = p.dni
        WHERE strftime('%m', a.fecha) = '{mes_str}' 
          AND strftime('%Y', a.fecha) = '{anio}'
          AND a.estado = 'Atendido'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def actualizar_esquema_diagnostico():
    """Añade la columna diagnostico a la tabla agenda si no existe."""
    conn = get_connection()
    try:
        conn.execute("ALTER TABLE agenda ADD COLUMN diagnostico TEXT")
        conn.commit()
    except:
        # Si la columna ya existe, no hará nada
        pass
    finally:
        conn.close()

def get_connection():
    return sqlite3.connect('psiconefrologia.db', check_same_thread=False)

def actualizar_esquema_diagnostico():
    """Añade la columna diagnostico a la tabla agenda para separar lo administrativo de lo clínico."""
    conn = get_connection()
    try:
        # Intentamos agregar la columna. Si ya existe, SQLite lanzará un error que ignoraremos.
        conn.execute("ALTER TABLE agenda ADD COLUMN diagnostico TEXT")
        conn.commit()
    except:
        pass
    finally:
        conn.close()

def obtener_atenciones_mensuales_completas(mes, anio):
    """Obtiene datos detallados ordenados cronológicamente para el informe mensual."""
    conn = get_connection()
    mes_str = str(mes).zfill(2)
    query = f"""
        SELECT a.id, p.dni, p.nombres, p.apellidos, p.edad, p.sexo, 
               a.fecha, a.tipo_cita, a.diagnostico
        FROM agenda a
        JOIN pacientes p ON a.dni_paciente = p.dni
        WHERE strftime('%m', a.fecha) = '{mes_str}' 
          AND strftime('%Y', a.fecha) = '{anio}'
          AND a.estado = 'Atendido'
        ORDER BY a.fecha ASC, a.tipo_cita ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def guardar_diagnostico_administrativo(id_registro, dx_texto):
    """Guarda el diagnóstico sin modificar la evolución (observaciones)."""
    conn = get_connection()
    try:
        conn.execute("UPDATE agenda SET diagnostico = ? WHERE id = ?", (dx_texto, id_registro))
        conn.commit()
        return True
    finally:
        conn.close()

def actualizar_filiacion_completa(dni, lugar, direccion, telefono, est_civil, instruccion, trabajo, servicio):
    """Actualiza los datos de base del paciente desde cualquier módulo."""
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE pacientes 
            SET lugar = ?, direccion = ?, telefono = ?, 
                estado_civil = ?, instruccion = ?, trabajo = ?, servicio = ?
            WHERE dni = ?
        """, (lugar, direccion, telefono, est_civil, instruccion, trabajo, servicio, dni))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return False
    finally:
        conn.close()

def eliminar_atenciones_por_fecha(fecha):
    """Elimina todos los registros de la tabla agenda para una fecha específica."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM agenda WHERE fecha = ?", (str(fecha),))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar jornada: {e}")
        return False
    finally:
        conn.close()

# Añadir a database.py dentro de create_tables()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pruebas_psicometricas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni_paciente TEXT,
            fecha TEXT,
            prueba TEXT,
            resultados_json TEXT,
            FOREIGN KEY(dni_paciente) REFERENCES pacientes(dni)
        )
    ''')
    
def guardar_resultado_psicometrico(dni, prueba, resultados):
    """Guarda el resultado de una prueba psicométrica en la base de datos."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO pruebas_psicometricas (dni_paciente, fecha, prueba, resultados_json) VALUES (?, date('now', 'localtime'), ?, ?)",
            (dni, prueba, json.dumps(resultados))
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al guardar prueba: {e}")
        return False
    finally:
        conn.close()
