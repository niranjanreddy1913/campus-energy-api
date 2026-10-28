"""Day 2 · Step 3 — put two months of substation readings into the database (5,664 rows, one per 15 minutes).
Run once:  python 02_load_readings.py
This is a FULL REFRESH: it replaces every reading with the CSV. (Other strategies: incremental — add only new readings;
upsert — add new ones and update existing ones.) Delete + insert happen in ONE transaction: if anything fails before commit(),
nothing changes and the old readings stay."""
import pandas as pd
from sqlalchemy import delete, func, select

from db import Reading, Session, data_file

csv = pd.read_csv(data_file(), parse_dates=["timestamp"])
with Session() as s:
    s.execute(delete(Reading))                                       # full refresh: safe to run twice, never duplicates
    s.add_all(Reading(**row) for row in csv.to_dict("records"))
    s.commit()
    count = s.scalar(select(func.count()).select_from(Reading))
    first, last = s.scalar(select(func.min(Reading.timestamp))), s.scalar(select(func.max(Reading.timestamp)))
    print(f"Loaded {count:,} readings, {first:%d %b %Y %H:%M} → {last:%d %b %Y %H:%M}")
    print("\nThe first three rows:")
    for r in s.scalars(select(Reading).order_by(Reading.timestamp).limit(3)):
        print(f"   {r.timestamp:%d %b %H:%M}  load {r.load_kw} kW  solar {r.solar_kw} kW  air {r.ambient_c} °C")
