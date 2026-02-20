import os
import re
from typing import Optional

import requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TM PRAS Contact Backend")


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[+()\-\s0-9]{7,25}$")


def _parse_origins() -> list[str]:
    raw = os.getenv("FRONTEND_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
    origins = [x.strip() for x in raw.split(",") if x.strip()]
    return origins or ["http://localhost:8000"]


origins = _parse_origins()
allow_credentials = "*" not in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/contacto")
def contacto(
    name: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    service: str = Form(""),
    incidentDate: str = Form(""),
    message: str = Form(""),
    incident_date: Optional[str] = Form(None),
) -> dict:
    access_key = os.getenv("WEB3FORMS_ACCESS_KEY")
    if not access_key:
        raise HTTPException(status_code=500, detail="Falta WEB3FORMS_ACCESS_KEY")

    name = name.strip()
    email = email.strip()
    phone = phone.strip()
    service = service.strip()
    message = message.strip()
    incident = (incident_date or incidentDate or "").strip()

    if not name or not email or not message:
        raise HTTPException(status_code=400, detail="name, email y message son obligatorios")

    if len(name) < 3:
        raise HTTPException(status_code=400, detail="El nombre debe tener al menos 3 caracteres")

    if len(message) < 20:
        raise HTTPException(status_code=400, detail="El mensaje debe tener al menos 20 caracteres")

    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Email invalido")

    if phone and not PHONE_RE.match(phone):
        raise HTTPException(status_code=400, detail="Telefono invalido")

    payload = {
        "access_key": access_key,
        "subject": "Nueva consulta desde contacto",
        "from_name": "Sitio T&M PRAS",
        "name": name,
        "email": email,
        "phone": phone,
        "service": service,
        "incidentDate": incident,
        "message": message,
    }

    try:
        resp = requests.post("https://api.web3forms.com/submit", data=payload, timeout=20)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="No se pudo contactar Web3Forms")

    try:
        data = resp.json()
    except ValueError:
        data = {"message": resp.text}

    success_flag = data.get("success")
    is_success = resp.ok and (success_flag is True or str(success_flag).lower() == "true")

    if not is_success:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "web3forms_error",
                "status": resp.status_code,
                "message": data.get("message", "Error enviando formulario"),
            },
        )

    return {"success": True, "message": "Consulta enviada correctamente"}


