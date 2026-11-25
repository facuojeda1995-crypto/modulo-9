Pipeline ETL Automatizado en Python con SQLAlchemy 2.0 y SQLite

Descripción y Arquitectura
Este proyecto implementa un flujo automatizado ETL (Extracción, Transformación y Carga) en Python (`etl_ventas.py`) 
diseñado para ingerir registros crudos de ventas, aplicar reglas de depuración y calidad de datos, y persistir métricas 
consolidadas en una base de datos relacional SQLite (`ventas_analitica.db`).

Esquema explícito (DDL): Definido mediante SQLAlchemy 2.0 (`DeclarativeBase`, `Mapped`, `mapped_column`) 
dentro del script y respaldado en `esquema.sql`.
Reproducibilidad e Idempotencia: El proceso ejecuta una limpieza transaccional previa
(`DELETE` dentro de una sesión atómica protegida con `try / except / rollback`), 
garantizando que correr el script múltiples veces produzca exactamente el mismo resultado sin duplicar filas.

-----------------------------------------------------------------------------------------------------------------------------

Patrón de Datos Utilizado
El flujo sigue el patrón ETL Batch con Carga Idempotente (Truncate & Load transaccional): 
1. Extracción (`extraer_datos`):** Lectura estructurada desde `ventas_crudas.csv` mediante `pandas` con validación de existencia de origen.
2. Transformación (`transformar_datos`):** Deduplicación por `id_orden`, filtrado de valores nulos y montos inválidos (`<= 0`), estandarización de texto (`strip` + `capitalize`) y agregación por categoría.
3. Carga (`cargar_datos`):** Creación automática de la tabla `tabla_resumen_ventas_categoria` y persistencia transaccional en SQLite.

-------------------------------------------------------------------------------------------------------------------------------
 Requisitos
Python: 3.10 o superior (compatible con Google Colab o ejecución local).
Dependencias:
  ```bash
  pip install sqlalchemy pandas

--------------------------------------------------------------------------------------------------------------------------------
pasos para ejecutar y verificar reproducibilidad: 
1- Clona el repositorio y accede a la carpeta del proyecto:
git clone [https://github.com/facuojeda1995-crypto/modulo-9.git](https://github.com/facuojeda1995-crypto/modulo-9.git)
cd "modulo-9/preentrega 8 "
2-Instala las dependencias necesarias:
pip install sqlalchemy pandas
3-Ejecuta el script ETL por primera vez:
python etl_ventas.py
4-Verificación de reproducibilidad: Vuelve a ejecutar python etl_ventas.py una segunda vez. Comprobarás en la salida de consola que los IDs (1 al 4) y totales por categoría se mantienen íntegros sin duplicar registros en ventas_analitica.db.
