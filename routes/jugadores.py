from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models.jugadores import (
    CATEGORIAS, POSICIONES, SEXOS, OBJETIVOS,
    crear_jugador, modificar_jugador, eliminar_jugador,
    obtener_jugador_por_id, obtener_jugadores_con_ultima_antropometria
)
import sqlite3

jugadores_bp = Blueprint("jugadores", __name__)


@jugadores_bp.route("/jugadores")
def listar():
    jugadores = obtener_jugadores_con_ultima_antropometria()
    return render_template("jugadores/index.html",
                           jugadores=jugadores,
                           categorias=CATEGORIAS,
                           sexos=SEXOS)


@jugadores_bp.route("/jugadores/nuevo", methods=["GET"])
def nuevo():
    return render_template("jugadores/nuevo.html",
                           categorias=CATEGORIAS,
                           posiciones=POSICIONES,
                           sexos=SEXOS,
                           objetivos=OBJETIVOS,
                           jugador={})


@jugadores_bp.route("/jugadores/nuevo", methods=["POST"])
def crear():
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    dni = request.form.get("dni", "").strip()
    sexo = request.form.get("sexo", "").strip()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()
    posicion = request.form.get("posicion_actual") or None
    categoria = request.form.get("categoria_actual") or None
    objetivo = request.form.get("objetivo") or None
    telefono = request.form.get("telefono", "").strip() or None
    observaciones = request.form.get("observaciones", "").strip() or None

    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio")
    if not apellido:
        errores.append("El apellido es obligatorio")
    if not dni:
        errores.append("El DNI es obligatorio")
    if not sexo:
        errores.append("El sexo es obligatorio")
    if not fecha_nacimiento:
        errores.append("La fecha de nacimiento es obligatoria")

    if errores:
        for e in errores:
            flash(e, "danger")
        jugador = {
            "nombre": nombre, "apellido": apellido, "dni": dni,
            "sexo": sexo, "fecha_nacimiento": fecha_nacimiento,
            "posicion_actual": posicion, "categoria_actual": categoria,
            "objetivo": objetivo, "telefono": telefono, "observaciones": observaciones
        }
        return render_template("jugadores/nuevo.html",
                               categorias=CATEGORIAS,
                               posiciones=POSICIONES,
                               sexos=SEXOS,
                               objetivos=OBJETIVOS,
                               jugador=jugador)

    try:
        crear_jugador(nombre, apellido, dni, sexo, fecha_nacimiento, posicion, categoria, objetivo, telefono, observaciones)
        flash("Jugador creado correctamente", "success")
        return redirect(url_for("jugadores.listar"))
    except sqlite3.IntegrityError:
        flash("Ya existe un jugador con ese DNI", "danger")
        jugador = {
            "nombre": nombre, "apellido": apellido, "dni": dni,
            "sexo": sexo, "fecha_nacimiento": fecha_nacimiento,
            "posicion_actual": posicion, "categoria_actual": categoria,
            "objetivo": objetivo, "telefono": telefono, "observaciones": observaciones
        }
        return render_template("jugadores/nuevo.html",
                               categorias=CATEGORIAS,
                               posiciones=POSICIONES,
                               sexos=SEXOS,
                               objetivos=OBJETIVOS,
                               jugador=jugador)


@jugadores_bp.route("/jugadores/<int:id>/editar", methods=["GET"])
def editar(id):
    jugador = obtener_jugador_por_id(id)
    if not jugador:
        abort(404)
    return render_template("jugadores/editar.html",
                           categorias=CATEGORIAS,
                           posiciones=POSICIONES,
                           sexos=SEXOS,
                           objetivos=OBJETIVOS,
                           jugador=jugador)


@jugadores_bp.route("/jugadores/<int:id>/editar", methods=["POST"])
def actualizar(id):
    jugador_actual = obtener_jugador_por_id(id)
    if not jugador_actual:
        abort(404)

    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    dni = request.form.get("dni", "").strip()
    sexo = request.form.get("sexo", "").strip()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()
    posicion = request.form.get("posicion_actual") or None
    categoria = request.form.get("categoria_actual") or None
    objetivo = request.form.get("objetivo") or None
    telefono = request.form.get("telefono", "").strip() or None
    observaciones = request.form.get("observaciones", "").strip() or None

    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio")
    if not apellido:
        errores.append("El apellido es obligatorio")
    if not dni:
        errores.append("El DNI es obligatorio")
    if not sexo:
        errores.append("El sexo es obligatorio")
    if not fecha_nacimiento:
        errores.append("La fecha de nacimiento es obligatoria")

    if errores:
        for e in errores:
            flash(e, "danger")
        jugador = {
            "id": id, "nombre": nombre, "apellido": apellido, "dni": dni,
            "sexo": sexo, "fecha_nacimiento": fecha_nacimiento,
            "posicion_actual": posicion, "categoria_actual": categoria,
            "objetivo": objetivo, "telefono": telefono, "observaciones": observaciones
        }
        return render_template("jugadores/editar.html",
                               categorias=CATEGORIAS,
                               posiciones=POSICIONES,
                               sexos=SEXOS,
                               objetivos=OBJETIVOS,
                               jugador=jugador)

    datos = {
        "nombre": nombre, "apellido": apellido, "dni": dni,
        "sexo": sexo, "fecha_nacimiento": fecha_nacimiento,
        "posicion_actual": posicion, "categoria_actual": categoria,
        "objetivo": objetivo, "telefono": telefono, "observaciones": observaciones
    }

    try:
        modificar_jugador(id, datos)
        flash("Jugador actualizado correctamente", "success")
        return redirect(url_for("jugadores.listar"))
    except ValueError as e:
        flash(str(e), "danger")
        jugador = {"id": id, **datos}
        return render_template("jugadores/editar.html",
                               categorias=CATEGORIAS,
                               posiciones=POSICIONES,
                               sexos=SEXOS,
                               objetivos=OBJETIVOS,
                               jugador=jugador)


@jugadores_bp.route("/jugadores/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        eliminar_jugador(id)
        flash("Jugador eliminado", "success")
    except ValueError:
        abort(404)
    return redirect(url_for("jugadores.listar"))


@jugadores_bp.route("/jugadores/eliminar_masivo", methods=["POST"])
def eliminar_masivo():
    ids = request.form.getlist("seleccionados")
    if not ids:
        flash("No se seleccionó ningún jugador", "warning")
        return redirect(url_for("jugadores.listar"))
    eliminados = 0
    for jid in ids:
        try:
            eliminar_jugador(int(jid))
            eliminados += 1
        except (ValueError, TypeError):
            pass
    flash(f"{eliminados} jugador(es) eliminado(s)", "success")
    return redirect(url_for("jugadores.listar"))
