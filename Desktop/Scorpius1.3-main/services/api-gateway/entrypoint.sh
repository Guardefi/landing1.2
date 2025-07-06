#!/usr/bin/env sh
set -e

###############################################################################
# 0. Always run from /app and ensure PATH contains /usr/local/bin
###############################################################################
cd /app
export PATH="/usr/local/bin:${PATH}"

###############################################################################
# 1. Sanity-check required files
###############################################################################
[ -d "./migrations" ]  || { echo "❌ migrations/ folder missing";  exit 1; }
[ -f "./alembic.ini" ] || { echo "❌ alembic.ini missing";        exit 1; }

###############################################################################
# 2. Wait for Postgres to be reachable
###############################################################################
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
printf "Waiting for database (%s:%s)" "$DB_HOST" "$DB_PORT"
until nc -z "$DB_HOST" "$DB_PORT" >/dev/null 2>&1 ; do printf "."; sleep 1; done
printf "\n✅  Database is ready\n"

###############################################################################
# 3. Run migrations
###############################################################################
echo "Running Alembic migrations…"
alembic -c ./alembic.ini upgrade head

###############################################################################
# 4. Launch the API with Gunicorn
###############################################################################
exec gunicorn main:app \
     -k uvicorn.workers.UvicornWorker \
     -b "0.0.0.0:${PORT:-8000}"
