# Sistema de Tracking para Ciencia de Datos (SQLAlchemy 2.0)

Descripción
Este proyecto implementa una arquitectura orientada a objetos para la persistencia de datos analíticos utilizando  mediante la sintaxis moderna (`DeclarativeBase`, `Mapped` y `mapped_column`)

Entidades del Modelo
1. **ConjuntoDatos** (Tabla: `tabla_conjuntos_datos`): Almacena metadatos de los archivos procesados (`id`, `nombre`, `url_fuente`, `numero_filas`).
2. **ExperimentoModelo** (Tabla: `tabla_experimentos_modelos`): Almacena los resultados de los modelos entrenados (`id`, `nombre_algoritmo`, `exactitud`, `esta_desplegado`).

## Ejecución
1. Abre tu entorno de Google Colab.
2. Asegúrate de tener los archivos `models.py` y `main.py` creados con el contenido provisto.
3. Ejecuta el script principal en una celda:
   ```bash
   python main.py