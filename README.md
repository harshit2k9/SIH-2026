# Secure Digital Document Management System — Upload Service

Low-latency, security-hardened document ingestion API for legal/investigation
case files. Built for SIH: FastAPI + asyncpg + PostgreSQL + MinIO + ClamAV.

## Why these choices (quick reference)

| Concern | Decision |
|---|---|
| DB driver | `asyncpg` — fastest async PostgreSQL driver, binary protocol, no ORM overhead |
| File storage | MinIO (S3-compatible) — files never touch the DB as BLOBs, keeps Postgres fast |
| Large file handling | Streamed in 1MB chunks (`aiofiles`) — flat memory usage, no event-loop blocking |
| Integrity | SHA-256 computed during streaming, stored + verifiable later |
| Chain of custody | Hash-chained `audit_log` table — tampering with history breaks the chain |
| Auth | JWT RS256, algorithm pinned server-side (prevents alg-confusion forgery) |
| Token revocation | `revoked_tokens` table checked per-request (swap for Redis SET at scale) |
| File type check | `python-magic` on actual bytes, not filename/Content-Type (both spoofable) |
| Malware | ClamAV via async `INSTREAM` — streamed straight from the quarantined file |
| SQL injection | 100% parameterized queries via asyncpg (`$1, $2...`), zero string-built SQL |
| Timing attacks | `hmac.compare_digest` for any secret/signature comparisons |
| Rate limiting | `slowapi`, per-IP/user, configurable per route |

## Setup

```bash
# System dependency for python-magic
sudo apt-get install libmagic1

pip install -r requirements.txt
cp .env.example .env   # fill in real secrets

# Generate RS256 keypair (auth service holds the private key; API only needs public)
mkdir -p keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem

# Apply schema
psql "$DATABASE_URL" -f sql/schema.sql

# Run (production: behind nginx/traefik with TLS termination)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop --http httptools
```

## Connection pool tuning notes

- `min_size=10, max_size=30` is a reasonable starting point for moderate
  concurrent load on a single Postgres instance. Rule of thumb: start near
  `2 × CPU_cores` on the DB server and load-test upward.
- If you put **PgBouncer** in front of Postgres in transaction-pooling mode,
  set `DB_STATEMENT_CACHE_SIZE=0` — prepared statement caching is
  incompatible with transaction pooling.
- `statement_timeout=15000` (15s) at the session level prevents a runaway
  query from holding a pool connection hostage indefinitely.

## Next steps I'd recommend

1. A separate **auth service** that issues short-lived (5–15 min) RS256
   access tokens + refresh tokens — not built here, this API only verifies.
2. A **download/retrieval endpoint** using short-TTL presigned MinIO URLs
   (function already stubbed in `services/storage.py`).
3. Move ClamAV daemon and MinIO into Docker Compose for the demo.
4. Load test with `locust` or `k6` against the upload endpoint to validate
   the pool sizing under your actual expected concurrency.
