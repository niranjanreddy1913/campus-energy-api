# Redeploy with the database (Day 2 stretch, about 10 minutes)

Same steps as Day 1 (`../../day1_mon_python_to_api/deploy_hf/HOW_TO_DEPLOY.md`). You can update your Day 1 Space or create a new one, e.g. `campus-energy-db`.

**Upload these 10 files** (Files → Add file → Upload files):

| From | Files |
|---|---|
| `deploy_hf/` | `Dockerfile`, `requirements.txt`, `README.md` (replace the Space's README) |
| `code/` | `app.py`, `appliance.py`, `ee.py`, `db.py`, `queries.py`, `02_load_readings.py` |
| `../data/` | `campus_feb_mar_2026.csv`. Upload it next to the code; `db.py` finds it there |

When the status shows **Running**, open `https://<your-username>-<space-name>.hf.space/summary?day=2026-03-23`. You should see the 23 March summary (peak 859 kW, loading 106.4%).

**What happens at start-up:**
- The Dockerfile runs `02_load_readings.py` first, which loads 5,664 readings into a fresh `energy.db`, then starts the API.
- A free Space's disk is reset on every restart, so your appliance list and calculation history start empty again. The readings are reloaded each time.
- Data that must survive restarts needs a database server, such as the MySQL version in `../reference/`. That's what a real deployment uses.
