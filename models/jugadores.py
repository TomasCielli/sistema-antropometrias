from database import get_connection

CATEGORIAS = ["M15", "M16", "M17", "M18", "M19", "Plantel Superior"]
POSICIONES = ["Ala", "Apertura", "Centro", "Fullback", "Hooker", "Medio scrum", "Numero 8", "Pilar", "Segunda línea", "Segundo centro", "Wing"]
SEXOS = ["Masculino", "Femenino"]
OBJETIVOS = ["Optimización", "Aumento de masa muscular", "Descenso de grasa"]


def crear_jugador(nombre, apellido, dni, sexo, fecha_nacimiento, posicion=None, categoria=None, objetivo=None, telefono=None, observaciones=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO jugadores (nombre, apellido, dni, sexo, fecha_nacimiento, posicion_actual, categoria_actual, objetivo, telefono, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre.strip(), apellido.strip(), dni.strip(), sexo, fecha_nacimiento, posicion, categoria, objetivo, telefono, observaciones))
        conn.commit()
    except Exception as e:
        conn.close()
        raise e
    conn.close()


def modificar_jugador(jugador_id, datos):
    conn = get_connection()
    cursor = conn.cursor()

    # Check player exists
    cursor.execute("SELECT 1 FROM jugadores WHERE id = ?", (jugador_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("El jugador no existe")

    # Check DNI uniqueness excluding self
    if "dni" in datos:
        cursor.execute("SELECT id FROM jugadores WHERE dni = ? AND id != ?", (datos["dni"], jugador_id))
        if cursor.fetchone():
            conn.close()
            raise ValueError("Ya existe un jugador con ese DNI")

    columnas = []
    valores = []
    for clave, valor in datos.items():
        columnas.append(f"{clave} = ?")
        valores.append(valor)

    if not columnas:
        conn.close()
        raise ValueError("No se enviaron datos para actualizar")

    valores.append(jugador_id)
    sql = f"UPDATE jugadores SET {', '.join(columnas)} WHERE id = ?"
    cursor.execute(sql, valores)
    conn.commit()
    conn.close()


def eliminar_jugador(jugador_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM jugadores WHERE id = ?", (jugador_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("El jugador no existe")
    cursor.execute("DELETE FROM jugadores WHERE id = ?", (jugador_id,))
    conn.commit()
    conn.close()


def obtener_jugador_por_id(jugador_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jugadores WHERE id = ?", (jugador_id,))
    jugador = cursor.fetchone()
    conn.close()
    if jugador:
        return dict(jugador)
    return None


def obtener_jugadores_con_ultima_antropometria():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            j.id, j.nombre, j.apellido, j.dni, j.sexo,
            j.posicion_actual, j.categoria_actual,
            j.fecha_nacimiento, j.objetivo,
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
                SELECT id FROM antropometrias
                WHERE jugador_id = j.id
                ORDER BY fecha DESC
                LIMIT 1
            )
        ORDER BY j.apellido, j.nombre
    """)
    filas = cursor.fetchall()
    conn.close()
    return [dict(f) for f in filas]
