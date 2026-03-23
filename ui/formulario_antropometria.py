import tkinter as tk
from tkinter import ttk
from datetime import datetime
import re


class FormularioAntropometria:

    def __init__(self, parent, jugador_id):
        self.parent = parent
        self.jugador_id = jugador_id
        self.validar_decimal_cmd = parent.register(self.validar_decimal)
        self.validar_dia_cmd = parent.register(self.validar_dia)
        self.validar_mes_cmd = parent.register(self.validar_mes)
        self.validar_anio_cmd = parent.register(self.validar_anio)

        self.crear_variables()
        self.crear_formulario()
        

    def crear_variables(self):
        self.peso = tk.StringVar()
        self.altura = tk.StringVar()

        self.peso.trace_add("write", self.redondear_peso)
        self.altura.trace_add("write", self.redondear_altura)

        self.dia = tk.StringVar(value="dd")
        self.mes = tk.StringVar(value="mm")
        self.anio = tk.StringVar(value="aaaa")

    def crear_formulario(self):

        frame = ttk.Frame(self.parent, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Peso (kg)").pack(anchor="w")
        self.peso_entry = ttk.Entry(
            frame,
            textvariable=self.peso,
            validate="key",
            validatecommand=(self.validar_decimal_cmd, "%P")
        )
        self.peso_entry.pack(fill="x")

        ttk.Label(frame, text="Altura (cm)").pack(anchor="w", pady=(10,0))
        ttk.Entry(frame, textvariable=self.altura).pack(fill="x")

        ttk.Label(frame, text="Fecha medición").pack(anchor="w", pady=(10,0))

        fecha_frame = ttk.Frame(frame)
        fecha_frame.pack()

        self.dia_entry = ttk.Entry(
            fecha_frame,
            textvariable=self.dia,
            width=5,
            validate="key",
            validatecommand=(self.validar_dia_cmd, "%P")
        )
        self.dia_entry.pack(side="left")
        self.dia_entry.bind("<KeyRelease>", self.saltar_mes)
        self.dia_entry.bind("<FocusIn>", self.limpiar_placeholder_dia)
        self.dia_entry.bind("<FocusOut>", self.restaurar_placeholder_dia)

        ttk.Label(fecha_frame, text="/").pack(side="left")

        self.mes_entry = ttk.Entry(
            fecha_frame,
            textvariable=self.mes,
            width=5,
            validate="key",
            validatecommand=(self.validar_mes_cmd, "%P")
        )
        self.mes_entry.pack(side="left")
        self.mes_entry.bind("<KeyRelease>", self.saltar_anio)
        self.mes_entry.bind("<FocusIn>", self.limpiar_placeholder_mes)
        self.mes_entry.bind("<FocusOut>", self.restaurar_placeholder_mes)

        ttk.Label(fecha_frame, text="/").pack(side="left")

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

    def obtener_datos(self):

        fecha = f"{self.anio.get()}-{self.mes.get()}-{self.dia.get()}"

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except:
            return None

        peso = self.procesar_decimal(self.peso.get())
        altura = self.procesar_decimal(self.altura.get())

        if peso is None or altura is None:
            return None

        return {
            "jugador_id": self.jugador_id,
            "peso": peso,
            "altura": altura,
            "fecha": fecha
        }
    
    def procesar_decimal(self, valor):

        if not valor:
            return None

        valor = valor.replace(",", ".")

        try:
            numero = float(valor)

            if numero < 0:
                return None

            return round(numero, 2)

        except ValueError:
            return None
    
    def validar_decimal(self, valor):

        if valor == "":
            return True

        valor = valor.replace(",", ".")

        return bool(re.match(r'^\d*\.?\d*$', valor))

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

    def redondear_peso(self, *args):
        self._redondear_var(self.peso)

    def redondear_altura(self, *args):
        self._redondear_var(self.altura)

    def _redondear_var(self, variable):
        valor = variable.get()

        if not valor:
            return

        valor = valor.replace(",", ".")

        try:
            numero = float(valor)

            if numero < 0:
                variable.set("")
                return

            redondeado = f"{round(numero, 2):.2f}"
            variable.set(redondeado)

        except:
            pass

    def validar_dia(self, valor):
        if valor in ("", "d", "dd"):
            return True

        if not valor.isdigit():
            return False

        if len(valor) > 2:
            return False

        return 1 <= int(valor) <= 31


    def validar_mes(self, valor):
        if valor in ("", "m", "mm"):
            return True

        if not valor.isdigit():
            return False

        if len(valor) > 2:
            return False

        return 1 <= int(valor) <= 12


    def validar_anio(self, valor):
        if valor in ("", "a", "aa", "aaa", "aaaa"):
            return True

        if not valor.isdigit():
            return False

        if len(valor) > 4:
            return False

        return 1900 <= int(valor) <= 2100
    
    def saltar_mes(self, event):
        valor = self.dia.get()
        if valor.isdigit() and len(valor) == 2:
            self.mes_entry.focus()


    def saltar_anio(self, event):
        valor = self.mes.get()
        if valor.isdigit() and len(valor) == 2:
            self.anio_entry.focus()