"""Pipeline educativo TIC 2: leer -> validar -> cargar."""
import os
from pathlib import Path
from dagster import op, job, Definitions, Config, RetryPolicy, Failure
from leer import leer_archivo
from validar import validar_datos
from cargar import cargar_datos


class LecturaConfig(Config):
    archivo: str = "/app/datos/prestamos.csv"
    lote_id: str = "LOTE_001"
    simular_fallo_temporal: bool = False


@op(retry_policy=RetryPolicy(max_retries=1, delay=5))
def leer(context, config: LecturaConfig):
    # Falla una sola vez por run para mostrar el reintento de Dagster.
    if config.simular_fallo_temporal and context.retry_number == 0:
        raise OSError("Fallo temporal simulado de lectura")
    if not config.lote_id.strip():
        raise Failure("El lote_id no puede estar vacío")
    ruta = Path(config.archivo).resolve()
    base = Path("/app/datos").resolve()
    if not ruta.is_relative_to(base):
        raise Failure("El archivo debe estar dentro de /app/datos")
    columnas, registros = leer_archivo(ruta)
    context.log.info(f"Lote {config.lote_id}: {len(registros)} filas leídas")
    return {"columnas": columnas, "registros": registros, "lote_id": config.lote_id}


@op
def validar(context, datos):
    registros = validar_datos(datos["columnas"], datos["registros"])
    context.log.info(f"Validación correcta: {len(registros)} registros")
    return {"registros": registros, "lote_id": datos["lote_id"]}


@op(retry_policy=RetryPolicy(max_retries=1, delay=5))
def cargar(context, datos):
    total = cargar_datos(datos["registros"], datos["lote_id"])
    context.log.info(f"Carga completada: {total} registros del lote {datos['lote_id']}")


@job
def pipeline_prestamos():
    cargar(validar(leer()))


defs = Definitions(jobs=[pipeline_prestamos])
