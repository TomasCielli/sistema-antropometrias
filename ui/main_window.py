import tkinter as tk
from tkinter import ttk
from ui.jugadores_view import JugadoresView


class MainWindow:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Antropometrías")
        self.root.geometry("1000x600")

        self.crear_layout()

    def crear_layout(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        # pestaña jugadores
        jugadores_tab = JugadoresView(notebook)
        notebook.add(jugadores_tab.frame, text="Jugadores")

    def run(self):
        self.root.mainloop()