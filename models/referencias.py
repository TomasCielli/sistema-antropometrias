from database import get_connection


CAMPOS_NUMERICOS_REFERENCIA = [
    "peso",
    "pct_grasa",
    "masa_adiposa",
    "pct_muscular",
    "masa_muscular",
    "masa_osea",
    "masa_residual",
    "masa_piel",
]


def crear_referencia(datos):
    conn = get_connection()
    cursor = conn.cursor()

    columnas = ["nombre", "deporte"]
    valores = [datos["nombre"], datos["deporte"]]

    for campo in ["categoria", "posicion", "sexo", "descripcion"]:
        valor = datos.get(campo)
        if valor:
            columnas.append(campo)
            valores.append(valor)

    for campo in CAMPOS_NUMERICOS_REFERENCIA:
        valor = datos.get(campo)
        if valor is not None:
            columnas.append(campo)
            valores.append(valor)

    placeholders = ", ".join(["?"] * len(valores))
    sql = f"INSERT INTO referencias_antropometricas ({', '.join(columnas)}) VALUES ({placeholders})"
    cursor.execute(sql, valores)

    conn.commit()
    conn.close()


def modificar_referencia(referencia_id, datos):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM referencias_antropometricas WHERE id = ?", (referencia_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("La referencia no existe")

    columnas = []
    valores = []
    for clave, valor in datos.items():
        columnas.append(f"{clave} = ?")
        valores.append(valor)

    if not columnas:
        conn.close()
        return

    valores.append(referencia_id)
    sql = f"UPDATE referencias_antropometricas SET {', '.join(columnas)} WHERE id = ?"
    cursor.execute(sql, valores)

    conn.commit()
    conn.close()


def eliminar_referencia(referencia_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM referencias_antropometricas WHERE id = ?", (referencia_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("La referencia no existe")

    cursor.execute("DELETE FROM referencias_antropometricas WHERE id = ?", (referencia_id,))

    conn.commit()
    conn.close()


def obtener_referencia_por_id(referencia_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM referencias_antropometricas WHERE id = ?", (referencia_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None


def obtener_referencias():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM referencias_antropometricas
        ORDER BY LOWER(deporte), LOWER(COALESCE(categoria, '')), LOWER(nombre)
        """
    )
    rows = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return rows
