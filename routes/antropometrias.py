import io
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from models.antropometrias import (
    CAMPOS_NUMERICOS, LABELS, SECCIONES,
    crear_antropometria, modificar_antropometria, eliminar_antropometria,
    obtener_antropometria_por_id, obtener_antropometrias_de_jugador
)
from models.jugadores import CATEGORIAS, POSICIONES, obtener_jugador_por_id
from models.informes import (
    calcular_composicion_completa, calcular_edad,
    obtener_historico_composicion,
)
from models.graficos import (
    grafico_composicion_pie, grafico_pliegues_bar, grafico_perimetros_bar,
    grafico_evolucion, grafico_comparacion_componentes,
)
from models.referencias import obtener_referencia_por_id, obtener_referencias

antropometrias_bp = Blueprint("antropometrias", __name__)


@antropometrias_bp.route("/jugadores/<int:id>/antropometrias")
def historial(id):
    jugador = obtener_jugador_por_id(id)
    if not jugador:
        abort(404)
    antropometrias = obtener_antropometrias_de_jugador(id)
    return render_template("antropometrias/historial.html",
                           jugador=jugador,
                           antropometrias=antropometrias)


@antropometrias_bp.route("/jugadores/<int:id>/antropometrias/nueva", methods=["GET"])
def nueva(id):
    jugador = obtener_jugador_por_id(id)
    if not jugador:
        abort(404)
    antropometria = {
        "fecha": date.today().isoformat(),
        "posicion": jugador.get("posicion_actual", ""),
        "categoria": jugador.get("categoria_actual", ""),
    }
    return render_template("antropometrias/nueva.html",
                           jugador=jugador,
                           antropometria=antropometria,
                           secciones=SECCIONES,
                           labels=LABELS,
                           categorias=CATEGORIAS,
                           posiciones=POSICIONES)


@antropometrias_bp.route("/jugadores/<int:id>/antropometrias/nueva", methods=["POST"])
def crear(id):
    jugador = obtener_jugador_por_id(id)
    if not jugador:
        abort(404)

    fecha = request.form.get("fecha", "").strip()
    posicion = request.form.get("posicion") or None
    categoria = request.form.get("categoria") or None

    errores = []
    if not fecha:
        errores.append("La fecha es obligatoria")

    # Parse numeric fields
    datos = {"jugador_id": id, "fecha": fecha, "posicion": posicion, "categoria": categoria}
    for campo in CAMPOS_NUMERICOS:
        valor_str = request.form.get(campo, "").strip()
        if valor_str:
            try:
                valor = float(valor_str)
                if valor < 0:
                    label = LABELS[campo][0]
                    errores.append(f"{label} no puede ser negativo")
                else:
                    datos[campo] = valor
            except ValueError:
                label = LABELS[campo][0]
                errores.append(f"{label} debe ser un número")
        else:
            datos[campo] = None

    if errores:
        for e in errores:
            flash(e, "danger")
        # Re-fill form with submitted values
        antropometria = {k: request.form.get(k, "") for k in ["fecha", "posicion", "categoria"] + CAMPOS_NUMERICOS}
        return render_template("antropometrias/nueva.html",
                               jugador=jugador,
                               antropometria=antropometria,
                               secciones=SECCIONES,
                               labels=LABELS,
                               categorias=CATEGORIAS,
                               posiciones=POSICIONES)

    try:
        crear_antropometria(datos)
        flash("Medición guardada correctamente", "success")
        return redirect(url_for("antropometrias.historial", id=id))
    except ValueError as e:
        flash(str(e), "danger")
        antropometria = {k: request.form.get(k, "") for k in ["fecha", "posicion", "categoria"] + CAMPOS_NUMERICOS}
        return render_template("antropometrias/nueva.html",
                               jugador=jugador,
                               antropometria=antropometria,
                               secciones=SECCIONES,
                               labels=LABELS,
                               categorias=CATEGORIAS,
                               posiciones=POSICIONES)


@antropometrias_bp.route("/antropometrias/<int:id>/ver")
def ver(id):
    antropometria = obtener_antropometria_por_id(id)
    if not antropometria:
        abort(404)
    jugador = obtener_jugador_por_id(antropometria["jugador_id"])
    return render_template("antropometrias/ver.html",
                           jugador=jugador,
                           antropometria=antropometria,
                           secciones=SECCIONES,
                           labels=LABELS)


