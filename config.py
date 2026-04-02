import os

DB_NAME = "sistema_antropometrias.db"
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-albatros-rugby-club-2026")
