# GraphQL
## Strawberry

Se escogio el framework the Strawberry para el servidor de GraphQL por que tiene integracion directa con FastAPI y tiene una version experimental de integracion con Pydantic. Ademas, este maneja las mutaciones y queries de forma pythonica, como lo son las clases.

## Base de datos
Se escogio PostgreSQL por su facilidad de manejo, ademas se uso SQLAlchemy para el proceso de query a la base de datos, usando su libreria asincrona.

## Migraciones
Para no estar haciendo archivos con configuraciones y precoupandose de no crear bien las tablas, se opto por manejar Alembic, este framework se encarga de realizar los cambios de las tablas en la base de datos, ademas nos da un versionamiento para volver a otra version si este es necesario.

## UV
Ademas de que UV esta creado en Rust, los tiempos de instalacion de las dependencias son casi inmediatas, se pueden manejar varias herramientas y ademas crea un archivo de tipo Pyproject.toml donde se pueden centralizar todas las configuraciones.

