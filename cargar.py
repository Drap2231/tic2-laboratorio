"""Carga idempotente de préstamos a PostgreSQL."""
import os
import psycopg2


def cargar_datos(registros, lote_id):
    conexion = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    )
    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prestamos (
                        id_prestamo INTEGER PRIMARY KEY,
                        equipo TEXT NOT NULL,
                        estado TEXT NOT NULL,
                        lote_id TEXT NOT NULL
                    )
                """)
                for r in registros:
                    cursor.execute("""
                        INSERT INTO prestamos (id_prestamo, equipo, estado, lote_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id_prestamo) DO UPDATE SET
                            equipo = EXCLUDED.equipo,
                            estado = EXCLUDED.estado,
                            lote_id = EXCLUDED.lote_id
                    """, (int(r["id_prestamo"]), r["equipo"], r["estado"], lote_id))
    finally:
        conexion.close()
    return len(registros)
