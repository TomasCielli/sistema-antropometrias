from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models.referencias import (
    CAMPOS_NUMERICOS_REFERENCIA,
    crear_referencia,
    modificar_referencia,
    eliminar_referencia,
    obtener_referencia_por_id,
    obtener_referencias,
)
from models.antropometrias import obtener_antropometria_por_id
from models.jugadores import obtener_jugador_por_id
from models.informes import calcular_composicion_completa

referencias_bp = Blueprint("referencias", __name__)


def _parsear_formulario(form):
    nombre = form.get("nombre", "").strip()
    deporte = form.get("deporte", "").strip()
    categoria = form.get("categoria", "").strip() or None
    posicion = form.get("posicion", "").strip() or None
    sexo = form.get("sexo", "").strip() or None
    descripcion = form.get("descripcion", "").strip() or None

    errores = []
    if not nombre:
        errores.append("El nombre de la referencia es obligatorio")
    if not deporte:
        errores.append("El deporte es obligatorio")

    datos = {
        "nombre": nombre,
        "deporte": deporte,
        "categoria": categoria,
        "posicion": posicion,
        "sexo": sexo,
        "descripcion": descripcion,
    }

    for campo in CAMPOS_NUMERICOS_REFERENCIA:
        valor = form.get(campo, "").strip()
        if not valor:
            datos[campo] = None
            continue

        try:
            valor_num = float(valor)
        except ValueError:
            errores.append(f"{campo.replace('_', ' ').title()} debe ser un numero")
            continue

        if valor_num < 0:
            errores.append(f"{campo.replace('_', ' ').title()} no puede ser negativo")
            continue

        datos[campo] = valor_num

    return datos, errores


@referencias_bp.route("/referencias")
def listar():
    referencias = obtener_referencias()
    return render_template("referencias/index.html", referencias=referencias, referencia_prefill={})


@referencias_bp.route("/referencias/nueva-desde-antropometria/<int:id>")
def nueva_desde_antropometria(id):
    antropometria = obtener_antropometria_por_id(id)
    if not antropometria:
        abort(404)

    jugador = obtener_jugador_por_id(antropometria["jugador_id"])
    if not jugador:
        abort(404)

    comp = calcular_composicion_completa(jugador, antropometria)
    referencia_prefill = {
        "nombre": f"{jugador['apellido']}, {jugador['nombre']} ({antropometria['fecha']})",
        "deporte": "Rugby",
        "categoria": antropometria.get("categoria") or jugador.get("categoria_actual") or "",
        "posicion": antropometria.get("posicion") or jugador.get("posicion_actual") or "",
        "sexo": jugador.get("sexo") or "",
        "descripcion": f"Precargada desde medición del {antropometria['fecha']}",
        "peso": antropometria.get("peso"),
        "pct_grasa": comp.get("pct_grasa"),
        "masa_adiposa": comp.get("masa_adiposa"),
        "pct_muscular": comp.get("pct_muscular"),
        "masa_muscular": comp.get("masa_muscular"),
        "masa_osea": comp.get("masa_osea"),
        "masa_residual": comp.get("masa_residual"),
        "masa_piel": comp.get("masa_piel"),
    }

    referencias = obtener_referencias()
    return render_template(
        "referencias/index.html",
        referencias=referencias,
        referencia_prefill=referencia_prefill,
    )


@referencias_bp.route("/referencias/nueva", methods=["POST"])
def crear():
    datos, errores = _parsear_formulario(request.form)

    if errores:
        for error in errores:
            flash(error, "danger")
        return redirect(url_for("referencias.listar"))

    crear_referencia(datos)
    flash("Referencia creada correctamente", "success")
    return redirect(url_for("referencias.listar"))


@referencias_bp.route("/referencias/<int:id>/editar", methods=["GET"])
def editar(id):
    referencia = obtener_referencia_por_id(id)
    if not referencia:
        abort(404)
    return render_template("referencias/editar.html", referencia=referencia)


@referencias_bp.route("/referencias/<int:id>/editar", methods=["POST"])
def actualizar(id):
    referencia_actual = obtener_referencia_por_id(id)
    if not referencia_actual:
        abort(404)

    datos, errores = _parsear_formulario(request.form)
    if errores:
        for error in errores:
            flash(error, "danger")
        referencia = {"id": id, **datos}
        return render_template("referencias/editar.html", referencia=referencia)

    try:
        modificar_referencia(id, datos)
        flash("Referencia actualizada", "success")
        return redirect(url_for("referencias.listar"))
    except ValueError:
        abort(404)


@referencias_bp.route("/referencias/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        eliminar_referencia(id)
        flash("Referencia eliminada", "success")
    except ValueError:
        abort(404)
    return redirect(url_for("referencias.listar"))
