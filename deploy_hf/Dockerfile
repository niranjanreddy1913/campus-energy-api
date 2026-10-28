# Hugging Face Docker Space for the Day 2 API — the same API, now with its SQLite database.
# Upload: this Dockerfile, requirements.txt, README.md, and from code/: app.py, appliance.py, ee.py, db.py, queries.py, 02_load_readings.py,
#         plus data/campus_feb_mar_2026.csv (upload it next to the code).
FROM python:3.12-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=user . .

EXPOSE 7860
# A Space's disk is reset when it restarts, so load the readings into a fresh energy.db every time it starts
CMD ["sh", "-c", "python 02_load_readings.py && uvicorn app:app --host 0.0.0.0 --port 7860"]
