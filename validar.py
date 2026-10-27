"""Validación de estructura mínima, no reemplaza las reglas de TIC 1."""


def validar_datos(columnas, registros):
    obligatorias = {"id_prestamo", "equipo", "estado"}
    faltantes = obligatorias - set(columnas)
    if faltantes:
        raise ValueError(f"Faltan columnas: {sorted(faltantes)}")
    if not registros:
        raise ValueError("El archivo no tiene registros")
    for numero, registro in enumerate(registros, start=2):
        if any(registro.get(c) in (None, "") for c in obligatorias):
            raise ValueError(f"Campos obligatorios vacíos en fila {numero}")
        try:
            int(registro["id_prestamo"])
        except (ValueError, TypeError):
            raise ValueError(f"ID no numérico en fila {numero}") from None
    return registros
