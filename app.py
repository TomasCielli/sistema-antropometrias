from flask import Flask, render_template
from config import SECRET_KEY, DEBUG, HOST, PORT
from database import crear_base, get_connection

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
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS total FROM jugadores")
        total_jugadores = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM antropometrias")
        total_mediciones = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM jugadores j
            LEFT JOIN antropometrias a ON a.jugador_id = j.id
            WHERE a.id IS NULL
            """
        )
        jugadores_sin_medicion = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM antropometrias
            WHERE date(fecha) >= date('now', '-30 day')
            """
        )
        mediciones_30_dias = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT
                a.fecha,
                j.id AS jugador_id,
                j.nombre,
                j.apellido,
                a.peso,
                a.talla_corporal
            FROM antropometrias a
            JOIN jugadores j ON j.id = a.jugador_id
            ORDER BY date(a.fecha) DESC, a.id DESC
            LIMIT 8
            """
        )
        ultimas_mediciones = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return render_template(
            "home.html",
            total_jugadores=total_jugadores,
            total_mediciones=total_mediciones,
            jugadores_sin_medicion=jugadores_sin_medicion,
            mediciones_30_dias=mediciones_30_dias,
            ultimas_mediciones=ultimas_mediciones,
        )

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)
