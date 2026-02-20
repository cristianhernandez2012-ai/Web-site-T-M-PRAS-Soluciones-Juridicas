import os
import requests

TOKEN = os.getenv("CALENDLY_TOKEN")
if not TOKEN:
    raise SystemExit("Falta CALENDLY_TOKEN en variables de entorno")

headers = {"Authorization": f"Bearer {TOKEN}"}

# 1) quién soy
me = requests.get("https://api.calendly.com/users/me", headers=headers, timeout=20).json()
user_uri = me["resource"]["uri"]
print("USER URI:", user_uri)

# 2) listar tipos de evento
r = requests.get(
    "https://api.calendly.com/event_types",
    headers=headers,
    params={"user": user_uri, "active": "true"},
    timeout=20,
)
data = r.json()

print("\nEVENT TYPES (elige el correcto):")
for ev in data.get("collection", []):
    print("- name:", ev.get("name"))
    print("  uri :", ev.get("uri"))
    print("  slug:", ev.get("slug"))
    print()