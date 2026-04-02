from database import get_connection
from datetime import date, datetime
import math


def calcular_edad(fecha_nacimiento, fecha_referencia=None):
    """Calculate age in years from birth date."""
    if not fecha_nacimiento:
        return None
    if isinstance(fecha_nacimiento, str):
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
    if fecha_referencia is None:
        fecha_referencia = date.today()
    elif isinstance(fecha_referencia, str):
        fecha_referencia = datetime.strptime(fecha_referencia, "%Y-%m-%d").date()
    edad = fecha_referencia.year - fecha_nacimiento.year
    if (fecha_referencia.month, fecha_referencia.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def calcular_suma_pliegues(a):
    """Sum of all 8 skinfolds."""
    campos = ["triceps", "subescapular", "supraespinal", "abdominal",
              "muslo_medial_pliegue", "pantorrilla_pliegue", "biceps", "cresta_iliaca"]
    valores = [a.get(c) for c in campos]
    if any(v is None for v in valores):
        return None
    return sum(valores)


def calcular_suma_6_pliegues(a):
    """Sum of 6 specific skinfolds for Yuhasz formula."""
    campos = ["triceps", "subescapular", "supraespinal", "abdominal",
              "muslo_medial_pliegue", "pantorrilla_pliegue"]
    valores = [a.get(c) for c in campos]
    if any(v is None for v in valores):
        return None
    return sum(valores)


def calcular_porcentaje_grasa(a, sexo):
    """Yuhasz modified formula for body fat percentage.
    Male: %G = (Σ6 × 0.1051) + 2.585
    Female: %G = (Σ6 × 0.1580) + 3.580
    """
    suma6 = calcular_suma_6_pliegues(a)
    if suma6 is None or not sexo:
        return None
    if sexo == "Masculino":
        return round(suma6 * 0.1051 + 2.585, 2)
    else:
        return round(suma6 * 0.1580 + 3.580, 2)


def calcular_kg_grasa(peso, pct_grasa):
    """Fat mass in kg."""
    if peso is None or pct_grasa is None:
        return None
    return round(peso * pct_grasa / 100, 2)


def calcular_masa_muscular(a, peso, talla_cm, sexo, edad):
    """Lee 2000 formula for skeletal muscle mass.
    MM(kg) = 0.244 × peso + 7.80 × talla(m) + 6.6 × sexo_val - 0.098 × edad + sexo_val × (-3.3 + 0.0264 × antebrazo²) - 4.03
    sexo_val: 1 = Male, 0 = Female
    antebrazo: forearm max circumference in cm
    """
    if any(v is None for v in [peso, talla_cm, sexo, edad]):
        return None
    antebrazo = a.get("antebrazo")
    if antebrazo is None:
        return None
    sexo_val = 1 if sexo == "Masculino" else 0
    talla_m = talla_cm / 100
    mm = (0.244 * peso + 7.80 * talla_m + 6.6 * sexo_val
          - 0.098 * edad + sexo_val * (-3.3 + 0.0264 * antebrazo ** 2) - 4.03)
    return round(mm, 2)


def calcular_masa_osea(talla_cm, femoral_cm, humeral_cm):
    """Von Döbeln-Rocha formula for bone mass.
    MO(kg) = 3.02 × (talla(m)² × femoral(m) × humeral(m) × 400) ^ 0.712
    """
    if any(v is None for v in [talla_cm, femoral_cm, humeral_cm]):
        return None
    talla_m = talla_cm / 100
    femoral_m = femoral_cm / 100
    humeral_m = humeral_cm / 100
    base = talla_m ** 2 * femoral_m * humeral_m * 400
    if base <= 0:
        return None
    mo = 3.02 * (base ** 0.712)
    return round(mo, 2)


def calcular_masa_magra(peso, kg_grasa):
    """Lean mass = total weight - fat mass."""
    if peso is None or kg_grasa is None:
        return None
    return round(peso - kg_grasa, 2)


def calcular_composicion(jugador, antropometria):
    """Calculate all body composition metrics for one measurement."""
    peso = antropometria.get("peso")
    talla = antropometria.get("talla_corporal")
    sexo = jugador.get("sexo")
    fecha_nac = jugador.get("fecha_nacimiento")
    fecha_medicion = antropometria.get("fecha")

    edad = calcular_edad(fecha_nac, fecha_medicion)

    suma_pliegues = calcular_suma_pliegues(antropometria)
    pct_grasa = calcular_porcentaje_grasa(antropometria, sexo)
    kg_grasa = calcular_kg_grasa(peso, pct_grasa)
    masa_muscular = calcular_masa_muscular(antropometria, peso, talla, sexo, edad)
    masa_osea = calcular_masa_osea(talla, antropometria.get("femoral"), antropometria.get("humeral"))
    masa_magra = calcular_masa_magra(peso, kg_grasa)

    return {
        "fecha": antropometria.get("fecha"),
        "talla": talla,
        "peso": peso,
        "suma_pliegues": suma_pliegues,
        "pct_grasa": pct_grasa,
        "kg_grasa": kg_grasa,
        "masa_muscular": masa_muscular,
        "masa_osea": masa_osea,
        "masa_magra": masa_magra,
    }


def obtener_datos_informe(categoria=None, posicion=None, sexo=None):
    """Get report data: each player with their last 3 measurements and computed values."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get filtered players
    query = "SELECT * FROM jugadores WHERE 1=1"
    params = []

    if categoria:
        query += " AND LOWER(categoria_actual) = LOWER(?)"
        params.append(categoria)
    if posicion:
        query += " AND LOWER(posicion_actual) = LOWER(?)"
        params.append(posicion)
    if sexo:
        query += " AND sexo = ?"
        params.append(sexo)

    query += " ORDER BY apellido, nombre"
    cursor.execute(query, params)
    jugadores = [dict(j) for j in cursor.fetchall()]

    resultado = []
    for jugador in jugadores:
        # Get last 3 measurements for this player
        cursor.execute("""
            SELECT * FROM antropometrias
            WHERE jugador_id = ?
            ORDER BY fecha DESC
            LIMIT 3
        """, (jugador["id"],))
        mediciones = [dict(m) for m in cursor.fetchall()]

        # Calculate composition for each measurement
        composiciones = []
        for m in mediciones:
            comp = calcular_composicion(jugador, m)
            composiciones.append(comp)

        resultado.append({
            "jugador": jugador,
            "mediciones": composiciones,
        })

    conn.close()
    return resultado
