import sqlite3
from database import DB_NAME


def crear_jugador(nombre, apellido, dni, posicion, categoria, fecha_nacimiento=None):
    # conectar a la base de datos
    conn = sqlite3.connect(DB_NAME)

    # activar claves foráneas
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    try:
        # insertar jugador en la base
        cursor.execute("""
        INSERT INTO jugadores (
            nombre,
            apellido,
            dni,
            posicion_actual,
            categoria_actual,
            fecha_nacimiento
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nombre,
            apellido,
            dni,
            posicion,
            categoria,
            fecha_nacimiento
        ))

        # guardar cambios
        conn.commit()

        print("Jugador creado correctamente")

    except sqlite3.IntegrityError:
        # ocurre si el DNI ya existe
        raise ValueError("Ya existe un jugador con ese DNI")

    finally:
        # cerrar conexión
        conn.close()

def modificar_jugador(jugador_id, datos):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    if not existe_jugador(jugador_id, cursor):
        conn.close()
        raise ValueError("El jugador no existe")

    # Si se está intentando cambiar el DNI, verificar duplicados
    if "dni" in datos:
        cursor.execute("""
            SELECT id
            FROM jugadores
            WHERE dni = ?
            AND id != ?
        """, (datos["dni"], jugador_id))

        if cursor.fetchone():
            conn.close()
            raise ValueError("Ese DNI ya pertenece a otro jugador")

    columnas = []
    valores = []

    for clave, valor in datos.items():
        columnas.append(f"{clave} = ?")
        valores.append(valor)

    valores.append(jugador_id)

    sql = f"""
    UPDATE jugadores
    SET {", ".join(columnas)}
    WHERE id = ?
    """

    cursor.execute(sql, valores)

    if not datos:
        conn.close()
        raise ValueError("No se enviaron datos para actualizar")

    conn.commit()
    conn.close()

def eliminar_jugador(jugador_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    if not existe_jugador(jugador_id, cursor):
        print("Error: el jugador no existe")
        conn.close()
        return

    cursor.execute("""
        DELETE FROM jugadores
        WHERE id = ?
    """, (jugador_id,))

    conn.commit()
    conn.close()

    print("Jugador eliminado correctamente")

def obtener_jugadores():
    # conectar a la base
    conn = sqlite3.connect(DB_NAME)

    # permite acceder a las columnas por nombre
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # consulta para traer todos los jugadores
    cursor.execute("""
    SELECT *
    FROM jugadores
    ORDER BY apellido, nombre
    """)

    # obtener resultados
    jugadores = cursor.fetchall()

    conn.close()

    return jugadores

def obtener_jugador_por_id(jugador_id):
    # conectar a la base
    conn = sqlite3.connect(DB_NAME)

    # permite acceder a las columnas por nombre
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # buscar jugador por id
    cursor.execute("""
    SELECT *
    FROM jugadores
    WHERE id = ?
    """, (jugador_id,))

    jugador = cursor.fetchone()

    conn.close()

    return jugador

def buscar_jugadores(texto_busqueda):

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    texto = f"%{texto_busqueda.lower()}%"

    cursor.execute("""
        SELECT
            j.id,
            j.nombre,
            j.apellido,
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
        WHERE
            LOWER(j.nombre) LIKE ?
            OR LOWER(j.apellido) LIKE ?
        ORDER BY j.apellido, j.nombre
    """, (texto, texto))

    filas = cursor.fetchall()
    conn.close()

    return [dict(fila) for fila in filas]

def existe_jugador(jugador_id, cursor):
    cursor.execute("""
        SELECT 1
        FROM jugadores
        WHERE id = ?
    """, (jugador_id,))
    
    return cursor.fetchone() is not None

def obtener_jugadores_filtrados(busqueda=None, posicion=None, categoria=None):

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM jugadores WHERE 1=1"
    parametros = []

    # Busqueda general (nombre, apellido o dni)
    if busqueda:
        query += """
        AND (
            LOWER(nombre) LIKE LOWER(?) OR
            LOWER(apellido) LIKE LOWER(?) OR
            dni LIKE ?
        )
        """
        parametros.extend([
            f"%{busqueda}%",
            f"%{busqueda}%",
            f"%{busqueda}%"
        ])

    # Filtro por posición
    if posicion:
        query += " AND LOWER(posicion_actual) = LOWER(?)"
        parametros.append(posicion)

    # Filtro por categoría
    if categoria:
        query += " AND LOWER(categoria_actual) = LOWER(?)"
        parametros.append(categoria)

    query += " ORDER BY apellido, nombre"

    cursor.execute(query, parametros)
    jugadores = cursor.fetchall()

    conn.close()

    return [dict(j) for j in jugadores]

def obtener_jugadores_por_ultima_medicion():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT 
        j.*,
        MAX(a.fecha) as ultima_medicion
    FROM jugadores j
    LEFT JOIN antropometrias a
        ON j.id = a.jugador_id
    GROUP BY j.id
    ORDER BY ultima_medicion DESC
    """

    cursor.execute(query)
    jugadores = cursor.fetchall()

    conn.close()

    return [dict(j) for j in jugadores]

