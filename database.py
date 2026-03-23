import sqlite3

# nombre de la base de datos (se crea sola)
DB_NAME = "sistema_antropometrias.db"


def crear_base():
    # conecta o crea la base de datos
    conn = sqlite3.connect(DB_NAME)

    # cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # crear tabla jugadores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jugadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT UNIQUE NOT NULL,
        posicion_actual TEXT,
        categoria_actual TEXT,
        fecha_nacimiento DATE,
        creado_en DATE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # crear tabla antropometrias
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
    );
    """)

    # índice para búsquedas por DNI
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_dni
    ON jugadores (dni);
    """)

    # índice para informes rápidos
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_antropometria_jugador_fecha
    ON antropometrias (jugador_id, fecha);
    """)

    # guardar cambios
    conn.commit()

    # cerrar conexión
    conn.close()