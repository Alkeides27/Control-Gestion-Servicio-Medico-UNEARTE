IMPORTANTE INICIAR EL ARCHIVO .env SI NO, LA WEB NO SE VA A EJECUTAR

Adicionalmente, es importante conectar la Base de Datos al proyecto Django.
Por defecto es:

DB_NAME=sistema_unearte
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

El archivo .env ya maneja estos datos, con solo configurar su maquina a ellos, correrá perfectamente.
(NOTA la contraseña "postgres" es para el usuario "postgres" que viene por defecto al instalar la BBDD)

(NOTA 2: Está Deshabilitado el modo DEBUG de Django, para habilitarlo tan simple como pasarlo de FALSE a TRUE)