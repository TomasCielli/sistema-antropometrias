from flask import Blueprint, render_template, request
from models.informes import obtener_datos_informe
from models.jugadores import CATEGORIAS, POSICIONES, SEXOS

informes_bp = Blueprint("informes", __name__)


@informes_bp.route("/informes")
def general():
    categoria = request.args.get("categoria", "")
    posicion = request.args.get("posicion", "")
    sexo = request.args.get("sexo", "")

    datos = obtener_datos_informe(
        categoria=categoria or None,
        posicion=posicion or None,
        sexo=sexo or None
    )

    return render_template("informes/general.html",
                           datos=datos,
                           categorias=CATEGORIAS,
                           posiciones=POSICIONES,
                           sexos=SEXOS,
                           filtro_categoria=categoria,
                           filtro_posicion=posicion,
                           filtro_sexo=sexo)
