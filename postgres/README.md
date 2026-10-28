# Day 2 · Extra: move the database from SQLite to PostgreSQL

**Why:**
- SQLite is one file on your laptop. That's perfect for learning, and fine for one user at a time.
- Real systems use a database **server** such as PostgreSQL. Many users and programs share it, it runs on its own machine, and it's built to be backed up and secured.

**What changes:** only *where* the data lives.
- The tables and the questions in `queries.py` stay the same, and so do the API and its answers.
- You change one setting, the `DATABASE_URL`.

| | SQLite (until now) | PostgreSQL (this step) |
|---|---|---|
| Where the data is | `code/energy.db`, a file | a server, here in a Docker container on **localhost:5432** |
| Install | nothing, it's built into Python | Docker Desktop and the `psycopg` driver |
| Who can use it | one program at a time writes | many users and programs at once |
| Used for | learning, prototypes, phone apps | websites, company systems, plant data |

## Before you start
- **Docker Desktop** is installed and running (the whale icon is steady).
- **Day 2 works on SQLite.** From `../code`, run `python 02_load_readings.py` (it should print "Loaded 5,664 readings…").
- **Port 5432 is free.** If another PostgreSQL is already running on your laptop, stop it first (see Troubleshooting).

## Step 1: Start PostgreSQL in Docker
```bash
cd day2_tue_database/postgres
cp .env.example .env            # Windows: copy .env.example .env
```
Open `.env` and replace `change-me-local-only` with a password of your own. It appears **in both lines**. `.env` stays on your laptop; it is never shared or committed.
```bash
docker compose up -d            # first time: downloads postgres:16-alpine (~100 MB)
docker compose ps               # STATUS should say "healthy" after a few seconds
```
You now have a PostgreSQL server:
- **Container:** `mgit-postgres`
- **Database:** `energy`
- **User:** `mgit`
- **Address:** `localhost:5432`, reachable only from your own laptop

## Step 2: Install the driver
```bash
pip install -r requirements.txt       # psycopg, the bridge between Python and PostgreSQL
```

## Step 3: Tell Python where the database is
Set `DATABASE_URL` in **the terminal you'll use**, with your own password:
```bash
# macOS / Linux
export DATABASE_URL="postgresql+psycopg://mgit:YOUR_PASSWORD@localhost:5432/energy"
# Windows PowerShell
$env:DATABASE_URL="postgresql+psycopg://mgit:YOUR_PASSWORD@localhost:5432/energy"
```
How to read it: `postgresql+psycopg` means the kind of database and the driver; then `mgit:YOUR_PASSWORD` (user and password) `@localhost:5432` (where the server is) `/energy` (which database).

`code/db.py` reads this variable. If it isn't set, `db.py` uses SQLite as before:
```python
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_FILE}")   # SQLite unless you say otherwise
```

## Step 4: Copy the data across
```bash
python migrate_sqlite_to_postgres.py
```
```
From  energy.db (SQLite)
To    postgresql+psycopg://mgit:***@localhost:5432/energy

table           SQLite  PostgreSQL
readings         5,664       5,664   ✓
calculations         2           2   ✓
appliances           2           2   ✓
```
Your `calculations` and `appliances` counts depend on what you did earlier; they only have to match.

What the script does:
- It creates the same three tables in PostgreSQL, from the same classes in `db.py`.
- It copies every row in **one transaction**, so it's all or nothing.
- It sets the id counters to continue after the copied rows.

Running it again is safe, because it empties the PostgreSQL tables first.

**Shortcut, if you only want the readings:** with `DATABASE_URL` set, run `python 02_load_readings.py` in `../code`. It loads the CSV straight into PostgreSQL. The migration script also keeps your saved calculations and appliances.

## Step 5: Run the same app on PostgreSQL
```bash
cd ../code
python test_api.py                # same answers as on SQLite: peak 859 kW, loading 106.4 %
python 03_appliances_db.py        # new appliances continue after the copied ids
uvicorn app:app --reload          # open http://127.0.0.1:8000/docs — now backed by PostgreSQL
```

## Step 6: Look inside PostgreSQL directly
```bash
docker exec -it mgit-postgres psql -U mgit -d energy -c "\dt"
docker exec -it mgit-postgres psql -U mgit -d energy -c "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM readings;"
```
```
 count |         min         |         max
-------+---------------------+---------------------
  5664 | 2026-02-01 00:00:00 | 2026-03-31 23:45:00
```
Tools such as **pgAdmin** or **DBeaver** can connect too:
- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `energy`
- **User:** `mgit`
- **Password:** the one in your `.env`

To switch back to SQLite, run `unset DATABASE_URL` (PowerShell: `Remove-Item Env:DATABASE_URL`).

## Your turn: convert the remaining days
Days 3, 4 and 5, the MCP server and the digital twin each have their own `db.py`. Each still uses SQLite. Convert every one the same way.

1. In each `db.py`, make the two changes Day 2 has:
   ```python
   import os                                                                  # add at the top
   DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_FILE}")      # replace the DATABASE_URL line
   ```
   The files are:
   - `day3_wed_ui/code/db.py`
   - `day4_thu_llm/code/db.py`
   - `day5_fri_agent/code/db.py`
   - `day5_fri_agent/mcp/code/db.py`
   - `bonus_twin_capstone/2_digital_twin/code/db.py`
2. Keep `DATABASE_URL` set and start that day's API (`uvicorn app:app --reload`). It uses the **same** PostgreSQL database you filled in Step 4, so there's no need to load anything again.
3. Run that day's programs and check the answers match what the day's page shows on SQLite.
4. **Done when:**
   - Every day runs with `DATABASE_URL` set.
   - Every day still runs when you `unset` it (back to SQLite).
   - `psql` shows the calculations you made from any day's API in one shared `calculations` table.

**Stretch:** the Day 2 Hugging Face deployment (`../deploy_hf/`) still uses SQLite inside the container. Point it at a hosted PostgreSQL instead (for example Neon or Supabase, both free) by adding `DATABASE_URL` as a **secret** in the Space settings. Never put it in a file.

## Troubleshooting
| You see | Do this |
|---|---|
| `port is already allocated` / `address already in use` on `docker compose up` | Another PostgreSQL uses 5432. Stop it (macOS: `brew services stop postgresql` or quit Postgres.app; Windows: stop the "postgresql" service) and run `docker compose up -d` again |
| `required variable POSTGRES_PASSWORD is missing` | You haven't created `.env`: run `cp .env.example .env` |
| `password authentication failed` | The password in `DATABASE_URL` doesn't match `.env`. If you changed `.env` after the first start, reset with `docker compose down -v` then `docker compose up -d` (this deletes the PostgreSQL data; copy it again with Step 4) |
| `connection refused` | The container isn't running: `docker compose up -d`, then `docker compose ps` |
| `No module named 'psycopg'` | `pip install -r requirements.txt` in the same environment you run Python from |
| The app still shows SQLite data | `DATABASE_URL` was set in a different terminal. Set it in the one running `uvicorn`/`python` |

**Stop everything:** `docker compose down` stops the server and keeps the data. `docker compose down -v` deletes the data as well.