def _preparar_informe(id):
    """Shared logic for informe HTML and PDF."""
    antropometria = obtener_antropometria_por_id(id)
    if not antropometria:
        return None, None, None, None, None, None
    jugador = obtener_jugador_por_id(antropometria["jugador_id"])
    edad = calcular_edad(jugador.get("fecha_nacimiento"), antropometria.get("fecha"))
    comp = calcular_composicion_completa(jugador, antropometria)
    historico = obtener_historico_composicion(antropometria["jugador_id"], jugador)
    graficos = {
        "composicion": grafico_composicion_pie(comp),
        "pliegues": grafico_pliegues_bar(antropometria, LABELS),
        "perimetros": grafico_perimetros_bar(antropometria, LABELS),
        "evolucion": grafico_evolucion(historico, antro_id_actual=id),
    }
    return antropometria, jugador, edad, comp, graficos, historico


@antropometrias_bp.route("/antropometrias/<int:id>/informe")
def informe(id):
    antropometria, jugador, edad, comp, graficos, historico = _preparar_informe(id)
    if not antropometria:
        abort(404)
    return render_template("antropometrias/informe.html",
                           jugador=jugador,
                           antropometria=antropometria,
                           edad=edad,
                           comp=comp,
                           graficos=graficos,
                           historico=historico,
                           secciones=SECCIONES,
                           labels=LABELS)


@antropometrias_bp.route("/antropometrias/<int:id>/informe/pdf")
def informe_pdf(id):
    import base64
    import os
    from xhtml2pdf import pisa

    antropometria, jugador, edad, comp, graficos, historico = _preparar_informe(id)
    if not antropometria:
        abort(404)

    # Embed logo as base64
    logo_b64 = None
    logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "img", "logo.png")
    logo_path = os.path.normpath(logo_path)
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("utf-8")

    html = render_template("antropometrias/informe_pdf.html",
                           jugador=jugador,
                           antropometria=antropometria,
                           edad=edad,
                           comp=comp,
                           graficos=graficos,
                           historico=historico,
                           logo_b64=logo_b64,
                           secciones=SECCIONES,
                           labels=LABELS)

    result = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=result)
    result.seek(0)

    filename = f"informe_{jugador['apellido']}_{jugador['nombre']}_{antropometria['fecha']}.pdf"
    return send_file(result, mimetype="application/pdf",
                     as_attachment=True, download_name=filename)


@antropometrias_bp.route("/antropometrias/<int:id>/editar", methods=["GET"])
def editar(id):
    antropometria = obtener_antropometria_por_id(id)
    if not antropometria:
        abort(404)
    jugador = obtener_jugador_por_id(antropometria["jugador_id"])
    return render_template("antropometrias/editar.html",
                           jugador=jugador,
                           antropometria=antropometria,
                           secciones=SECCIONES,
                           labels=LABELS,
                           categorias=CATEGORIAS,
                           posiciones=POSICIONES)


@antropometrias_bp.route("/antropometrias/<int:id>/editar", methods=["POST"])
def actualizar(id):
    antropometria_actual = obtener_antropometria_por_id(id)
    if not antropometria_actual:
        abort(404)

    jugador = obtener_jugador_por_id(antropometria_actual["jugador_id"])

    fecha = request.form.get("fecha", "").strip()
    posicion = request.form.get("posicion") or None
    categoria = request.form.get("categoria") or None

    errores = []
    if not fecha:
        errores.append("La fecha es obligatoria")

    datos = {"fecha": fecha, "posicion": posicion, "categoria": categoria}
    for campo in CAMPOS_NUMERICOS:
        valor_str = request.form.get(campo, "").strip()
        if valor_str:
            try:
                valor = float(valor_str)
                if valor < 0:
                    label = LABELS[campo][0]
                    errores.append(f"{label} no puede ser negativo")
                else:
                    datos[campo] = valor
            except ValueError:
                label = LABELS[campo][0]
                errores.append(f"{label} debe ser un número")
        else:
            datos[campo] = None

    if errores:
        for e in errores:
            flash(e, "danger")
        antropometria = {k: request.form.get(k, "") for k in ["fecha", "posicion", "categoria"] + CAMPOS_NUMERICOS}
        antropometria["id"] = id
        antropometria["jugador_id"] = antropometria_actual["jugador_id"]
        return render_template("antropometrias/editar.html",
                               jugador=jugador,
                               antropometria=antropometria,
                               secciones=SECCIONES,
                               labels=LABELS,
                               categorias=CATEGORIAS,
                               posiciones=POSICIONES)

    try:
        modificar_antropometria(id, datos)
        flash("Medición actualizada correctamente", "success")
        return redirect(url_for("antropometrias.historial", id=antropometria_actual["jugador_id"]))
    except ValueError as e:
        flash(str(e), "danger")
        antropometria = {k: request.form.get(k, "") for k in ["fecha", "posicion", "categoria"] + CAMPOS_NUMERICOS}
        antropometria["id"] = id
        antropometria["jugador_id"] = antropometria_actual["jugador_id"]
        return render_template("antropometrias/editar.html",
                               jugador=jugador,
                               antropometria=antropometria,
                               secciones=SECCIONES,
                               labels=LABELS,
                               categorias=CATEGORIAS,
                               posiciones=POSICIONES)


