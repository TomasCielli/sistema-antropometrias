import tkinter as tk
from tkinter import ttk, messagebox
from jugadores import modificar_jugador
from ui.formulario_jugador import FormularioJugador


class EditarJugadorWindow:

    def __init__(self, parent, jugador, on_success=None):
        self.jugador = jugador
        self.on_success = on_success

        self.window = tk.Toplevel(parent)
        self.window.title("Editar jugador")
        self.window.geometry("420x460")

        self.formulario = FormularioJugador(
            self.window,
            datos_iniciales=jugador
        )

        ttk.Button(
            self.window,
            text="Guardar cambios",
            command=self.guardar
        ).pack(pady=20)

    def guardar(self):

        try:
            datos = self.formulario.obtener_datos()

            if not datos:
                messagebox.showerror("Error", "Fecha inválida")
                return

            modificar_jugador(
                self.jugador["id"],
                {
                    "nombre": datos["nombre"],
                    "apellido": datos["apellido"],
                    "dni": datos["dni"],
                    "posicion_actual": datos["posicion"],
                    "categoria_actual": datos["categoria"],
                    "fecha_nacimiento": datos["fecha"]
                }
            )

            messagebox.showinfo("Éxito", "Jugador actualizado")

            if self.on_success:
                self.on_success()

            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))