from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import calendar

import os
import requests
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from collections import defaultdict

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def home():
    return FileResponse(str(STATIC_DIR / "index.html"))


def calendly_available_times(token: str, event_type_uri: str, tz: str, start_utc: datetime, end_utc: datetime):
    """Llama a Calendly para un rango <= 7 días."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "event_type": event_type_uri,
        "start_time": start_utc.isoformat().replace("+00:00", "Z"),
        "end_time": end_utc.isoformat().replace("+00:00", "Z"),
        "timezone": tz,
    }
    r = requests.get(
        "https://api.calendly.com/event_type_available_times",
        headers=headers,
        params=params,
        timeout=25
    )
    if r.status_code >= 400:
        return None, {"status": r.status_code, "details": r.text}
    return r.json(), None


@app.get("/api/disponibilidad")
def disponibilidad(year: int, month: int):
    token = os.getenv("CALENDLY_TOKEN")
    event_type_uri = os.getenv("CALENDLY_EVENT_TYPE_URI")
    tz = os.getenv("TIMEZONE", "America/Bogota")

    if not token:
        return {"error": "Falta CALENDLY_TOKEN"}
    if not event_type_uri:
        return {"error": "Falta CALENDLY_EVENT_TYPE_URI"}
    if month < 1 or month > 12:
        return {"error": "month debe estar entre 1 y 12"}

    # Rango del mes (UTC)
    month_start = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    month_end = month_start + relativedelta(months=1)

    # Calendly exige start_time en el futuro (por si piden un mes pasado)
    now_utc = datetime.now(timezone.utc)
    if month_end <= now_utc:
        return {"error": "El mes solicitado está en el pasado. Calendly exige start_time en el futuro."}

    # Si el mes empieza en el pasado (mes actual), arrancamos desde "ahora"
    query_start = month_start if month_start > now_utc else now_utc
    query_end = month_end

    # Consultar por bloques de máximo 7 días
    by_day = defaultdict(int)
    cursor = query_start

    # seguridad para no loops infinitos
    max_calls = 10  # un mes suele ser 4-5; 10 sobra
    calls = 0

    while cursor < query_end and calls < max_calls:
        calls += 1
        end = min(cursor + timedelta(days=7), query_end)

        data, err = calendly_available_times(token, event_type_uri, tz, cursor, end)
        if err:
            return {"error": "Calendly API", **err}

        slots = data.get("collection", [])
        for s in slots:
            st = s.get("start_time")
            if st:
                by_day[st[:10]] += 1

        cursor = end  # siguiente bloque

    # Construimos todos los días del mes para pintar calendario
    days_in_month = calendar.monthrange(year, month)[1]
    days = []
    for d in range(1, days_in_month + 1):
        day_key = f"{year:04d}-{month:02d}-{d:02d}"
        count = by_day.get(day_key, 0)
        days.append({"date": day_key, "hasAvailability": count > 0, "slotsCount": count})

    return {"month": f"{year:04d}-{month:02d}", "timezone": tz, "days": days}