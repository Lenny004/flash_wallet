# Flash

Billetera digital con tarjeta virtual para el pago de servicios (telecomunicaciones y
utilities) mediante escaneo de códigos QR, recargas de saldo, transacciones recurrentes
y facturación.

> Estado: prototipo funcional en proceso de profesionalización. Consulta el plan completo
> en [docs/](docs/README.md).

## Características

- Registro e inicio de sesión de usuarios.
- Tarjeta digital (PAN, CVC, saldo) creada automáticamente al registrarse.
- Recarga de saldo.
- Escaneo de QR para dar de alta pagos de servicios.
- Procesamiento automático de pagos recurrentes.
- Historial de depósitos y de facturas, con búsqueda.
- Perfil de usuario editable.

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | FastAPI + SQLAlchemy + PyJWT + Pydantic |
| Base de datos | MySQL 8 |
| Frontend | HTML + CSS + JavaScript (SweetAlert2) |

Detalle y evolución del stack en [docs/STACK.md](docs/STACK.md).

## Estructura

```
Flash/
├── api/            # Backend FastAPI (routers, modelos, schemas, helpers)
├── views/          # Páginas HTML
├── controllers/    # Lógica JavaScript por página
├── css/            # Estilos y fuente
├── resources/      # Librerías de terceros
├── docs/           # Documentación y plan de escalado
└── dbflash.sql     # Esquema y datos semilla
```

## Puesta en marcha (desarrollo actual)

Requisitos: Python 3.12+, MySQL 8 (o XAMPP), y un servidor estático para las vistas.

1. Crear la base de datos importando `dbflash.sql`.
2. Copiar `.env.example` a `.env` y ajustar los valores.
3. Instalar dependencias del backend:

```bash
pip install -r requirements.txt
```

4. Levantar la API:

```bash
uvicorn api.api:app --reload
```

5. Servir la carpeta de vistas (por ejemplo con XAMPP o un servidor estático) y abrir
   `views/login.html`.

Documentación interactiva de la API disponible en `http://127.0.0.1:8000/docs`.

## Seguridad

Antes de publicar o desplegar, revisa [docs/SEGURIDAD.md](docs/SEGURIDAD.md). Hay secretos
que deben moverse a `.env` y rotarse, y endpoints que requieren autenticación.

## Documentación

- [Producto](docs/PRODUCTO.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Stack](docs/STACK.md)
- [Base de datos](docs/BASE_DATOS.md)
- [Seguridad](docs/SEGURIDAD.md)
- [Docker](docs/DOCKER.md)
- [GitHub](docs/GITHUB.md)
- [Roadmap](docs/ROADMAP.md)
- [Referencias](docs/REFERENCIAS.md)

## Licencia

MIT (pendiente de añadir archivo `LICENSE`).
