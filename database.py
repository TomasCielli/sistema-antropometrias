import sqlite3
from config import DB_NAME

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def crear_base():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jugadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT UNIQUE NOT NULL,
        sexo TEXT NOT NULL,
        posicion_actual TEXT,
        categoria_actual TEXT,
        fecha_nacimiento DATE NOT NULL,
        objetivo TEXT,
        telefono TEXT,
        observaciones TEXT,
        creado_en DATE DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS antropometrias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jugador_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        posicion TEXT,
        categoria TEXT,
        peso REAL,
        talla_corporal REAL,
        talla_sentado REAL,
        biacromial REAL,
        torax_transverso REAL,
        torax_anteroposterior REAL,
        bi_iliocrestideo REAL,
        humeral REAL,
        femoral REAL,
        cabeza REAL,
        brazo_relajado REAL,
        brazo_flexionado REAL,
        antebrazo REAL,
        torax_mesoesternal REAL,
        cintura REAL,
        cadera REAL,
        muslo_maximo REAL,
        muslo_medial REAL,
        pantorrilla_maxima REAL,
        triceps REAL,
        subescapular REAL,
        supraespinal REAL,
        abdominal REAL,
        muslo_medial_pliegue REAL,
        pantorrilla_pliegue REAL,
        biceps REAL,
        cresta_iliaca REAL,
        FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE
    )
    """)

    # Add new columns if they don't exist (migration for existing DBs)
    try:
        cursor.execute("ALTER TABLE jugadores ADD COLUMN telefono TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cursor.execute("ALTER TABLE jugadores ADD COLUMN observaciones TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_dni ON jugadores (dni)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_antropometria_jugador_fecha
    ON antropometrias (jugador_id, fecha)
    """)

    conn.commit()
    conn.close()
