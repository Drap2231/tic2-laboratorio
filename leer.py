"""Lectura de CSV para la prueba mínima de TIC 2."""
import csv


def leer_archivo(ruta):
    with open(ruta, newline="", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        columnas = lector.fieldnames or []
        registros = list(lector)
    return columnas, registros
