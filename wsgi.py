"""WSGI entry point for PythonAnywhere and other WSGI servers."""
from app import create_app

application = create_app()
