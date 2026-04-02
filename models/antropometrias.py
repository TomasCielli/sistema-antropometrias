from database import get_connection

CAMPOS_NUMERICOS = [
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

LABELS = {
    "peso": ("Peso", "kg"),
    "talla_corporal": ("Talla corporal", "cm"),
    "talla_sentado": ("Talla sentado", "cm"),
    "biacromial": ("Biacromial", "cm"),
    "torax_transverso": ("Tórax transverso", "cm"),
    "torax_anteroposterior": ("Tórax anteroposterior", "cm"),
    "bi_iliocrestideo": ("Bi-iliocrestídeo", "cm"),
    "humeral": ("Humeral", "cm"),
    "femoral": ("Femoral", "cm"),
    "cabeza": ("Cabeza", "cm"),
    "brazo_relajado": ("Brazo relajado", "cm"),
    "brazo_flexionado": ("Brazo flexionado", "cm"),
    "antebrazo": ("Antebrazo", "cm"),
    "torax_mesoesternal": ("Tórax mesoesternal", "cm"),
    "cintura": ("Cintura", "cm"),
    "cadera": ("Cadera", "cm"),
    "muslo_maximo": ("Muslo máximo", "cm"),
    "muslo_medial": ("Muslo medial", "cm"),
    "pantorrilla_maxima": ("Pantorrilla máxima", "cm"),
    "triceps": ("Tríceps", "mm"),
    "subescapular": ("Subescapular", "mm"),
    "supraespinal": ("Supraespinal", "mm"),
    "abdominal": ("Abdominal", "mm"),
    "muslo_medial_pliegue": ("Muslo medial (pliegue)", "mm"),
    "pantorrilla_pliegue": ("Pantorrilla (pliegue)", "mm"),
    "biceps": ("Bíceps", "mm"),
    "cresta_iliaca": ("Cresta ilíaca", "mm"),
}

SECCIONES = [
    ("Medidas generales", ["peso", "talla_corporal", "talla_sentado"]),
    ("Diámetros (cm)", ["biacromial", "torax_transverso", "torax_anteroposterior", "bi_iliocrestideo", "humeral", "femoral"]),
    ("Perímetros (cm)", ["cabeza", "brazo_relajado", "brazo_flexionado", "antebrazo", "torax_mesoesternal", "cintura", "cadera", "muslo_maximo", "muslo_medial", "pantorrilla_maxima"]),
    ("Pliegues cutáneos (mm)", ["triceps", "subescapular", "supraespinal", "abdominal", "muslo_medial_pliegue", "pantorrilla_pliegue", "biceps", "cresta_iliaca"]),
]


def crear_antropometria(datos):
    conn = get_connection()
    cursor = conn.cursor()

    jugador_id = datos.get("jugador_id")
    fecha = datos.get("fecha")

    # Duplicate check
    cursor.execute(
        "SELECT 1 FROM antropometrias WHERE jugador_id = ? AND fecha = ?",
        (jugador_id, fecha)
    )
    if cursor.fetchone():
        conn.close()
        raise ValueError("Ya existe una medición para este jugador en esa fecha")

    # Build dynamic INSERT
    columnas = ["jugador_id", "fecha"]
    valores = [jugador_id, fecha]

    for campo in ["posicion", "categoria"]:
        if campo in datos and datos[campo]:
            columnas.append(campo)
            valores.append(datos[campo])

    for campo in CAMPOS_NUMERICOS:
        if campo in datos and datos[campo] is not None:
            columnas.append(campo)
            valores.append(datos[campo])

    placeholders = ", ".join(["?"] * len(valores))
    sql = f"INSERT INTO antropometrias ({', '.join(columnas)}) VALUES ({placeholders})"
    cursor.execute(sql, valores)

    # Update player's posicion_actual and categoria_actual
    updates = []
    update_vals = []
    if datos.get("posicion"):
        updates.append("posicion_actual = ?")
        update_vals.append(datos["posicion"])
    if datos.get("categoria"):
        updates.append("categoria_actual = ?")
        update_vals.append(datos["categoria"])

    if updates:
        update_vals.append(jugador_id)
        cursor.execute(
            f"UPDATE jugadores SET {', '.join(updates)} WHERE id = ?",
            update_vals
        )

    conn.commit()
    conn.close()


def modificar_antropometria(antropometria_id, datos):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM antropometrias WHERE id = ?", (antropometria_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("La antropometría no existe")

    # Check duplicate date (excluding self)
    if "fecha" in datos:
        cursor.execute(
            "SELECT jugador_id FROM antropometrias WHERE id = ?",
            (antropometria_id,)
        )
        row = cursor.fetchone()
        jugador_id = row["jugador_id"]
        cursor.execute(
            "SELECT 1 FROM antropometrias WHERE jugador_id = ? AND fecha = ? AND id != ?",
            (jugador_id, datos["fecha"], antropometria_id)
        )
        if cursor.fetchone():
            conn.close()
            raise ValueError("Ya existe una medición para este jugador en esa fecha")

    columnas = []
    valores = []
    for clave, valor in datos.items():
        columnas.append(f"{clave} = ?")
        valores.append(valor)

    if not columnas:
        conn.close()
        return

    valores.append(antropometria_id)
    sql = f"UPDATE antropometrias SET {', '.join(columnas)} WHERE id = ?"
    cursor.execute(sql, valores)
    conn.commit()
    conn.close()


def eliminar_antropometria(antropometria_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT jugador_id FROM antropometrias WHERE id = ?", (antropometria_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("La antropometría no existe")
    jugador_id = row["jugador_id"]
    cursor.execute("DELETE FROM antropometrias WHERE id = ?", (antropometria_id,))
    conn.commit()
    conn.close()
    return jugador_id


def obtener_antropometria_por_id(antropometria_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM antropometrias WHERE id = ?", (antropometria_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def obtener_antropometrias_de_jugador(jugador_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM antropometrias WHERE jugador_id = ? ORDER BY fecha DESC",
        (jugador_id,)
    )
    filas = cursor.fetchall()
    conn.close()
    return [dict(f) for f in filas]
