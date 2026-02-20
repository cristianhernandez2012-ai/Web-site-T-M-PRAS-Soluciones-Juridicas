# Backend (nuevo)

Este backend es independiente de `backed lab`.

## Ejecutar

1. Crear y activar entorno virtual.
2. Instalar dependencias:
   pip install -r requirements.txt
3. Definir variable de entorno:
   WEB3FORMS_ACCESS_KEY=...
4. Iniciar servidor:
   uvicorn main:app --reload --port 8000

## Endpoint

- `POST /api/contacto`
- `GET /health`
