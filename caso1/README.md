# Sistema de Gestión de Préstamos de Equipos — UNCP

Aplicación académica Django para consultar equipos y gestionar solicitudes, préstamos y devoluciones de laboratorio. No integra el sistema institucional de identidad; utiliza cuentas locales de Django.

## Tecnologías y arquitectura

Python 3, Django 5.2, SQLite, ORM, Templates, Bootstrap 5. Proyecto MVT: `config` configura el sitio, `equipos` contiene dominio, formularios, vistas, admin y middleware; `usuarios` expone login/logout.

## Instalación y ejecución

```bash
cd caso1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Visita `http://127.0.0.1:8000/`; administración en `/admin/`.

## Datos de demostración

El comando idempotente crea cinco cuentas locales: `admin.uncp`, `docente1.uncp`, `docente2.uncp`, `asistente.uncp`, `invitado.uncp`. Para práctica local todas reciben `Demo-UNCP-2026`. Cambiar las claves y no reutilizarlas fuera del entorno demo. Grupos: Administrador, Docente, Asistente e Invitado.

## Operación y seguridad

El catálogo es público; login/logout, sesiones (30 min) y logout POST con CSRF están configurados. La creación de solicitudes y devoluciones se restringe en backend por grupos. Admin permite administrar datos y ver auditoría. Cookies de sesión HttpOnly. `select_for_update` envuelve validación y alta/devolución; SQLite serializa escrituras de forma limitada y no es recomendado como motor concurrente de producción. El backend de correo de consola sirve para recordatorios locales.

## Pruebas

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py test
```

## Evidencias

`capturas/` está destinada a capturas de código/aplicación, `evidencias/` al checklist de entrega. No se agregan imágenes simuladas; completar capturas manualmente desde navegador/DevTools.

## Limitaciones

La interfaz de administración principal de entidades se ofrece en Django Admin. El rol invitado solo consulta catálogo. El stock reservado se descuenta en préstamos activos y vencidos (las solicitudes pendientes aún no reservan stock). Para despliegue real deben configurarse secretos, HTTPS, correo y motor de base de datos transaccional.
