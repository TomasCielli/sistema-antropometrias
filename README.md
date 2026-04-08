# Sistema de Antropometrías — Albatros Rugby Club

Sistema web para la carga y seguimiento de datos antropométricos de los jugadores del club **Albatros Rugby Club** (La Plata). Diseñado para ser usado por la nutricionista del club desde cualquier dispositivo en la red local (notebook, iPad, celular).

## Stack

- **Backend**: Python + Flask
- **Base de datos**: SQLite
- **Frontend**: Bootstrap 5 (offline, sin conexión a internet)
- **Import/Export**: Excel (.xlsx) via openpyxl

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
git clone https://github.com/TomasCielli/sistema-antropometrias.git
cd sistema-antropometrias
pip install -r requirements.txt
```

## Uso

### Opción 1 — Doble clic (Windows)

Ejecutar `iniciar.bat`. Verifica Python, instala dependencias, muestra la IP para conectarse desde otros dispositivos y abre el navegador automáticamente.

### Opción 2 — Terminal

```bash
python app.py
```

Abrir en el navegador: `http://localhost:5000`

### Acceso desde iPad / celular

Conectar el dispositivo a la misma red WiFi que la notebook. Abrir el navegador y navegar a `http://<IP-de-la-notebook>:5000`. La IP se muestra al iniciar la app.

## Módulos

### Jugadores

CRUD completo de jugadores con los siguientes datos:

| Campo | Obligatorio |
|-------|:-----------:|
| Apellido | Si |
| Nombre | Si |
| DNI | Si (único) |
| Sexo | Si |
| Fecha de nacimiento | Si |
| Posición | No |
| Categoría | No |
| Objetivo | No |

**Categorías**: M15, M16, M17, M18, M19, Plantel Superior

**Posiciones**: Ala, Apertura, Centro, Fullback, Hooker, Medio scrum, Numero 8, Pilar, Segunda línea, Segundo centro, Wing

**Objetivo**: Optimización, Aumento de masa muscular, Descenso de grasa

La lista de jugadores permite buscar por nombre/apellido/DNI y filtrar por categoría y sexo. Al eliminar un jugador se eliminan todas sus antropometrías (con confirmación previa).

### Antropometrías

Cada jugador puede tener múltiples estudios antropométricos, cada uno identificado por fecha. Los datos se organizan en 4 secciones:

- **Medidas generales**: Peso (kg), Talla corporal (cm), Talla sentado (cm)
- **Diámetros (cm)**: Biacromial, Tórax transverso, Tórax anteroposterior, Bi-iliocrestídeo, Humeral, Femoral
- **Perímetros (cm)**: Cabeza, Brazo relajado, Brazo flexionado, Antebrazo, Tórax mesoesternal, Cintura, Cadera, Muslo máximo, Muslo medial, Pantorrilla máxima
- **Pliegues cutáneos (mm)**: Tríceps, Subescapular, Supraespinal, Abdominal, Muslo medial, Pantorrilla, Bíceps, Cresta ilíaca

La categoría y posición se guardan como snapshot al momento de la medición (no cambian si luego se edita el jugador). Al crear una nueva medición, la posición y categoría actuales del jugador se actualizan automáticamente.

### Tablas de Referencia

Se pueden cargar perfiles de referencia por deporte (por ejemplo Rugby), categoría, posición y sexo para comparar mediciones reales contra una referencia objetivo.

- Gestión completa: alta, edición y baja desde la sección **Referencias**.
- Comparación flexible: permite comparar múltiples mediciones entre sí o una medición + una referencia.
- Import / export: la hoja **Referencias** se exporta automáticamente y su importación es opcional.

### Informe General

Reporte evolutivo del club que muestra las últimas 3 antropometrías de cada jugador con los siguientes cálculos:

| Dato | Fórmula |
|------|---------|
| Talla | Valor directo |
| Peso | Valor directo |
| Sumatoria de pliegues | Suma de los 8 pliegues |
| % Grasa | Yuhasz modificada (M: Σ6 × 0.1051 + 2.585 / F: Σ6 × 0.1580 + 3.580) |
| Kg Grasa | Peso × %Grasa / 100 |
| Masa Muscular (kg) | Lee 2000 |
| Masa Ósea (kg) | Von Döbeln-Rocha |
| Masa Magra (kg) | Peso - Kg Grasa |
| Objetivo | Definido manualmente por la nutricionista |

El informe es filtrable por categoría, posición y sexo.

### Import / Export

- **Exportar**: descarga un archivo `.xlsx` con toda la base de datos (2 hojas: Jugadores y Antropometrías)
- **Importar**: sube un archivo `.xlsx` con el mismo formato
  - Detecta conflictos: si un jugador del archivo ya existe con datos diferentes, muestra una comparación campo por campo y permite elegir entre mantener o sobreescribir
  - Reporta errores detallados por fila y campo
  - Ideal para sincronizar datos entre dispositivos (ej: notebook y iPad)

## Estructura del proyecto

```
├── app.py                          # Entry point Flask
├── config.py                       # Configuración (DB, host, puerto)
├── database.py                     # Creación del schema SQLite
├── iniciar.bat                     # Script de inicio para Windows
├── requirements.txt                # Dependencias (flask, openpyxl)
├── models/
│   ├── jugadores.py                # CRUD jugadores
│   ├── antropometrias.py           # CRUD antropometrías
│   └── informes.py                 # Motor de cálculos (composición corporal)
├── routes/
│   ├── jugadores.py                # Rutas /jugadores
│   ├── antropometrias.py           # Rutas /antropometrias
│   ├── informes.py                 # Rutas /informes
│   └── datos.py                    # Rutas /datos (import/export)
├── templates/
│   ├── base.html                   # Layout + navbar
│   ├── jugadores/                  # Templates de jugadores
│   ├── antropometrias/             # Templates de antropometrías
│   ├── informes/                   # Template del informe general
│   └── datos/                      # Templates de import/export
└── static/
    ├── css/
    │   ├── bootstrap.min.css       # Bootstrap 5.3.3 (offline)
    │   └── main.css                # Estilos custom
    └── js/
        ├── bootstrap.bundle.min.js # Bootstrap 5.3.3 JS (offline)
        └── main.js                 # Búsqueda/filtros client-side
```

## Logo

Para agregar el logo del club, guardar la imagen como `static/img/logo.png`. Se mostrará automáticamente en el navbar.
