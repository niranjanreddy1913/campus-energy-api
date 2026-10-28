# Day 2 · Tue 27 Oct · Connect the API to a database (1 hour)

**Goal:** the API gets a memory. Monday's appliance list survives restarts, every calculation is remembered, and two months of substation readings can be queried.

## What we are working on today

**Introduction.** Yesterday's API forgets everything the moment it answers. Real systems remember: who asked what, and every reading the equipment ever sent. They keep it in a **database**.

A database is a set of tables you can *ask questions*: "the peak on 23 March", "the five worst days". The answers come back in milliseconds and stay correct for many users at once. Today our API gets one.

### Problem statement

> The substation logger has produced two months of 15-minute readings: campus load, rooftop solar and air temperature. It is a CSV file of 5,664 rows that nobody opens. The maintenance engineer keeps asking simple questions: *"What was the peak on 23 March? How hard did the transformer work? What did we calculate last week?"* Each answer means someone spends twenty minutes in Excel.
>
> **They want the API to answer these questions directly, and to keep a record of every calculation.**

| | |
|---|---|
| **Given** | Day 1's API. `data/campus_feb_mar_2026.csv` (1 Feb – 31 Mar 2026). Transformer TR-MAIN: 630 kVA, campus power factor 0.93 |
| **Find** | `GET /history` (recent calculations), `GET /readings?start&end`, `GET /summary?day=`: peak load, energy, solar, transformer loading |
| **Constraints** | No database server to install (SQLite: one file). The same code must work on MySQL later. Loading data twice must not create duplicates |

**Key idea:** the transformer only carries what solar doesn't supply. Loading = (load − solar) ÷ 0.93 ÷ 630 kVA.

### Solution approach

| Step | What we do | File | Concept learned |
|---|---|---|---|
| 1 | Create a table, insert rows and ask questions in plain SQL | `01_sql_basics.py` | Tables, rows, keys, SELECT … WHERE, SUM |
| 2 | Describe the tables as Python classes | `db.py` | SQLAlchemy models, SQLite file |
| 3 | Load the 5,664 readings | `02_load_readings.py` | Bulk insert, repeatable loading |
| 4 | Write the questions once, as functions | `queries.py` | Reusable queries (used all week) |
| 5 | Connect them to the API; save each calculation | `app.py` | API + database |
| ✓ | Ask the API | `test_api.py` | — |

### What you'll have at the end

- An API with memory: `/history` shows the latest calculations.
- `/summary?day=2026-03-23` shows **peak 859 kW at 13:00, transformer loading 106.4% at 12:45, 9,351 kWh used, 1,848 kWh from solar**.
- A query layer (`queries.py`) that the UI, the agent and MCP will reuse.

## Session plan

| Time | What | How |
|---|---|---|
| 0–5 min | Homework review | Show `GET`/`POST /energy-cost` from the Day 1 solution; two students demo theirs |
| 5–10 min | Why a database | A CSV is a file; a database answers questions. Tables, rows, columns, primary keys. Slides 2–12 of `slides/Day2_Database_Explained.pptx` |
| 10–20 min | SQL in 10 lines | `python 01_sql_basics.py`: CREATE, INSERT, SELECT … WHERE, SUM |
| 20–30 min | SQLAlchemy: tables as Python classes | Walk through `db.py`. Then `python 02_load_readings.py` loads 5,664 readings |
| 30–45 min | The API uses the database | `queries.py`, then `app.py`: `/history`, `/readings`, `/summary` |
| 45–55 min | Try it, then Step 6 | `uvicorn app:app --reload` → `/docs` → `/summary?day=2026-03-23` (the hottest day) |
| 55–60 min | Brief the task | — |

## Run

```bash
cd code
```
```bash
python 02_load_readings.py
```
```bash
uvicorn app:app --reload
```

To test without a browser, run `python test_api.py`.

## Files

| File | What |
|---|---|
| `01_sql_basics.py` | Plain SQL with Python's built-in `sqlite3` |
| `db.py` | Two tables, `readings` and `calculations`, as SQLAlchemy classes; SQLite file `energy.db` |
| `02_load_readings.py` | Loads `../../data/campus_feb_mar_2026.csv` into the database |
| `queries.py` | The questions we ask the database. **The API, UI, agent and MCP all reuse these** |
| `app.py` | Day 1's API, plus the database |
| `appliance.py` | Monday's appliance list as an `APIRouter`, now calling `queries.py`; plugged into `app.py` with one line |
| `03_appliances_db.py` | Step 6: Monday's appliance list in a table; survives a restart; read back with plain SQL |

## Task (30–45 min)

Add `GET /peak-days?top=5`: the days the transformer worked hardest.

- **Starter:** `task/starter/` (copy over `code/`).
- **Check:** the first row is **2026-02-24, 112.8% at 12:30**.
- **Solution:** `task/solution/`.

## Materials

- **Slides:** `slides/Day2_Database_Explained.pptx`. These are 26 slides in the Actoryx format, written for anyone, including people with no coding background, with trainer notes. They open with the problem statement and solution approach, how each need became a technical decision, and the design at a glance (simulated data, where it's stored, the three tables). Then they cover what a database is (and why memory isn't enough), the CSV columns, SQL in plain English, the three tables (readings, calculations, appliances), the three calculations worked out step by step (energy cost, slab bill, calculator), the calculations log, SQL vs the ORM side by side, `db.py`, session and commit, loading the CSV, `queries.py`, the transformer loading worked example, the appliance list, how to run it, key words and a 5-question check. Every number comes from running the real code. They're generated by `../tools/build_day2_explained_deck.js`.
- **Extra step, PostgreSQL:** `postgres/` moves the database from SQLite to PostgreSQL. It uses a Docker container on localhost:5432 (`docker-compose.yml`, `.env.example`) and `migrate_sqlite_to_postgres.py`, which copies all three tables. `postgres/README.md` has the full steps, a task to convert Days 3–5, the MCP server and the twin, and troubleshooting. `code/db.py` reads `DATABASE_URL` from the environment and falls back to SQLite. Slides 20–23 of the deck cover it.
- **Older reference deck:** `slides/Actoryx_DB_Deploy.pptx` is the generic MySQL / MongoDB / Hugging Face session. It does not match this day's code; use it only as background.
- **Reference:**
  - `reference/mysql_fastapi_app.py`: the same idea on MySQL. Credentials now come from environment variables.
  - `reference/mongodb_fastapi_app.py`: a NoSQL version (`MONGO_URI` from the environment).
  - `reference/mysql_Dockerfile`.
- **Deeper:** mgit Chapter 3 (pandas): `../../chapters/ch03/index.html`
