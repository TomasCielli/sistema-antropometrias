"""Seed script: creates 10 test players with varying anthropometry measurements."""
import os
import sys

# Ensure we can import from the project root
sys.path.insert(0, os.path.dirname(__file__))

from database import crear_base, get_connection

crear_base()
conn = get_connection()
c = conn.cursor()

# Clear existing data
c.execute("DELETE FROM antropometrias")
c.execute("DELETE FROM jugadores")

jugadores = [
    ("Gonzalez", "Matias", "40111001", "Masculino", "Pilar", "Plantel Superior", "2000-03-12", "Aumento de masa muscular", "221-555-1001", None),
    ("Rodriguez", "Lucia", "41222002", "Femenino", "Centro", "M19", "2005-07-24", "Optimización", "221-555-1002", "Lesión de rodilla derecha (2025)"),
    ("Fernandez", "Tomas", "42333003", "Masculino", "Hooker", "Plantel Superior", "1999-11-05", "Descenso de grasa", "221-555-1003", None),
    ("Lopez", "Camila", "43444004", "Femenino", "Wing", "M18", "2007-01-30", "Optimización", None, None),
    ("Martinez", "Santiago", "44555005", "Masculino", "Segunda línea", "Plantel Superior", "1998-06-18", "Aumento de masa muscular", "221-555-1005", "Vegano"),
    ("Garcia", "Valentina", "45666006", "Femenino", "Apertura", "M17", "2008-09-02", None, None, None),
    ("Diaz", "Franco", "46777007", "Masculino", "Ala", "M19", "2006-04-11", "Optimización", "221-555-1007", None),
    ("Alvarez", "Bruno", "47888008", "Masculino", "Numero 8", "Plantel Superior", "1997-12-25", "Descenso de grasa", "221-555-1008", "Operado hombro izquierdo (2024)"),
    ("Romero", "Sol", "48999009", "Femenino", "Medio scrum", "M16", "2009-08-14", "Aumento de masa muscular", None, "Primera temporada en el club"),
    ("Torres", "Nicolas", "49000010", "Masculino", "Fullback", "M15", "2010-02-20", None, "221-555-1010", None),
]

