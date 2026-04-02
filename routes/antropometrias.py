from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models.antropometrias import (
    CAMPOS_NUMERICOS, LABELS, SECCIONES,
    crear_antropometria, modificar_antropometria, eliminar_antropometria,
    obtener_antropometria_por_id, obtener_antropometrias_de_jugador
)
from models.jugadores import CATEGORIAS, POSICIONES, obtener_jugador_por_id

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
    # Pre-fill with player's current posicion and categoria
    antropometria = {
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
