"""Day 2 · Step 6 — Monday's appliance list, now in the database: it survives a server restart.
Run:  python 03_appliances_db.py   (comment out the  client.delete(...)  line near the end and run it twice — the list keeps growing)"""
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import app
from db import engine

client = TestClient(app)
before = client.get("/appliances").json()
print(f"Appliances already stored from earlier runs: {len(before)}")
new = client.post("/appliances", json={"name": "Room AC", "watts": 1500, "hours": 8}).json()
print("POST   /appliances          ->", new)
print("PUT    /appliances/{id}     ->", client.put(f"/appliances/{new['id']}", json={"name": "Room AC", "watts": 1500, "hours": 6}).json())
print("GET    /appliances/{id}/cost ->", client.get(f"/appliances/{new['id']}/cost").json())

# Not through the API at all: ask the database directly with plain SQL — the row is really stored (SQLite or PostgreSQL).
con = engine.connect()
print("\nSQL: SELECT * FROM appliances ->", [tuple(r) for r in con.execute(text("SELECT id, name, watts, hours FROM appliances"))])
print("DELETE /appliances/{id}     ->", client.delete(f"/appliances/{new['id']}").json())
print("Rows left:", con.execute(text("SELECT COUNT(*) FROM appliances")).scalar())
con.close()