for j in jugadores:
    c.execute("""
        INSERT INTO jugadores (apellido, nombre, dni, sexo, posicion_actual, categoria_actual,
                               fecha_nacimiento, objetivo, telefono, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, j)

conn.commit()

# Get inserted IDs mapped by DNI
c.execute("SELECT id, dni FROM jugadores")
id_map = {row["dni"]: row["id"] for row in c.fetchall()}

# Base anthropometry template (realistic rugby player values)
def antro(jid, fecha, peso, talla, posicion, categoria, sexo_m=True, variacion=0):
    """Generate a realistic anthropometry record with slight variations."""
    v = variacion
    is_m = sexo_m
    return (
        jid, fecha, posicion, categoria,
        peso + v, talla,                         # peso, talla_corporal
        talla * 0.52,                             # talla_sentado
        42 + v * 0.1 if is_m else 38 + v * 0.1,  # biacromial
        30 + v * 0.05, 22 + v * 0.03,            # torax_transverso, torax_anteroposterior
        28 + v * 0.04,                             # bi_iliocrestideo
        7.0 + v * 0.02, 10.0 + v * 0.03,         # humeral, femoral
        57, 34 + v * 0.2, 37 + v * 0.2,          # cabeza, brazo_relajado, brazo_flexionado
        28 + v * 0.1,                              # antebrazo
        100 + v * 0.3, 84 + v * 0.5,             # torax_mesoesternal, cintura
        100 + v * 0.2,                             # cadera
        58 + v * 0.3, 54 + v * 0.2,              # muslo_maximo, muslo_medial
        38 + v * 0.1,                              # pantorrilla_maxima
        12 + v * 0.5, 14 + v * 0.3,              # triceps, subescapular
        10 + v * 0.4, 18 + v * 0.6,              # supraespinal, abdominal
        16 + v * 0.4, 10 + v * 0.2,              # muslo_medial_pliegue, pantorrilla_pliegue
        6 + v * 0.2, 14 + v * 0.5,               # biceps, cresta_iliaca
    )

campos_antro = """jugador_id, fecha, posicion, categoria, peso, talla_corporal, talla_sentado,
    biacromial, torax_transverso, torax_anteroposterior, bi_iliocrestideo,
    humeral, femoral, cabeza, brazo_relajado, brazo_flexionado, antebrazo,
    torax_mesoesternal, cintura, cadera, muslo_maximo, muslo_medial,
    pantorrilla_maxima, triceps, subescapular, supraespinal, abdominal,
    muslo_medial_pliegue, pantorrilla_pliegue, biceps, cresta_iliaca"""

placeholders = ", ".join(["?"] * 31)
sql = f"INSERT INTO antropometrias ({campos_antro}) VALUES ({placeholders})"

# Player 1: Gonzalez - 4 measurements
jid = id_map["40111001"]
c.execute(sql, antro(jid, "2025-06-15", 92, 182, "Pilar", "Plantel Superior", True, 0))
c.execute(sql, antro(jid, "2025-09-20", 94, 182, "Pilar", "Plantel Superior", True, 1))
c.execute(sql, antro(jid, "2026-01-10", 95, 182, "Pilar", "Plantel Superior", True, 2))
c.execute(sql, antro(jid, "2026-03-28", 96, 182, "Pilar", "Plantel Superior", True, 2.5))

# Player 2: Rodriguez - 3 measurements
jid = id_map["41222002"]
c.execute(sql, antro(jid, "2025-08-01", 65, 168, "Centro", "M19", False, 0))
c.execute(sql, antro(jid, "2025-12-15", 64, 168, "Centro", "M19", False, -0.5))
c.execute(sql, antro(jid, "2026-03-20", 63, 168, "Centro", "M19", False, -1))

# Player 3: Fernandez - 5 measurements (most data)
jid = id_map["42333003"]
c.execute(sql, antro(jid, "2025-03-10", 105, 178, "Hooker", "Plantel Superior", True, 4))
c.execute(sql, antro(jid, "2025-06-22", 103, 178, "Hooker", "Plantel Superior", True, 3))
c.execute(sql, antro(jid, "2025-09-15", 101, 178, "Hooker", "Plantel Superior", True, 2))
c.execute(sql, antro(jid, "2025-12-20", 99, 178, "Hooker", "Plantel Superior", True, 1))
c.execute(sql, antro(jid, "2026-03-25", 97, 178, "Hooker", "Plantel Superior", True, 0))

# Player 4: Lopez - 2 measurements
jid = id_map["43444004"]
c.execute(sql, antro(jid, "2025-10-05", 60, 165, "Wing", "M18", False, 0))
c.execute(sql, antro(jid, "2026-02-18", 61, 165, "Wing", "M18", False, 0.5))

# Player 5: Martinez - 4 measurements
jid = id_map["44555005"]
c.execute(sql, antro(jid, "2025-04-01", 108, 195, "Segunda línea", "Plantel Superior", True, 3))
c.execute(sql, antro(jid, "2025-07-15", 110, 195, "Segunda línea", "Plantel Superior", True, 3.5))
c.execute(sql, antro(jid, "2025-11-20", 111, 195, "Segunda línea", "Plantel Superior", True, 4))
c.execute(sql, antro(jid, "2026-03-15", 112, 195, "Segunda línea", "Plantel Superior", True, 4.5))

# Player 6: Garcia - 1 measurement
jid = id_map["45666006"]
c.execute(sql, antro(jid, "2026-03-01", 55, 160, "Apertura", "M17", False, 0))

# Player 7: Diaz - 3 measurements
jid = id_map["46777007"]
c.execute(sql, antro(jid, "2025-07-10", 85, 180, "Ala", "M19", True, 0))
c.execute(sql, antro(jid, "2025-11-05", 86, 180, "Ala", "M19", True, 0.5))
c.execute(sql, antro(jid, "2026-03-10", 87, 180, "Ala", "M19", True, 1))

# Player 8: Alvarez - 5 measurements
jid = id_map["47888008"]
c.execute(sql, antro(jid, "2025-02-15", 102, 185, "Numero 8", "Plantel Superior", True, 5))
c.execute(sql, antro(jid, "2025-05-20", 100, 185, "Numero 8", "Plantel Superior", True, 4))
c.execute(sql, antro(jid, "2025-08-10", 98, 185, "Numero 8", "Plantel Superior", True, 3))
c.execute(sql, antro(jid, "2025-11-25", 96, 185, "Numero 8", "Plantel Superior", True, 2))
c.execute(sql, antro(jid, "2026-03-30", 95, 185, "Numero 8", "Plantel Superior", True, 1))

# Player 9: Romero - 2 measurements
jid = id_map["48999009"]
c.execute(sql, antro(jid, "2026-01-20", 52, 158, "Medio scrum", "M16", False, 0))
c.execute(sql, antro(jid, "2026-03-22", 53, 158, "Medio scrum", "M16", False, 0.5))

# Player 10: Torres - 0 measurements (new player, no data yet)

conn.commit()
conn.close()

print("Seed completado:")
print("  10 jugadores creados")
print("  29 antropometrías cargadas")
print("  Torres (M15) sin mediciones")
