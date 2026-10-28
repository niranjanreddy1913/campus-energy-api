"""Exercise the Day 2 API without a server.  Run:  python test_api.py   (after 02_load_readings.py)"""
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)
client.get("/energy-cost?watts=1500&hours=8")
client.get("/bill?units=250")
print("GET /history?limit=2 ->")
for h in client.get("/history?limit=2").json():
    print("   ", h["kind"], h["inputs"], "->", h["result"])
day = client.get("/readings?start=2026-03-23T12:00&end=2026-03-23T13:00").json()
print(f"GET /readings (23 Mar 12:00–13:00) -> {len(day)} rows, first {day[0]}")
print("GET /summary?day=2026-03-23 ->", client.get("/summary?day=2026-03-23").json())
print("GET /summary?day=2026-05-01 ->", client.get("/summary?day=2026-05-01").status_code, client.get("/summary?day=2026-05-01").json())
