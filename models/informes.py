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
    """Sum of 6 skinfolds (ISAK): triceps + subescapular + supraespinal + abdominal + muslo + pantorrilla."""
    campos = ["triceps", "subescapular", "supraespinal", "abdominal",
              "muslo_medial_pliegue", "pantorrilla_pliegue"]
    valores = [a.get(c) for c in campos]
    if any(v is None for v in valores):
        return None
    return sum(valores)


# --- SUPERFICIE CORPORAL (Du Bois) ---

def calcular_superficie_corporal(peso, talla_cm):
    """Du Bois formula: SC = 0.007184 * peso^0.425 * talla^0.725"""
    if peso is None or talla_cm is None:
        return None
    return round(0.007184 * (peso ** 0.425) * (talla_cm ** 0.725), 4)


# --- MASA ADIPOSA (ISAK / Ross & Kerr) ---

def calcular_masa_adiposa(a, peso, talla_cm):
    """ISAK/Ross & Kerr adipose mass.
    Σ6 = triceps + subescapular + supraespinal + abdominal + muslo + pantorrilla
    Masa adiposa (kg) = (Σ6 * 0.1051) * SC
    % grasa = (masa adiposa / peso) * 100
    """
    suma6 = calcular_suma_6_pliegues(a)
    sc = calcular_superficie_corporal(peso, talla_cm)
    if suma6 is None or sc is None or peso is None or peso == 0:
        return None, None
    masa_adiposa = round((suma6 * 0.1051) * sc, 2)
    pct_grasa = round((masa_adiposa / peso) * 100, 2)
    return masa_adiposa, pct_grasa


# --- MASA MUSCULAR (Lee adaptada ISAK) ---

def calcular_masa_muscular(a, talla_cm, sexo, edad):
    """Lee formula adapted ISAK.
    Corrected perimeters:
        brazo_corr = brazo_relajado - (π * triceps / 10)
        muslo_corr = muslo_maximo - (π * muslo_medial_pliegue / 10)
        pantorrilla_corr = pantorrilla_maxima - (π * pantorrilla_pliegue / 10)
    MM = (altura * 0.00744 * brazo_corr²) +
         (altura * 0.00088 * muslo_corr²) +
         (altura * 0.00441 * pantorrilla_corr²) +
         (2.4 * sexo_val) - (0.048 * edad) + raza + 7.8
    sexo: masculino=1, femenino=0 | raza: caucásico=0 (default)
    """
    if any(v is None for v in [talla_cm, sexo, edad]):
        return None

    brazo = a.get("brazo_relajado")
    triceps = a.get("triceps")
    muslo = a.get("muslo_maximo")
    muslo_pl = a.get("muslo_medial_pliegue")
    panto = a.get("pantorrilla_maxima")
    panto_pl = a.get("pantorrilla_pliegue")

    if any(v is None for v in [brazo, triceps, muslo, muslo_pl, panto, panto_pl]):
        return None

    altura_m = talla_cm / 100
    brazo_corr = brazo - (math.pi * triceps / 10)
    muslo_corr = muslo - (math.pi * muslo_pl / 10)
    panto_corr = panto - (math.pi * panto_pl / 10)

    sexo_val = 1 if sexo == "Masculino" else 0
    raza = 0  # caucásico por defecto

    mm = ((altura_m * 0.00744 * brazo_corr ** 2) +
          (altura_m * 0.00088 * muslo_corr ** 2) +
          (altura_m * 0.00441 * panto_corr ** 2) +
          (2.4 * sexo_val) - (0.048 * edad) + raza + 7.8)
    return round(mm, 2)


# --- MASA ÓSEA (Rocha) ---

def calcular_masa_osea(talla_cm, femoral_cm, humeral_cm):
    """Rocha formula: MO = 3.02 * ((altura_m² * diam_humero * diam_femur * 400) ^ 0.712)"""
    if any(v is None for v in [talla_cm, femoral_cm, humeral_cm]):
        return None
    talla_m = talla_cm / 100
    femoral_m = femoral_cm / 100
    humeral_m = humeral_cm / 100
    base = talla_m ** 2 * femoral_m * humeral_m * 400
    if base <= 0:
        return None
    return round(3.02 * (base ** 0.712), 2)


# --- MASA RESIDUAL ---

