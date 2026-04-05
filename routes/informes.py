import io
import os
import base64

from flask import Blueprint, render_template, request, send_file
from models.informes import obtener_datos_informe, obtener_estadisticas_grupales
from models.jugadores import CATEGORIAS, POSICIONES, SEXOS
from models.graficos import grafico_grupo_comparativa

informes_bp = Blueprint("informes", __name__)


def _datos_informe(categoria, posicion, sexo):
    """Shared data gathering for HTML and PDF views."""
    datos = obtener_datos_informe(
        categoria=categoria or None,
        posicion=posicion or None,
        sexo=sexo or None,
    )
    stats_grupo = obtener_estadisticas_grupales(datos)
    grafico_grupo = grafico_grupo_comparativa(stats_grupo)
    return datos, stats_grupo, grafico_grupo


@informes_bp.route("/informes")
def general():
    categoria = request.args.get("categoria", "")
    posicion = request.args.get("posicion", "")
    sexo = request.args.get("sexo", "")

    datos, stats_grupo, grafico_grupo = _datos_informe(categoria, posicion, sexo)

    return render_template("informes/general.html",
                           datos=datos,
                           stats_grupo=stats_grupo,
                           grafico_grupo=grafico_grupo,
                           categorias=CATEGORIAS,
                           posiciones=POSICIONES,
                           sexos=SEXOS,
                           filtro_categoria=categoria,
                           filtro_posicion=posicion,
                           filtro_sexo=sexo)


@informes_bp.route("/informes/pdf")
def general_pdf():
    from xhtml2pdf import pisa

    categoria = request.args.get("categoria", "")
    posicion = request.args.get("posicion", "")
    sexo = request.args.get("sexo", "")

    datos, stats_grupo, grafico_grupo = _datos_informe(categoria, posicion, sexo)

    # Embed logo
    logo_b64 = None
    logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "img", "logo.png")
    logo_path = os.path.normpath(logo_path)
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Build subtitle from active filters
    filtros_texto = []
    if categoria:
        filtros_texto.append(f"Categoria: {categoria}")
    if posicion:
        filtros_texto.append(f"Posicion: {posicion}")
    if sexo:
        filtros_texto.append(f"Sexo: {sexo}")
    subtitulo = " | ".join(filtros_texto) if filtros_texto else "Sin filtros (todos)"

    html = render_template("informes/general_pdf.html",
                           datos=datos,
                           stats_grupo=stats_grupo,
                           grafico_grupo=grafico_grupo,
                           logo_b64=logo_b64,
                           subtitulo=subtitulo)

    result = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=result)
    result.seek(0)

    filename = "informe_grupal"
    if categoria:
        filename += f"_{categoria}"
    if posicion:
        filename += f"_{posicion}"
    if sexo:
        filename += f"_{sexo}"
    filename += ".pdf"

    return send_file(result, mimetype="application/pdf",
                     as_attachment=True, download_name=filename)
