-- Definición DDL de la tabla de destino para métricas consolidadas de ventas
CREATE TABLE IF NOT EXISTS tabla_resumen_ventas_categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria VARCHAR(100) NOT NULL UNIQUE,
    cantidad_ordenes INTEGER NOT NULL,
    ingresos_totales_usd FLOAT NOT NULL,
    ticket_promedio_usd FLOAT NOT NULL
);
