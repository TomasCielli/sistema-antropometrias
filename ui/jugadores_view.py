import tkinter as tk
from tkinter import ttk, messagebox
from jugadores import obtener_jugadores_filtrados
from ui.nuevo_jugador_window import NuevoJugadorWindow
from ui.editar_jugador_window import EditarJugadorWindow
from jugadores import obtener_jugador_por_id
from ui.cargar_antropometria_window import CargarAntropometriaWindow

class JugadoresView:

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)

        self.crear_busqueda()
        self.crear_botones()
        self.crear_tabla()
        self.cargar_jugadores()

    def crear_busqueda(self):
        contenedor = ttk.Frame(self.frame)
        contenedor.pack(fill="x", padx=10, pady=10)

        ttk.Label(contenedor, text="Buscar").pack(side="left")

        self.busqueda_var = tk.StringVar()
        entry = ttk.Entry(contenedor, textvariable=self.busqueda_var)
        entry.pack(side="left", padx=10)

        boton = ttk.Button(contenedor, text="Buscar", command=self.buscar)
        boton.pack(side="left")

    # NUEVO
    def crear_botones(self):
        contenedor = ttk.Frame(self.frame)
        contenedor.pack(fill="x", padx=10)

        ttk.Button(
            contenedor,
            text="➕ Nuevo jugador",
            command=self.nuevo_jugador
        ).pack(side="left", padx=5)

        ttk.Button(
            contenedor,
            text="✏️ Editar jugador",
            command=self.editar_jugador
        ).pack(side="left", padx=5)

        ttk.Button(
            contenedor,
            text="📏 Cargar antropometría",
            command=self.cargar_antropometria
        ).pack(side="left", padx=5)

        ttk.Button(
            contenedor,
            text="📊 Ver historial",
            command=self.ver_historial
        ).pack(side="left", padx=5)

    def crear_tabla(self):
        columnas = ("id", "apellido", "nombre", "dni", "posicion", "categoria")

        self.tabla = ttk.Treeview(self.frame, columns=columnas, show="headings")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)

        for col in columnas:
            self.tabla.heading(col, text=col.capitalize())

    def cargar_jugadores(self):
        jugadores = obtener_jugadores_filtrados()

        for j in jugadores:
            self.tabla.insert(
                "",
                "end",
                values=(
                    j["id"],
                    j["apellido"],
                    j["nombre"],
                    j["dni"],
                    j["posicion_actual"],
                    j["categoria_actual"]
                )
            )

    def buscar(self):
        busqueda = self.busqueda_var.get()

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        jugadores = obtener_jugadores_filtrados(busqueda=busqueda)

        for j in jugadores:
            self.tabla.insert(
                "",
                "end",
                values=(
                    j["id"],
                    j["apellido"],
                    j["nombre"],
                    j["dni"],
                    j["posicion_actual"],
                    j["categoria_actual"]
                )
            )

    # -------------------------
    # FUNCIONES DE BOTONES
    # -------------------------

    def obtener_jugador_seleccionado(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccioná un jugador primero")
            return None

        valores = self.tabla.item(seleccion[0])["values"]
        jugador_id = valores[0]

        return jugador_id

    def nuevo_jugador(self):
        NuevoJugadorWindow(
            self.frame,
            on_success=self.recargar_tabla
        )

    def editar_jugador(self):
        jugador_id = self.obtener_jugador_seleccionado()

        if not jugador_id:
            return

        jugador = dict(obtener_jugador_por_id(jugador_id))

        EditarJugadorWindow(
            self.frame,
            jugador,
            on_success=self.recargar_tabla
        )

    def cargar_antropometria(self):
        jugador_id = self.obtener_jugador_seleccionado()

        if not jugador_id:
            return

        CargarAntropometriaWindow(
            self.frame,
            jugador_id
        )

    def ver_historial(self):
        jugador_id = self.obtener_jugador_seleccionado()
        if jugador_id:
            messagebox.showinfo("Historial", f"Ver historial del jugador {jugador_id}")

    def recargar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        self.cargar_jugadores()