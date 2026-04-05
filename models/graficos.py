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
    "Osea":     "#f39c12",
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
        ("Osea",     comp.get("masa_osea")),
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
    ax.set_title("Composicion Corporal", fontsize=11, fontweight="bold", pad=8)
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
    ax.set_title("Pliegues Cutaneos", fontsize=11, fontweight="bold", pad=8)
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
    ax.set_title("Perimetros", fontsize=11, fontweight="bold", pad=8)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    return _to_base64(fig)


def grafico_evolucion(historico, antro_id_actual=None):
    """Two-panel line chart: peso over time + % grasa vs % muscular over time.

    historico: list of dicts with keys id, fecha, peso, pct_grasa, pct_muscular
               sorted by date ascending.
    antro_id_actual: highlights the current measurement in the chart.
    Returns None if fewer than 2 data points.
    """
    if len(historico) < 2:
        return None

    fechas = [h["fecha"] for h in historico]
    pesos = [h.get("peso") for h in historico]
    pct_grasa = [h.get("pct_grasa") for h in historico]
    pct_muscular = [h.get("pct_muscular") for h in historico]

    idx_actual = next(
        (i for i, h in enumerate(historico) if h.get("id") == antro_id_actual), None
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), facecolor="white")

    def _plot_serie(ax, valores, color, label, unidad):
        validos = [(f, v) for f, v in zip(fechas, valores) if v is not None]
        if not validos:
            ax.text(0.5, 0.5, "Sin datos suficientes", ha="center", va="center",
                    transform=ax.transAxes, color="#aaa", fontsize=9)
            return
        fx, vy = zip(*validos)
        ax.plot(list(fx), list(vy), marker="o", color=color, linewidth=2, label=label,
                markersize=5, zorder=2)
        if idx_actual is not None and idx_actual < len(fechas):
            xi = fechas[idx_actual]
            yi_list = [v for f, v in zip(fechas, valores) if f == xi and v is not None]
            if yi_list:
                ax.plot(xi, yi_list[0], marker="o", color=color, markersize=11,
                        markeredgewidth=2.5, markeredgecolor="white",
                        markerfacecolor=color, zorder=3)
        ax.set_ylabel(unidad, fontsize=9)
        ax.tick_params(labelsize=7, axis="x", rotation=30)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    _plot_serie(axes[0], pesos, "#2c3e50", "Peso", "kg")
    axes[0].set_title("Evolucion del Peso", fontsize=10, fontweight="bold", pad=6)

    _plot_serie(axes[1], pct_grasa, "#e74c3c", "% Grasa", "%")
    _plot_serie(axes[1], pct_muscular, "#2ecc71", "% Muscular", "%")
    axes[1].set_title("Composicion (%)", fontsize=10, fontweight="bold", pad=6)
    axes[1].legend(fontsize=8, frameon=False, loc="best")

    fig.tight_layout(pad=1.5)
    return _to_base64(fig)


def grafico_grupo_comparativa(stats_grupo):
    """Horizontal grouped bar chart comparing % grasa and % muscular across players.

    stats_grupo: list of dicts with keys nombre, pct_grasa, pct_muscular.
    Returns None if no valid data.
    """
    items = [s for s in stats_grupo
             if s.get("pct_grasa") is not None or s.get("pct_muscular") is not None]
    if not items:
        return None

    nombres = [s["nombre"] for s in items]
    pct_grasa = [s.get("pct_grasa") or 0 for s in items]
    pct_muscular = [s.get("pct_muscular") or 0 for s in items]

    y = list(range(len(nombres)))
    alto = max(3.5, len(nombres) * 0.55)
    fig, axes = plt.subplots(1, 2, figsize=(11, alto), facecolor="white")

    for ax, valores, color, titulo, unidad in [
        (axes[0], pct_grasa,    "#e74c3c", "% Grasa",    "%"),
        (axes[1], pct_muscular, "#2ecc71", "% Muscular", "%"),
    ]:
        bars = ax.barh(y, valores, color=color, edgecolor="white", height=0.6)
        ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=8)
        ax.set_yticks(y)
        ax.set_yticklabels(nombres, fontsize=8)
        ax.set_xlabel(unidad, fontsize=9)
        ax.set_title(titulo, fontsize=10, fontweight="bold", pad=6)
        ax.invert_yaxis()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=8)

    fig.tight_layout(pad=1.5)
    return _to_base64(fig)


def grafico_comparacion_componentes(items):
    """Grouped bar chart comparing 5-component masses across 2+ measurements.

    items: list of dicts with keys 'label' (str) and 'comp' (composition dict).
    Returns None if no valid data.
    """
    if not items:
        return None

    componentes = ["masa_adiposa", "masa_muscular", "masa_osea", "masa_residual", "masa_piel"]
    nombres_comp = ["Adiposa", "Muscular", "Osea", "Residual", "Piel"]
    colores_items = ["#3498db", "#e67e22", "#9b59b6", "#1abc9c", "#e74c3c",
                     "#f39c12", "#2ecc71", "#34495e"]

    n = len(componentes)
    m = len(items)
    ancho = 0.7 / m
    x = list(range(n))

    fig, ax = plt.subplots(figsize=(9, 4), facecolor="white")

    for i, item in enumerate(items):
        comp = item.get("comp", {})
        valores = [comp.get(c) or 0 for c in componentes]
        offsets = [xi + (i - m / 2 + 0.5) * ancho for xi in x]
        bars = ax.bar(offsets, valores, width=ancho * 0.9,
                      color=colores_items[i % len(colores_items)],
                      label=item.get("label", f"Medicion {i+1}"),
                      edgecolor="white")
        ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels(nombres_comp, fontsize=9)
    ax.set_ylabel("kg", fontsize=9)
    ax.set_title("Comparacion de Componentes Corporales", fontsize=11, fontweight="bold", pad=8)
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    return _to_base64(fig)
