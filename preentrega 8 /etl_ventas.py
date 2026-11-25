import os
import pandas as pd
from sqlalchemy import Float, Integer, String, create_engine, delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# ==============================================================================
# 1. DEFINICIÓN DEL ESQUEMA DE DESTINO (DDL CON SQLALCHEMY 2.0)
# ==============================================================================
class Base(DeclarativeBase):
  pass


class ResumenVentasCategoria(Base):
  __tablename__ = "tabla_resumen_ventas_categoria"

  id: Mapped[int] = mapped_column(primary_key=True)
  categoria: Mapped[str] = mapped_column(
      String(100), unique=True, nullable=False
  )
  cantidad_ordenes: Mapped[int] = mapped_column(Integer, nullable=False)
  ingresos_totales_usd: Mapped[float] = mapped_column(Float, nullable=False)
  ticket_promedio_usd: Mapped[float] = mapped_column(Float, nullable=False)


# ==============================================================================
# 2. GENERACIÓN / EXTRACCIÓN DE DATOS FUENTE
# ==============================================================================
def asegurar_fuente_datos(ruta_csv: str) -> None:
  """Genera un dataset CSV con registros realistas (incluyendo nulos y duplicados) si no existe."""
  if not os.path.exists(ruta_csv):
    datos_crudos = {
        "id_orden": [
            1001,
            1002,
            1003,
            1004,
            1005,
            1006,
            1007,
            1008,
            1008,
            1009,
            1010,
        ],
        "fecha": [
            "2026-10-01",
            "2026-10-01",
            "2026-10-02",
            "2026-10-02",
            "2026-10-03",
            "2026-10-03",
            "2026-10-04",
            "2026-10-04",
            "2026-10-04",
            "2026-10-05",
            "2026-10-05",
        ],
        "categoria": [
            " Electrónica ",
            "hogar",
            "ELECTRÓNICA",
            "Ropa",
            "Hogar",
            None,
            "Deportes",
            "Ropa",
            "Ropa",
            "deportes ",
            "Electrónica",
        ],
        "monto_usd": [
            320.00,
            85.50,
            540.00,
            49.90,
            -20.00,
            110.00,
            135.00,
            65.00,
            65.00,
            95.00,
            210.00,
        ],
    }
    pd.DataFrame(datos_crudos).to_csv(ruta_csv, index=False)
    print(f"[INFO] Archivo fuente creado en '{ruta_csv}'.")


def extraer_datos(ruta_csv: str) -> pd.DataFrame:
  """Lee los datos crudos desde el archivo CSV local."""
  if not os.path.exists(ruta_csv):
    raise FileNotFoundError(f"No se encontró el archivo fuente: {ruta_csv}")

  df = pd.read_csv(ruta_csv)
  print(
      f"[1. EXTRACCIÓN] Se leyeron {len(df)} registros crudos desde"
      f" '{ruta_csv}'."
  )
  return df


# ==============================================================================
# 3. TRANSFORMACIÓN Y LIMPIEZA DE DATOS
# ==============================================================================
def transformar_datos(df: pd.DataFrame) -> pd.DataFrame:
  """Elimina duplicados, filtra valores nulos/inválidos, normaliza texto y agrega métricas."""
  df_limpio = df.drop_duplicates(subset=["id_orden"]).copy()
  df_limpio = df_limpio.dropna(subset=["categoria", "monto_usd"])
  df_limpio = df_limpio[df_limpio["monto_usd"] > 0]
  df_limpio["categoria"] = (
      df_limpio["categoria"].str.strip().str.capitalize()
  )

  df_agregado = (
      df_limpio.groupby("categoria", as_index=False)
      .agg(
          cantidad_ordenes=("id_orden", "count"),
          ingresos_totales_usd=("monto_usd", "sum"),
          ticket_promedio_usd=("monto_usd", "mean"),
      )
      .round(2)
  )

  print(
      f"[2. TRANSFORMACIÓN] Registros depurados y consolidados en"
      f" {len(df_agregado)} categorías."
  )
  return df_agregado


# ==============================================================================
# 4. CARGA TRANSACCIONAL E IDEMPOTENTE EN SQLITE
# ==============================================================================
def cargar_datos(df_agregado: pd.DataFrame, url_bd: str) -> None:
  """Crea la tabla de destino y persiste los datos evitando duplicidad en ejecuciones repetidas."""
  motor = create_engine(url_bd, echo=False)
  Base.metadata.create_all(motor)

  with Session(motor) as sesion:
    try:
      # Lógica anti-duplicidad (Idempotencia): limpieza previa dentro de la transacción
      sesion.execute(delete(ResumenVentasCategoria))

      registros = [
          ResumenVentasCategoria(
              categoria=fila["categoria"],
              cantidad_ordenes=int(fila["cantidad_ordenes"]),
              ingresos_totales_usd=float(fila["ingresos_totales_usd"]),
              ticket_promedio_usd=float(fila["ticket_promedio_usd"]),
          )
          for _, fila in df_agregado.iterrows()
      ]

      sesion.add_all(registros)
      sesion.commit()
      print(
          f"[3. CARGA] {len(registros)} registros persistidos correctamente en"
          " SQLite."
      )

      print("\n--- Verificación de Tabla de Destino en SQLite ---")
      filas_guardadas = sesion.scalars(select(ResumenVentasCategoria)).all()
      for fila in filas_guardadas:
        print(
            f"ID: {fila.id} | Categoría: {fila.categoria:<12} | "
            f"Órdenes: {fila.cantidad_ordenes} | "
            f"Total: ${fila.ingresos_totales_usd:>7.2f} | "
            f"Promedio: ${fila.ticket_promedio_usd:>6.2f}"
        )

    except SQLAlchemyError as error_bd:
      sesion.rollback()
      print(f"[ERROR BD] Fallo en la carga. Se ejecutó rollback: {error_bd}")
      raise


# ==============================================================================
# 5. ORQUESTACIÓN DEL FLUJO COMPLETO
# ==============================================================================
def ejecutar_pipeline() -> None:
  ruta_fuente = "ventas_crudas.csv"
  url_base_datos = "sqlite:///ventas_analitica.db"

  try:
    asegurar_fuente_datos(ruta_fuente)
    df_crudo = extraer_datos(ruta_fuente)
    df_transformado = transformar_datos(df_crudo)
    cargar_datos(df_transformado, url_base_datos)
    print("\n[ÉXITO] Flujo ETL ejecutado de punta a punta sin errores.")
  except Exception as error:
    print(f"\n[ERROR CRÍTICO] El proceso ETL se detuvo: {error}")


if __name__ == "__main__":
  ejecutar_pipeline()
