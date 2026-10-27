# TIC 2 — Operación y orquestación del laboratorio de préstamos

Prueba de concepto de la fase inicial. Dagster ejecuta `leer → validar → cargar`; PostgreSQL almacena préstamos; Docker Compose levanta ambos servicios. La validación es **mínima** y no sustituye el procesamiento completo de TIC 1.

## Requisitos

Docker Desktop con Docker Compose, o Docker Engine + Compose en Linux. Puertos locales 3000 y 5432 libres.

## Iniciar

1. Copiar `.env.example` a `.env` (en PowerShell: `Copy-Item .env.example .env`). Cambiar la contraseña antes de iniciar.
2. Ejecutar `docker compose up --build -d`.
3. Comprobar con `docker compose ps` y `docker compose logs dagster`.
4. Abrir http://localhost:3000, buscar `pipeline_prestamos`, abrir **Launchpad** y lanzar la ejecución.
5. Consultar la base:
   `docker compose exec postgres psql -U tic2 -d prestamos -c "SELECT * FROM prestamos ORDER BY id_prestamo;"`
   Si cambiaste POSTGRES_USER/DB, cambia también los parámetros `-U` y `-d`.

## Configuración de la ejecución

En el Launchpad, los parámetros de la operación `leer` son `archivo`, `lote_id` y `simular_fallo_temporal`. Usa los valores por defecto para la primera ejecución. Para el CSV defectuoso, cambia `archivo` a `/app/datos/prestamos_sin_estado.csv`. Para simular un fallo de lectura transitorio, activa `simular_fallo_temporal`; el primer intento falla y el segundo continúa. La sintaxis concreta del Launchpad depende de la versión instalada de Dagster.

## Pruebas solicitadas por la diapositiva 15

| Prueba | Cómo hacerla | Resultado esperado |
|---|---|---|
| Archivo correcto | Ejecutar valores predeterminados | 3 operaciones correctas; 5 filas |
| Falta `estado` | Usar `prestamos_sin_estado.csv` | Falla `validar`; no se ejecuta `cargar` |
| Archivo temporalmente inaccesible (simulado) | Activar `simular_fallo_temporal` | Primer intento de `leer` falla, luego reintenta |
| Mismo lote dos veces | Ejecutar dos veces `LOTE_001` | Sigue habiendo 5 filas por clave primaria y upsert |
| PostgreSQL no disponible | `docker compose stop postgres`, luego lanzar job | `cargar` falla y registra reintento/error |
| Recuperación | `docker compose start postgres`, esperar y ejecutar | La carga vuelve a funcionar |

Para contar filas: `docker compose exec postgres psql -U tic2 -d prestamos -c "SELECT COUNT(*) FROM prestamos;"`.

**Aviso:** Si detienes PostgreSQL, Dagster continúa activo porque son servicios separados. Docker Compose solo verifica la salud al iniciar. La prueba de lectura es una simulación controlada, no un fallo real del sistema de archivos.

## Evidencias para el informe

Guardar captura del grafo, logs de ejecución correcta, logs de dos fallos, reintento, historial, consulta SQL y tabla de fallos reintentables/no reintentables. No se incluyen capturas ni resultados fabricados; deben obtenerse al ejecutar el proyecto.

## Contrato inicial con TIC 1

Entrada: ruta CSV dentro de `/app/datos`, `lote_id` no vacío. Salida mínima: conteos en logs y tabla `prestamos` con `id_prestamo` único. Fallos de estructura detienen la carga. TIC 1 deberá acordar después reglas de calidad completas, formato de resultados válidos/rechazados, manejo de cuarentena y claves de negocio.

## Limitaciones

- `dagster dev` es para desarrollo local, no despliegue de producción.
- Las dependencias Python están acotadas por rangos, pero no fijadas a un lockfile; para reproducibilidad estricta se deben congelar versiones después de verificar el entorno.
- Se usa una única tabla de demostración y `upsert`; no es un Data Warehouse dimensional.
- El historial de Dagster se guarda en un volumen local; no se configura su almacenamiento de eventos en PostgreSQL.
- El reintento de `cargar` aplica a excepciones de la operación, no clasifica aún fallos permanentes y transitorios.
- Si cambias usuario/contraseña en `.env` después de crear el volumen de PostgreSQL, debes actualizar las credenciales de la base existente o recrear el volumen de forma consciente.

## Detener

`docker compose down` conserva los datos. **No usar `docker compose down -v`** si quieres conservar las evidencias.

## Pruebas unitarias opcionales

Con Python 3.11 y dependencias instaladas: `python -m pytest -q`.
