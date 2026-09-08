# PythonAnywhere Developer deployment

The Flask application is imported by PythonAnywhere's WSGI server; do not run
the development server there.

This runbook targets the current paid **Developer** plan: one web app, three
web workers, one always-on task, scheduled tasks, and approximately 5 GB of
private storage. Confirm the exact entitlements in the account dashboard if
the account uses a legacy or regional plan name.

## Initial setup

1. Clone the repository into `/home/USERNAME/BEAT-CHALLENGE`.
2. Upload the ignored `beats/` library and create `data/`, `output/packs/`, and
   `logs/`.
3. Create a virtual environment using the same Python version selected in the
   Web tab:

   ```sh
   python3.12 -m venv /home/USERNAME/BEAT-CHALLENGE/.venv
   source /home/USERNAME/BEAT-CHALLENGE/.venv/bin/activate
   python -m pip install /home/USERNAME/BEAT-CHALLENGE
   ```

4. Set the Web tab virtualenv to `/home/USERNAME/BEAT-CHALLENGE/.venv`.
5. Copy `pythonanywhere_wsgi.example.py` into the WSGI editor, replace
   `USERNAME`, and set `SECRET_KEY` through a protected environment mechanism.
6. In a Bash console, initialize the database index:

   ```sh
   cd /home/USERNAME/BEAT-CHALLENGE
   source .venv/bin/activate
   export PYTHONPATH="$PWD/src"
   export DATABASE_URL="sqlite:////home/USERNAME/BEAT-CHALLENGE/data/beat_challenge.db"
   python -m beat_challenge_generator.ingest
   ```

   On a new deployment, initialize tables before ingestion:

   ```sh
   beat-init-db
   python -m beat_challenge_generator.ingest
   ```

7. Reload the web app and inspect the Web tab error log if the WSGI import
   fails.

## Configuration

- `DATABASE_URL` controls the SQLAlchemy database. Use an absolute path for
  SQLite on PythonAnywhere.
- `SECRET_KEY` must be set for a hosted deployment.
- `TRUSTED_HOSTS` may contain a comma-separated hostname allowlist, for example
  `USERNAME.pythonanywhere.com`.
- `ALLOWED_ORIGINS` is a comma-separated list of approved browser origins. It
  is empty by default, so CORS is disabled unless explicitly configured.
- `ALLOW_RANDOM_CHALLENGES` defaults to `false`. Daily challenge requests reuse
  an existing generated pack; random generation should only be enabled when
  resource controls are in place.
- `BEAT_API_KEY` protects random generation with an
  `Authorization: Bearer ...` header. Random mode returns `503` when enabled
  without a key, so it cannot accidentally become unauthenticated.
- `ALLOW_ASYNC_CHALLENGES` defaults to `false`. Enable it only after the
  `challenge_jobs` table exists and the always-on worker is configured.
- `JOB_RATE_LIMIT_SECONDS` and `MAX_JOBS_PER_RATE_WINDOW` default to one job
  per 60 seconds for the configured API key.

## Developer-tier operating model

Use the three web workers for short requests only. The daily endpoint should
reuse an existing pack and avoid compression on normal requests. Do not use
Flask background threads: they are not durable across worker reloads and can
duplicate work across the three processes.

For the current implementation, use scheduled tasks for maintenance:

```text
/home/USERNAME/BEAT-CHALLENGE/.venv/bin/beat-cleanup --keep 5
```

The repository includes a database-backed job table and worker for this case.
Enable it only after installing the updated package and initializing the
database:

```sh
beat-init-db
export ALLOW_ASYNC_CHALLENGES=true
export ALLOW_RANDOM_CHALLENGES=true
export BEAT_API_KEY='use-a-long-random-secret'
```

Configure the single Developer always-on task as:

```text
/home/USERNAME/BEAT-CHALLENGE/.venv/bin/beat-worker
```

The API route `POST /api/challenges` returns `202` with a job ID, and clients
poll `GET /api/challenges/<id>` before downloading from the returned
`download_url`. The worker claims jobs transactionally, writes archives
atomically, and records completion/failure. Keep only one worker process for
this SQLite-compatible design.

Example:

```sh
curl -X POST \
  -H "Authorization: Bearer $BEAT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"mode":"random"}' \
  https://USERNAME.pythonanywhere.com/api/challenges
```

Do not assume a built-in Redis service or Celery worker is included. An
external Redis service is possible on a paid plan, but it adds another service
and credential to operate.

## Database choice

SQLite is acceptable for a low-volume, mostly-read deployment. Use the
absolute path shown above and keep generation concurrency low. Developer
includes PythonAnywhere MySQL, which is the preferred next step when the
application has concurrent writes, more than one generation worker, or
business-critical pack metadata:

```text
mysql+pymysql://USERNAME:PASSWORD@USERNAME.mysql.pythonanywhere-services.com/USERNAME$DATABASE
```

Install the matching driver in the virtualenv before switching:

```sh
python -m pip install "/home/USERNAME/BEAT-CHALLENGE[mysql]"
```

The SQLAlchemy
engine enables `pool_recycle=280` and `pool_pre_ping=True` for MySQL because
PythonAnywhere documents idle database connection timeouts. Review and test
the database schema before switching; the current application uses direct
SQLAlchemy table creation rather than a complete migration workflow.

PostgreSQL is not assumed to be included with Developer. Use an external
PostgreSQL provider or upgrade if PostgreSQL-specific features are required.

## Maintenance

Generated archives remain under `output/packs/`. Run the cleanup command from a
scheduled PythonAnywhere task or manually:

```sh
source /home/USERNAME/BEAT-CHALLENGE/.venv/bin/activate
beat-cleanup --keep 5
```

Keep `data/`, `output/`, `logs/`, `.env`, and the source library out of static
file mappings. Schedule cleanup rather than relying on web-worker imports.
Review the redistribution rights for every audio asset before making
generated ZIPs public.

## Deployment checks

After configuring the Web tab and reloading, verify:

```sh
curl -f -I https://USERNAME.pythonanywhere.com/api/daily-challenge
curl -i "https://USERNAME.pythonanywhere.com/api/daily-challenge?mode=random"
curl -i -H "Authorization: Bearer $BEAT_API_KEY" \
  "https://USERNAME.pythonanywhere.com/api/daily-challenge?mode=random"
```

Expected behavior is a ZIP response for daily mode, `403` when random mode is
disabled, `503` when random mode is enabled without a configured key, and
`401` for an invalid random-mode key. Do not put the API key in a URL.
