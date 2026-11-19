# TecnoAndes | Control de asistencia y permisos

Aplicación académica Django 5.2 para registrar jornadas, permisos y vacaciones de una empresa ficticia.

## Tecnologías y arquitectura

Python 3, Django 5.2, SQLite, ORM, Django Auth/Groups, templates Django, Bootstrap 5 y CSS local. Aplicaciones separadas: `empleados`, `asistencias`, `permisos`, `auditoria`; proyecto en `config`. No usa servicios externos; Bootstrap se obtiene por CDN cuando hay conexión.

## Instalación local

```bash
cd caso3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # opcional; variables de ejemplo, configure SECRET_KEY antes de producción
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Abrir http://127.0.0.1:8000. Usuarios demo: `rrhh`, `jefe1`…`jefe5`, `empleado01`…`empleado10`, `contador`. Contraseña común únicamente para entorno local: `Demo2026!`. No reutilizar ni publicar estos usuarios en producción.

## Funcionalidades / roles

- Empleados con DNI único de 8 dígitos, correo `@tecnoandes.pe`, fecha de ingreso, área y antigüedad.
- Marcación del servidor, restricción horaria configurable por área (09:00–18:00 por defecto, margen ±2 h), jornada intradiaria, cálculo de extras sobre 8 h.
- Solicitudes con fechas, motivo mínimo, validación de solapamiento; aprobación/rechazo transaccional por RRHH o jefe directo del área; notificación interna.
- Listado de asistencias, exportación TXT; administración de Django Admin y auditoría.
- Grupos `Administrador RRHH`, `Jefe de Área`, `Empleado`, `Contador`; controles de objeto en vistas.

## Middleware, seguridad y privacidad

Middleware bloquea usuarios desactivados, recuerda marcar asistencia y audita POST/PUT/PATCH/DELETE exitosos en rutas relevantes. CSRF activo, password hashing estándar de Django, logout POST, cookie de sesión HttpOnly y expiración por inactividad de 45 minutos. SQLite/local usa HTTP. En producción configure HTTPS, `DEBUG=False`, `ALLOWED_HOSTS`, `SECRET_KEY` desde entorno, cookies Secure, HSTS, HTTPS redirect, copias de seguridad y revisión de permisos. No se implementa información salarial; el modelo no contiene sueldos.

## Desarrollo y pruebas

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py seed_demo
```

## Limitaciones conocidas

La asistencia solo contempla turnos dentro del mismo día (no turnos nocturnos). Las horas se almacenan a dos decimales. El saldo académico aplica `30 - vacaciones aprobadas`, sin prorrateo ni reglas laborales completas del Perú. El registro de auditoría web recoge metadatos de operaciones; cambios hechos directamente desde consola/ORM no pasan por ese middleware. El recordatorio se evalúa una vez por sesión. El control de horario del servicio es autoritativo; validación adicional por middleware HTTP se limita a delegar en ese servicio al marcar.
