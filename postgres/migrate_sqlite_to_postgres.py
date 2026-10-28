"""Day 2 · Extra — copy everything in energy.db (SQLite) into PostgreSQL: readings, calculations and appliances.
Run from this folder, with the container up and DATABASE_URL set (see README.md):
    python migrate_sqlite_to_postgres.py
Safe to run again: it empties the PostgreSQL tables first, and copies everything in ONE transaction."""
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "code"))                       # use the SAME table classes as the app


def postgres_url():
    """DATABASE_URL from the terminal, or from the .env file next to this script."""
    url = os.environ.get("DATABASE_URL")
    if not url and (HERE / ".env").exists():
        for line in (HERE / ".env").read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                url = line.split("=", 1)[1].strip()
    if not url or not url.startswith("postgresql"):
        sys.exit("Set DATABASE_URL to your PostgreSQL address first, e.g.\n"
                 "  DATABASE_URL=postgresql+psycopg://mgit:<password>@localhost:5432/energy")
    os.environ["DATABASE_URL"] = url                                 # db.py below now points at PostgreSQL too
    return url


url = postgres_url()
from db import DB_FILE, ApplianceRow, Base, Calculation, Reading  # noqa: E402  (after DATABASE_URL is set)

if not DB_FILE.exists():
    sys.exit(f"{DB_FILE} not found — run  python 02_load_readings.py  in ../code first")

source = create_engine(f"sqlite:///{DB_FILE}")                       # FROM: the SQLite file
target = create_engine(url)                                          # TO:   the PostgreSQL server
Base.metadata.create_all(target)                                     # same classes → same three tables in PostgreSQL

TABLES = [Reading, Calculation, ApplianceRow]
print(f"From  {DB_FILE.name} (SQLite)\nTo    {target.url.render_as_string(hide_password=True)}\n")
with Session(source) as src, Session(target) as dst:
    for model in TABLES:                                             # 1. empty the PostgreSQL tables (safe to re-run)
        dst.query(model).delete()
    for model in TABLES:                                             # 2. copy every row, column by column
        columns = [c.key for c in model.__table__.columns]
        rows = [{c: getattr(r, c) for c in columns} for r in src.scalars(select(model))]
        if rows:
            dst.execute(model.__table__.insert(), rows)
    for model in (Calculation, ApplianceRow):                        # 3. continue the id numbering after the copied rows
        table = model.__tablename__
        dst.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table}"))
    dst.commit()                                                     # all or nothing

    print(f"{'table':<14}{'SQLite':>8}{'PostgreSQL':>12}")
    for model in TABLES:
        n_src = src.scalar(select(func.count()).select_from(model))
        n_dst = dst.scalar(select(func.count()).select_from(model))
        print(f"{model.__tablename__:<14}{n_src:>8,}{n_dst:>12,}   {'✓' if n_src == n_dst else '✗ different!'}")
