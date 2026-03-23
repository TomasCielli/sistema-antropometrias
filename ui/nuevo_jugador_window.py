import tkinter as tk
from tkinter import ttk, messagebox
from jugadores import crear_jugador
from ui.formulario_jugador import FormularioJugador


class NuevoJugadorWindow:

    def __init__(self, parent, on_success=None):
        self.on_success = on_success

        self.window = tk.Toplevel(parent)
        self.window.title("Nuevo jugador")
        self.window.geometry("420x460")

        self.formulario = FormularioJugador(self.window)

        ttk.Button(
            self.window,
            text="Guardar jugador",
            command=self.guardar
        ).pack(pady=20)

    def guardar(self):

        try:
            datos = self.formulario.obtener_datos()

            if not datos:
                messagebox.showerror("Error", "Fecha inválida")
                return

            if "" in [datos["nombre"], datos["apellido"], datos["dni"]]:
                messagebox.showerror("Error", "Tenés que completar todos los campos")
                return

            crear_jugador(
                datos["nombre"],
                datos["apellido"],
                datos["dni"],
                datos["posicion"],
                datos["categoria"],
                datos["fecha"]
            )

            messagebox.showinfo("Éxito", "Jugador creado")

            if self.on_success:
                self.on_success()

            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))