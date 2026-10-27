import pytest
from leer import leer_archivo
from validar import validar_datos


def test_archivo_correcto():
    columnas, filas = leer_archivo("datos/prestamos.csv")
    assert len(validar_datos(columnas, filas)) == 5


def test_columna_estado_faltante():
    columnas, filas = leer_archivo("datos/prestamos_sin_estado.csv")
    with pytest.raises(ValueError, match="Faltan columnas"):
        validar_datos(columnas, filas)


def test_archivo_vacio():
    with pytest.raises(ValueError, match="no tiene registros"):
        validar_datos(["id_prestamo", "equipo", "estado"], [])
