import tkinter as tk
from tkinter import ttk, messagebox
from antropometrias import crear_antropometria
from ui.formulario_antropometria import FormularioAntropometria


class CargarAntropometriaWindow:

    def __init__(self, parent, jugador_id):

        self.window = tk.Toplevel(parent)
        self.window.title("Cargar antropometría")
        self.window.geometry("400x350")

        self.formulario = FormularioAntropometria(
            self.window,
            jugador_id
        )

        ttk.Button(
            self.window,
            text="Guardar medición",
            command=self.guardar
        ).pack(pady=20)

    def guardar(self):

        datos = self.formulario.obtener_datos()

        if not datos:
            messagebox.showerror(
                "Error",
                "Revisá los datos: fecha inválida o números incorrectos"
            )
            return

        try:
            crear_antropometria(
                datos["jugador_id"],
                datos["fecha"],
                datos["peso"],
                datos["altura"]
            )

            messagebox.showinfo("Éxito", "Medición guardada")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))