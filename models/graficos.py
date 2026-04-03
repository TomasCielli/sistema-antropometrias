"""Chart generators — return base64-encoded PNG strings for embedding in HTML/PDF."""
import io
import base64

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for web servers
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


COLORES_COMP = {
    "Adiposa":  "#e74c3c",
    "Muscular": "#2ecc71",
    "Ósea":     "#f39c12",
    "Residual": "#9b59b6",
    "Piel":     "#3498db",
}

COLORES_PLIEGUES = "#5b9bd5"


def _to_base64(fig, dpi=120):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=dpi, transparent=False)
    buf.seek(0)
    result = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return result


def grafico_composicion_pie(comp):
    """Pie chart of 5-component body composition."""
    datos = [
        ("Adiposa",  comp.get("masa_adiposa")),
        ("Muscular", comp.get("masa_muscular")),
        ("Ósea",     comp.get("masa_osea")),
        ("Residual", comp.get("masa_residual")),
        ("Piel",     comp.get("masa_piel")),
    ]
    etiquetas = [d[0] for d in datos if d[1] is not None and d[1] > 0]
    valores   = [d[1] for d in datos if d[1] is not None and d[1] > 0]
    colores   = [COLORES_COMP[e] for e in etiquetas]

    if not valores:
        return None

    fig, ax = plt.subplots(figsize=(5, 4), facecolor="white")
    wedges, texts, autotexts = ax.pie(
        valores,
        labels=None,
        colors=colores,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.78,
        wedgeprops={"linewidth": 0.8, "edgecolor": "white"},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")

    # Custom legend with kg values
    parches = [
        mpatches.Patch(color=c, label=f"{e}: {v:.1f} kg")
        for e, v, c in zip(etiquetas, valores, colores)
    ]
    ax.legend(handles=parches, loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=3, fontsize=8, frameon=False)
    ax.set_title("Composición Corporal", fontsize=11, fontweight="bold", pad=8)
    fig.tight_layout()
    return _to_base64(fig)


def grafico_pliegues_bar(antropometria, labels):
    """Horizontal bar chart of skinfold values."""
    pliegues_campos = [
        "triceps", "subescapular", "supraespinal", "abdominal",
        "muslo_medial_pliegue", "pantorrilla_pliegue", "biceps", "cresta_iliaca",
    ]
    etiquetas = []
    valores = []
    for campo in pliegues_campos:
        val = antropometria.get(campo)
        if val is not None:
            etiquetas.append(labels[campo][0])
            valores.append(val)

    if not valores:
        return None

    fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="white")
    bars = ax.barh(etiquetas, valores, color=COLORES_PLIEGUES, edgecolor="white", height=0.6)
    ax.bar_label(bars, fmt="%.1f mm", padding=3, fontsize=8)
    ax.set_xlabel("mm", fontsize=9)
    ax.set_title("Pliegues Cutáneos", fontsize=11, fontweight="bold", pad=8)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    return _to_base64(fig)


def grafico_perimetros_bar(antropometria, labels):
    """Horizontal bar chart of perimeter measurements."""
    perimetros_campos = [
        "brazo_relajado", "brazo_flexionado", "antebrazo",
        "torax_mesoesternal", "cintura", "cadera",
        "muslo_maximo", "pantorrilla_maxima",
    ]
    etiquetas = []
    valores = []
    for campo in perimetros_campos:
        val = antropometria.get(campo)
        if val is not None:
            etiquetas.append(labels[campo][0])
            valores.append(val)

    if not valores:
        return None

    fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="white")
    bars = ax.barh(etiquetas, valores, color="#27ae60", edgecolor="white", height=0.6)
    ax.bar_label(bars, fmt="%.1f cm", padding=3, fontsize=8)
    ax.set_xlabel("cm", fontsize=9)
    ax.set_title("Perímetros", fontsize=11, fontweight="bold", pad=8)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    return _to_base64(fig)
