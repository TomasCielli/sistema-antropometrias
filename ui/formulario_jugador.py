import tkinter as tk
from tkinter import ttk
from datetime import datetime


class FormularioJugador:
    """
    Formulario reutilizable para crear o editar jugadores.
    """

    def __init__(self, parent, datos_iniciales=None):
        """
        parent: frame donde se dibuja el formulario
        datos_iniciales: diccionario con datos del jugador (solo para editar)
        """

        self.parent = parent
        self.datos = datos_iniciales or {}

        # Registrar validaciones
        self.validar_dni_cmd = parent.register(self.validar_dni)
        self.validar_dia_cmd = parent.register(self.validar_dia)
        self.validar_mes_cmd = parent.register(self.validar_mes)
        self.validar_anio_cmd = parent.register(self.validar_anio)

        self.crear_variables()
        self.crear_formulario()

    # ================= VARIABLES =================

    def crear_variables(self):
        """
        Variables del formulario.
        Si estamos editando, cargamos datos existentes.
        """

        self.nombre = tk.StringVar(value=self.datos.get("nombre", ""))
        self.apellido = tk.StringVar(value=self.datos.get("apellido", ""))
        self.dni = tk.StringVar(value=self.datos.get("dni", ""))
        self.posicion = tk.StringVar(value=self.datos.get("posicion_actual", "Pilar"))
        self.categoria = tk.StringVar(value=self.datos.get("categoria_actual", "M15"))

        fecha = self.datos.get("fecha_nacimiento", None)

        if fecha:
            anio, mes, dia = fecha.split("-")
        else:
            dia, mes, anio = "dd", "mm", "aaaa"

        self.dia = tk.StringVar(value=dia)
        self.mes = tk.StringVar(value=mes)
        self.anio = tk.StringVar(value=anio)

    # ================= FORMULARIO =================

    def crear_formulario(self):

        frame = ttk.Frame(self.parent, padding=20)
        frame.pack(fill="both", expand=True)

        self.crear_input(frame, "Nombre", self.nombre)
        self.crear_input(frame, "Apellido", self.apellido)

        ttk.Label(frame, text="DNI").pack(anchor="w", pady=(10, 0))

        self.dni_entry = ttk.Entry(
            frame,
            textvariable=self.dni,
            validate="key",
            validatecommand=(self.validar_dni_cmd, "%P")
        )
        self.dni_entry.pack(fill="x")

        # POSICION
        ttk.Label(frame, text="Posición").pack(anchor="w", pady=(10, 0))

        self.posicion_combo = ttk.Combobox(
            frame,
            textvariable=self.posicion,
            state="readonly"
        )

        self.posicion_combo["values"] = [
            "Pilar", "Hooker", "Segunda línea", "Tercera línea",
            "Medio scrum", "Apertura", "Wing", "Centro", "Fullback"
        ]

        self.posicion_combo.pack(fill="x")

        # CATEGORIA
        ttk.Label(frame, text="Categoría").pack(anchor="w", pady=(10, 0))

        self.categoria_combo = ttk.Combobox(
            frame,
            textvariable=self.categoria,
            state="readonly"
        )

        self.categoria_combo["values"] = [
            "M15", "M16", "M17", "M18", "M19",
            "Preintermedia", "Intermedia", "Primera"
        ]

        self.categoria_combo.pack(fill="x")

        # FECHA
        ttk.Label(frame, text="Fecha nacimiento").pack(anchor="w", pady=(10, 0))

        fecha_frame = ttk.Frame(frame)
        fecha_frame.pack(fill="x")

        self.dia_entry = ttk.Entry(
            fecha_frame,
            textvariable=self.dia,
            width=5,
            validate="key",
            validatecommand=(self.validar_dia_cmd, "%P")
        )
        self.dia_entry.pack(side="left")

        # eventos de placeholder
        self.dia_entry.bind("<FocusIn>", self.limpiar_placeholder_dia)
        self.dia_entry.bind("<FocusOut>", self.restaurar_placeholder_dia)

        # UX automática
        self.dia_entry.bind("<KeyRelease>", self.pasar_a_mes)

        ttk.Label(fecha_frame, text="/").pack(side="left", padx=5)

        self.mes_entry = ttk.Entry(
            fecha_frame,
            textvariable=self.mes,
            width=5,
            validate="key",
            validatecommand=(self.validar_mes_cmd, "%P")
        )
        self.mes_entry.pack(side="left")

        self.mes_entry.bind("<FocusIn>", self.limpiar_placeholder_mes)
        self.mes_entry.bind("<FocusOut>", self.restaurar_placeholder_mes)

        self.mes_entry.bind("<KeyRelease>", self.pasar_a_anio)

        ttk.Label(fecha_frame, text="/").pack(side="left", padx=5)

        self.anio_entry = ttk.Entry(
            fecha_frame,
            textvariable=self.anio,
            width=8,
            validate="key",
            validatecommand=(self.validar_anio_cmd, "%P")
        )
        self.anio_entry.pack(side="left")

        self.anio_entry.bind("<FocusIn>", self.limpiar_placeholder_anio)
        self.anio_entry.bind("<FocusOut>", self.restaurar_placeholder_anio)

    # ================= HELPERS =================

    def crear_input(self, parent, label, variable):
        ttk.Label(parent, text=label).pack(anchor="w", pady=(10, 0))
        ttk.Entry(parent, textvariable=variable).pack(fill="x")

    # ================= VALIDACIONES =================

    def validar_dni(self, valor):
        return (valor.isdigit() and len(valor) <= 8) or valor == ""

    def validar_dia(self, valor):
        return valor.isdigit() and len(valor) <= 2 or valor in ("", "dd")

    def validar_mes(self, valor):
        return valor.isdigit() and len(valor) <= 2 or valor in ("", "mm")

    def validar_anio(self, valor):
        return valor.isdigit() and len(valor) <= 4 or valor in ("", "aaaa")

    # ================= UX =================

    def pasar_a_mes(self, event):
        if len(self.dia.get()) >= 2:
            self.mes_entry.focus()

    def pasar_a_anio(self, event):
        if len(self.mes.get()) >= 2:
            self.anio_entry.focus()

    # ================= DATOS =================

    def obtener_datos(self):
        """
        Devuelve los datos del formulario.
        """

        fecha = f"{self.anio.get()}-{self.mes.get().zfill(2)}-{self.dia.get().zfill(2)}"

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            return None

        return {
            "nombre": self.nombre.get().strip(),
            "apellido": self.apellido.get().strip(),
            "dni": self.dni.get().strip(),
            "posicion": self.posicion.get(),
            "categoria": self.categoria.get(),
            "fecha": fecha
        }
    
    # ================= PLACEHOLDERS =================

    def limpiar_placeholder_dia(self, event):
        if self.dia.get() == "dd":
            self.dia.set("")

    def restaurar_placeholder_dia(self, event):
        if self.dia.get() == "":
            self.dia.set("dd")


    def limpiar_placeholder_mes(self, event):
        if self.mes.get() == "mm":
            self.mes.set("")

    def restaurar_placeholder_mes(self, event):
        if self.mes.get() == "":
            self.mes.set("mm")


    def limpiar_placeholder_anio(self, event):
        if self.anio.get() == "aaaa":
            self.anio.set("")

    def restaurar_placeholder_anio(self, event):
        if self.anio.get() == "":
            self.anio.set("aaaa")