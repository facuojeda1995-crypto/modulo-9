Pipeline ETL Automatizado en Google Colab con SQLAlchemy 2.0 y SQLite

¿Qué se hizo y por qué?
Se desarrolló un flujo automatizado de **Extracción, Transformación y Carga (ETL)** contenido íntegramente en un cuaderno interactivo de Google Colab (`Pre entrega 8 ejecucion.ipynb`). El proceso lee registros crudos de ventas, depura inconsistencias y persiste métricas consolidadas en una base de datos relacional SQLite (`ventas_analitica.db`).

¿Por qué estructurar el flujo en celdas secuenciales dentro de una notebook?
Permite ejecutar y auditar cada etapa del pipeline (definición del esquema DDL, funciones ETL y ejecución transaccional) 
de forma directa y autocontenida sin depender de archivos externos ni configuraciones complejas.

¿Por qué utilizar SQLAlchemy 2.0 (`DeclarativeBase`, `Mapped`, `mapped_column`)? 
Garantiza tipado estático moderno, seguridad frente a inyecciones SQL y portabilidad del esquema hacia motores productivos
(PostgreSQL, MySQL o SQL Server) modificando únicamente la cadena de conexión.

¿Por qué implementar idempotencia (limpieza previa controlada)? 
En entornos de automatización, un mismo flujo puede ejecutarse múltiples veces. Eliminar los registros previos de la tabla de resumen dentro de una transacción atómica antes de insertar el nuevo cálculo evita duplicidades en la base de datos.

------------------------------------------------------------------------------------------------------------------------------------------------------------

Patrón de Datos y Esquema DDL

El proyecto implementa el patrón ETL (Extract, Transform, Load) con Carga Idempotente (Truncate & Load transaccional) en tres etapas:

1. Extracción (`extraer_datos`): Verifica la existencia de la fuente local (`ventas_crudas.csv`) y carga los registros en memoria mediante `pandas`.
2. Transformación (`transformar_datos`): Elimina órdenes duplicadas (`id_orden`), descarta filas con valores nulos o montos inválidos (`<= 0`), normaliza el formato de texto en las categorías y calcula métricas agregadas (`cantidad_ordenes`, `ingresos_totales_usd` y `ticket_promedio_usd`).
3. Carga y Persistencia (`cargar_datos`): Crea automáticamente la tabla de destino mediante el modelo ORM (`Base.metadata.create_all`) y guarda los resultados dentro de una sesión transaccional (`Session`) protegida con bloques `try / except / rollback`.

Estructura de la Tabla de Destino (`tabla_resumen_ventas_categoria`)
* `id`: Clave primaria autoincremental (`Integer`, `Primary Key`).
* `categoria`: Nombre estandarizado de la categoría (`String(100)`, `Unique`, `Not Null`).
* `cantidad_ordenes`: Total de órdenes válidas procesadas (`Integer`, `Not Null`).
* `ingresos_totales_usd`: Suma total de ventas por categoría (`Float`, `Not Null`).
* `ticket_promedio_usd`: Valor promedio por orden (`Float`, `Not Null`).

------------------------------------------------------------------------------------------------------------------------------------------------------------

Requisitos

Entorno de ejecución: Google Colab o entorno local con **Python 3.10 o superior** y soporte para Jupyter Notebooks.
Librerías necesarias:
`sqlalchemy >= 2.0`
`pandas >= 2.0`

------------------------------------------------------------------------------------------------------------------------------------------------------------

Pasos para ejecutar

1. Clona este repositorio o descarga el archivo **`Pre_entrega_8_ETL.ipynb`**.
2. Ábrelo en **Google Colab** (o en Jupyter Notebook / VS Code en local). Si trabajas en un entorno local, instala las dependencias previas:
   ```bash
   pip install sqlalchemy pandas notebook