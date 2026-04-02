from flask import Flask, redirect, url_for
from config import SECRET_KEY, DEBUG, HOST, PORT
from database import crear_base

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    crear_base()

    from routes.jugadores import jugadores_bp
    from routes.antropometrias import antropometrias_bp
    from routes.informes import informes_bp
    from routes.datos import datos_bp

    app.register_blueprint(jugadores_bp)
    app.register_blueprint(antropometrias_bp)
    app.register_blueprint(informes_bp)
    app.register_blueprint(datos_bp)

    @app.route("/")
    def index():
        return redirect(url_for("jugadores.listar"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)
