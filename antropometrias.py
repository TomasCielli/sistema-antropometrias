import sqlite3
from database import DB_NAME
from datetime import datetime


def crear_antropometria(datos):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # -------------------------
    # Validaciones obligatorias
    # -------------------------
    if "jugador_id" not in datos or "fecha" not in datos:
        print("Error: jugador_id y fecha son obligatorios")
        conn.close()
        return

    # validar fecha
    try:
        datetime.strptime(datos["fecha"], "%Y-%m-%d")
    except ValueError:
        print("Error: formato de fecha inválido (usar YYYY-MM-DD)")
        conn.close()
        return

    # -------------------------
    # Evitar duplicados
    # -------------------------
    cursor.execute("""
        SELECT 1
        FROM antropometrias
        WHERE jugador_id = ? AND fecha = ?
    """, (datos["jugador_id"], datos["fecha"]))

    if cursor.fetchone():
        print("Error: ya existe una medición para este jugador en esa fecha")
        conn.close()
        return

    # -------------------------
    # Validación de valores numéricos
    # -------------------------
    campos_numericos = [
        "peso", "talla_corporal", "talla_sentado",
        "biacromial", "torax_transverso", "torax_anteroposterior",
        "bi_iliocrestideo", "humeral", "femoral",
        "cabeza", "brazo_relajado", "brazo_flexionado",
        "antebrazo", "torax_mesoesternal", "cintura",
        "cadera", "muslo_maximo", "muslo_medial",
        "pantorrilla_maxima", "triceps", "subescapular",
        "supraespinal", "abdominal", "muslo_medial_pliegue",
        "pantorrilla_pliegue", "biceps", "cresta_iliaca"
    ]

    for campo in campos_numericos:
        if campo in datos and datos[campo] is not None:
            if not isinstance(datos[campo], (int, float)):
                print(f"Error: {campo} debe ser numérico")
                conn.close()
                return

            if datos[campo] < 0:
                print(f"Error: {campo} no puede ser negativo")
                conn.close()
                return

    # -------------------------
    # Insert dinámico
    # -------------------------
    columnas = []
    valores = []
    placeholders = []

    cursor.execute("PRAGMA table_info(antropometrias)")
    columnas_tabla = [col[1] for col in cursor.fetchall()]

    for clave, valor in datos.items():
        if clave in columnas_tabla:
            columnas.append(clave)
            valores.append(valor)
            placeholders.append("?")

    sql = f"""
    INSERT INTO antropometrias ({", ".join(columnas)})
    VALUES ({", ".join(placeholders)})
    """

    cursor.execute(sql, valores)

    # -------------------------
    # Actualizar posición y categoría del jugador
    # -------------------------
    if "posicion" in datos or "categoria" in datos:
        campos_update = []
        valores_update = []

        if "posicion" in datos:
            campos_update.append("posicion_actual = ?")
            valores_update.append(datos["posicion"])

        if "categoria" in datos:
            campos_update.append("categoria_actual = ?")
            valores_update.append(datos["categoria"])

        valores_update.append(datos["jugador_id"])

        cursor.execute(f"""
            UPDATE jugadores
            SET {", ".join(campos_update)}
            WHERE id = ?
        """, valores_update)

    conn.commit()
    conn.close()

    print("Antropometría guardada correctamente")
    
def modificar_antropometria(antropometria_id, datos):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if not existe_antropometria(antropometria_id, cursor):
        print("Error: la antropometría no existe")
        conn.close()
        return

    columnas = []
    valores = []

    for clave, valor in datos.items():
        columnas.append(f"{clave} = ?")
        valores.append(valor)

    valores.append(antropometria_id)

    sql = f"""
    UPDATE antropometrias
    SET {", ".join(columnas)}
    WHERE id = ?
    """

    cursor.execute(sql, valores)

    conn.commit()
    conn.close()

    print("Antropometría actualizada correctamente")

def eliminar_antropometria(antropometria_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if not existe_antropometria(antropometria_id, cursor):
        print("Error: la antropometría no existe")
        conn.close()
        return

    cursor.execute("""
        DELETE FROM antropometrias
        WHERE id = ?
    """, (antropometria_id,))

    conn.commit()
    conn.close()

    print("Antropometría eliminada correctamente")

def obtener_antropometrias_de_jugador(jugador_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM antropometrias
        WHERE jugador_id = ?
        ORDER BY fecha DESC
    """, (jugador_id,))

    filas = cursor.fetchall()

    if filas is None:
        return None

    conn.close()

    return [dict(fila) for fila in filas]

def obtener_ultima_antropometria(jugador_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM antropometrias
        WHERE jugador_id = ?
        ORDER BY fecha DESC
        LIMIT 1
    """, (jugador_id,))

    fila = cursor.fetchone()

    conn.close()

    if fila is None:
        return None

    return dict(fila)

def obtener_jugadores_con_ultima_antropometria():

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            j.id,
            j.nombre,
            j.apellido,
            j.dni,
            j.posicion_actual,
            j.categoria_actual,
            a.fecha AS fecha_ultima_medicion,
            a.peso AS peso_actual,

            CASE
                WHEN a.fecha IS NOT NULL
                THEN CAST(julianday('now') - julianday(a.fecha) AS INTEGER)
                ELSE NULL
            END AS dias_desde_ultima_medicion

        FROM jugadores j
        LEFT JOIN antropometrias a
            ON a.id = (
                SELECT id
                FROM antropometrias
                WHERE jugador_id = j.id
                ORDER BY fecha DESC
                LIMIT 1
            )
        ORDER BY j.apellido, j.nombre
    """)

    filas = cursor.fetchall()
    conn.close()

    return [dict(fila) for fila in filas]

def existe_antropometria(antropometria_id, cursor):
    cursor.execute("""
        SELECT 1
        FROM antropometrias
        WHERE id = ?
    """, (antropometria_id,))
    
    return cursor.fetchone() is not None