def calcular_masa_residual(peso, sexo):
    """Fixed values: hombres = peso * 0.241, mujeres = peso * 0.209"""
    if peso is None or not sexo:
        return None
    if sexo == "Masculino":
        return round(peso * 0.241, 2)
    else:
        return round(peso * 0.209, 2)


# --- MASA DE PIEL ---

def calcular_masa_piel(sc):
    """Masa piel = SC * 1.05"""
    if sc is None:
        return None
    return round(sc * 1.05, 2)


# --- COMPOSICIÓN COMPLETA (para informe individual) ---

def calcular_composicion_completa(jugador, antropometria):
    """Calculate full 5-component body composition model.

    Residual mass is derived as the remainder (peso - other 4 components)
    so the model always closes to 100%. The expected residual (fixed fraction)
    is shown as a quality indicator — large deviation signals measurement error.
    """
    peso = antropometria.get("peso")
    talla = antropometria.get("talla_corporal")
    sexo = jugador.get("sexo")
    fecha_nac = jugador.get("fecha_nacimiento")
    fecha_medicion = antropometria.get("fecha")
    edad = calcular_edad(fecha_nac, fecha_medicion)

    suma_8 = calcular_suma_pliegues(antropometria)
    suma_6 = calcular_suma_6_pliegues(antropometria)
    sc = calcular_superficie_corporal(peso, talla)
    masa_adiposa, pct_grasa = calcular_masa_adiposa(antropometria, peso, talla)
    masa_muscular = calcular_masa_muscular(antropometria, talla, sexo, edad)
    masa_osea = calcular_masa_osea(talla, antropometria.get("femoral"), antropometria.get("humeral"))
    masa_piel = calcular_masa_piel(sc)

    # Residual = remainder so model always closes to 100%
    masa_residual = None
    residual_esperado = calcular_masa_residual(peso, sexo)
    desviacion_residual = None

    if all(v is not None for v in [peso, masa_adiposa, masa_muscular, masa_osea, masa_piel]):
        masa_residual = round(peso - masa_adiposa - masa_muscular - masa_osea - masa_piel, 2)
        if residual_esperado is not None:
            desviacion_residual = round(masa_residual - residual_esperado, 2)

    return {
        "edad": edad,
        "suma_6_pliegues": suma_6,
        "suma_8_pliegues": suma_8,
        "superficie_corporal": sc,
        "masa_adiposa": masa_adiposa,
        "pct_grasa": pct_grasa,
        "masa_muscular": masa_muscular,
        "pct_muscular": round((masa_muscular / peso) * 100, 2) if masa_muscular and peso else None,
        "masa_osea": masa_osea,
        "pct_osea": round((masa_osea / peso) * 100, 2) if masa_osea and peso else None,
        "masa_residual": masa_residual,
        "pct_residual": round((masa_residual / peso) * 100, 2) if masa_residual and peso else None,
        "residual_esperado": residual_esperado,
        "desviacion_residual": desviacion_residual,
        "masa_piel": masa_piel,
        "pct_piel": round((masa_piel / peso) * 100, 2) if masa_piel and peso else None,
        "suma_componentes": peso,  # always closes
        "diferencia_peso": 0,
    }


# --- INFORME GENERAL (para la vista de club) ---

def calcular_composicion(jugador, antropometria):
    """Simplified composition for the general report."""
    comp = calcular_composicion_completa(jugador, antropometria)
    return {
        "fecha": antropometria.get("fecha"),
        "talla": antropometria.get("talla_corporal"),
        "peso": antropometria.get("peso"),
        "suma_pliegues": comp["suma_8_pliegues"],
        "pct_grasa": comp["pct_grasa"],
        "kg_grasa": comp["masa_adiposa"],
        "masa_muscular": comp["masa_muscular"],
        "masa_osea": comp["masa_osea"],
        "masa_residual": comp["masa_residual"],
        "masa_piel": comp["masa_piel"],
    }


def obtener_datos_informe(categoria=None, posicion=None, sexo=None):
    """Get report data: each player with their last 3 measurements and computed values."""
    conn = get_connection()
    cursor = conn.cursor()

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
        cursor.execute("""
            SELECT * FROM antropometrias
            WHERE jugador_id = ?
            ORDER BY fecha DESC
            LIMIT 3
        """, (jugador["id"],))
        mediciones = [dict(m) for m in cursor.fetchall()]

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
