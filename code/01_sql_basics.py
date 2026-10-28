"""Day 2 · Step 1 — what a database is, in plain SQL (Python's built-in sqlite3, nothing to install).
A database is a set of TABLES; each table has COLUMNS (fields) and ROWS (records). SQL is the language to ask it things.
Run:  python 01_sql_basics.py"""
import sqlite3

con = sqlite3.connect(":memory:")                                # a throw-away database in memory — gone when the program ends
                                                                 # (Step 2's energy.db is different: it is a file on disk and stays)
con.execute("CREATE TABLE feeders (name TEXT PRIMARY KEY, v_ll REAL, i_line REAL, pf REAL)")
con.executemany("INSERT INTO feeders VALUES (?, ?, ?, ?)", [
    ("HOSTEL", 415, 120, 0.90), ("WORKSHOP", 415, 60, 0.72), ("LIBRARY", 415, 45, 0.95), ("LABS", 415, 150, 0.82)])

print("All feeders:")
for row in con.execute("SELECT name, i_line, pf FROM feeders"):
    print("  ", row)
print("\nFeeders with poor power factor (below 0.85):")
for row in con.execute("SELECT name, pf FROM feeders WHERE pf < 0.85 ORDER BY pf"):
    print("  ", row)
print("\nTotal current on all feeders:", con.execute("SELECT SUM(i_line) FROM feeders").fetchone()[0], "A")
