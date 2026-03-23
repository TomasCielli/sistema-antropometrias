from database import crear_base
from ui.main_window import MainWindow

crear_base()

app = MainWindow()
app.run()