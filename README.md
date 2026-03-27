# Sistema de Antropometrías

Aplicación de escritorio para el registro y seguimiento de mediciones antropométricas de jugadores. Desarrollada en Python con interfaz gráfica en Tkinter y base de datos SQLite.

## Características

- **Gestión de jugadores**: alta, baja y modificación de jugadores con datos personales (nombre, apellido, DNI, posición, categoría, fecha de nacimiento).
- **Registro de antropometrías**: carga de mediciones completas por jugador y fecha, incluyendo medidas corporales y pliegues cutáneos.
- **Búsqueda y filtrado**: búsqueda por nombre, apellido o DNI; filtrado por posición y categoría.
- **Historial por jugador**: visualización de todas las mediciones registradas ordenadas por fecha.
- **Última medición**: vista rápida de la última medición de cada jugador con días transcurridos desde la misma.
- **Validaciones**: evita duplicados de DNI, fechas duplicadas por jugador y valores negativos en mediciones.

## Tecnologías

- **Python 3** — lenguaje principal
- **Tkinter / ttk** — interfaz gráfica de escritorio
- **SQLite3** — base de datos local (no requiere servidor)

> No se requieren dependencias externas. Todo funciona con la biblioteca estándar de Python.

## Estructura del proyecto

```
sistema-antropometrias/
├── app.py                          # Punto de entrada
├── database.py                     # Creación de tablas e índices
├── jugadores.py                    # Lógica de negocio de jugadores
├── antropometrias.py               # Lógica de negocio de antropometrías
├── requirements.txt
└── ui/
    ├── main_window.py              # Ventana principal con tabs
    ├── jugadores_view.py           # Vista principal de jugadores
    ├── nuevo_jugador_window.py     # Formulario alta de jugador
    ├── editar_jugador_window.py    # Formulario edición de jugador
    ├── formulario_jugador.py       # Componente compartido de formulario de jugador
    ├── cargar_antropometria_window.py  # Ventana de carga de antropometría
    └── formulario_antropometria.py     # Componente de formulario de antropometría
```

## Base de datos

La base de datos (`sistema_antropometrias.db`) se crea automáticamente al iniciar la aplicación.

### Tabla `jugadores`

| Campo              | Tipo    | Descripción                          |
|--------------------|---------|--------------------------------------|
| id                 | INTEGER | Clave primaria (autoincremental)     |
| nombre             | TEXT    | Nombre del jugador                   |
| apellido           | TEXT    | Apellido del jugador                 |
| dni                | TEXT    | DNI único del jugador                |
| posicion_actual    | TEXT    | Posición actual en el equipo         |
| categoria_actual   | TEXT    | Categoría actual                     |
| fecha_nacimiento   | DATE    | Fecha de nacimiento                  |
| creado_en          | DATE    | Fecha de registro en el sistema      |

### Tabla `antropometrias`

Almacena una medición completa por jugador por fecha. Incluye:

- **Datos generales**: fecha, posición, categoría, peso, talla corporal, talla sentado
- **Diámetros óseos**: biacromial, tórax transverso y anteroposterior, bi-iliocrestídeo, humeral, femoral
- **Perímetros**: cabeza, brazo relajado, brazo flexionado, antebrazo, tórax mesoesternal, cintura, cadera, muslo máximo, muslo medial, pantorrilla máxima
- **Pliegues cutáneos**: tríceps, subescapular, supraespinal, abdominal, muslo medial, pantorrilla, bíceps, cresta ilíaca

## Instalación y uso

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/TomasCielli/sistema-antropometrias.git
   cd sistema-antropometrias
   ```

2. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

La base de datos se crea automáticamente en el directorio raíz del proyecto.

## Requisitos

- Python 3.8 o superior
- Tkinter incluido en la instalación estándar de Python (en Linux puede requerir instalación separada: `sudo apt install python3-tk`)
