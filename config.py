import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "sistema_antropometrias.db"))
DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-albatros-rugby-club-2026")

# Auth credentials (set via environment in production)
AUTH_USERNAME = os.environ.get("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "albatros2026")