@antropometrias_bp.route("/antropometrias/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        jugador_id = eliminar_antropometria(id)
        flash("Medición eliminada", "success")
        return redirect(url_for("antropometrias.historial", id=jugador_id))
    except ValueError:
        abort(404)


@antropometrias_bp.route("/jugadores/<int:id>/antropometrias/eliminar_masivo", methods=["POST"])
def eliminar_masivo(id):
    ids = request.form.getlist("seleccionados")
    if not ids:
        flash("No se seleccionó ninguna medición", "warning")
        return redirect(url_for("antropometrias.historial", id=id))
    eliminados = 0
    for aid in ids:
        try:
            eliminar_antropometria(int(aid))
            eliminados += 1
        except (ValueError, TypeError):
            pass
    flash(f"{eliminados} medición(es) eliminada(s)", "success")
    return redirect(url_for("antropometrias.historial", id=id))


@antropometrias_bp.route("/antropometrias/comparar")
def comparar():
    ids_str = request.args.get("ids", "")
    ids = [int(i) for i in ids_str.split(",") if i.strip().isdigit()]
    referencia_id = request.args.get("referencia_id", "").strip()

    referencias = obtener_referencias()
    referencia = None
    if referencia_id.isdigit():
        referencia = obtener_referencia_por_id(int(referencia_id))

    if len(ids) < 2 and not (len(ids) >= 1 and referencia):
        flash("Seleccioná al menos 2 mediciones o 1 medición + una referencia", "warning")
        return redirect(url_for("jugadores.listar"))

    items = []

    if referencia:
        items.append({
            "antropometria": {
                "id": None,
                "fecha": None,
                "peso": referencia.get("peso"),
                "posicion": referencia.get("posicion"),
                "categoria": referencia.get("categoria"),
            },
            "jugador": {
                "apellido": "Referencia",
                "nombre": referencia.get("nombre"),
                "sexo": referencia.get("sexo") or "—",
            },
            "edad": None,
            "comp": {
                "pct_grasa": referencia.get("pct_grasa"),
                "masa_adiposa": referencia.get("masa_adiposa"),
                "pct_muscular": referencia.get("pct_muscular"),
                "masa_muscular": referencia.get("masa_muscular"),
                "masa_osea": referencia.get("masa_osea"),
                "masa_residual": referencia.get("masa_residual"),
                "masa_piel": referencia.get("masa_piel"),
                "suma_6_pliegues": None,
                "suma_8_pliegues": None,
                "superficie_corporal": None,
            },
            "label": f"Referencia: {referencia['nombre']}",
            "es_referencia": True,
        })

    for aid in ids:
        a = obtener_antropometria_por_id(aid)
        if not a:
            continue
        jugador = obtener_jugador_por_id(a["jugador_id"])
        edad = calcular_edad(jugador.get("fecha_nacimiento"), a.get("fecha"))
        comp = calcular_composicion_completa(jugador, a)
        items.append({
            "antropometria": a,
            "jugador": jugador,
            "edad": edad,
            "comp": comp,
            "label": f"{a['fecha']} ({jugador['apellido']})",
            "es_referencia": False,
        })

    if len(items) < 2:
        flash("No se pudieron cargar las mediciones seleccionadas", "danger")
        return redirect(url_for("jugadores.listar"))

    # Compute deltas relative to the first item
    primera_comp = items[0]["comp"]
    primera_antro = items[0]["antropometria"]
    campos_delta = [
        "pct_grasa", "pct_muscular", "masa_adiposa", "masa_muscular",
        "masa_osea", "masa_residual", "masa_piel",
    ]
    for item in items[1:]:
        deltas = {}
        for key in campos_delta:
            v1 = primera_comp.get(key)
            v2 = item["comp"].get(key)
            deltas[key] = round(v2 - v1, 2) if v1 is not None and v2 is not None else None
        peso_v1 = primera_antro.get("peso")
        peso_v2 = item["antropometria"].get("peso")
        deltas["peso"] = round(peso_v2 - peso_v1, 2) if peso_v1 is not None and peso_v2 is not None else None
        item["deltas"] = deltas
    items[0]["deltas"] = None

    grafico = grafico_comparacion_componentes(items)

    return render_template("antropometrias/comparar.html",
                           items=items,
                           grafico=grafico,
                           referencias=referencias,
                           referencia_id_actual=referencia.get("id") if referencia else None,
                           ids_str=ids_str,
                           secciones=SECCIONES,
                           labels=LABELS)
