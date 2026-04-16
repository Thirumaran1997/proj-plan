"""
service.py
----------
Reads KYC records from the database (PostgreSQL) or from the bundled CSV
file (for local testing), maps each record to the new KRA API format, and
POSTs it to the /v3/client/kyc/kra/app/register endpoint.

Usage
-----
  # Against a real Postgres database
  export DB_URL="postgresql://user:password@host:5432/dbname"
  export KRA_BASE_URL="https://api.example.com"
  python service.py

  # Local test using the CSV dump (no DB required)
  export KRA_BASE_URL="https://api.example.com"
  python service.py --csv ../data-1776257662670.csv

  # Dry-run: print the payload and curl without actually calling the API
  python service.py --csv ../data-1776257662670.csv --dry-run
"""

import argparse
import csv
import json
import logging
import os
import sys
import uuid

import requests

from mapper import build_api_payload

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config (all overridable via environment variables)
# ---------------------------------------------------------------------------
BASE_URL   = os.environ.get("KRA_BASE_URL", "https://api.example.com")
API_PATH   = "/v3/client/kyc/kra/app/register"
API_URL    = BASE_URL.rstrip("/") + API_PATH
DB_URL     = os.environ.get("DB_URL", "")          # postgresql://...
API_TOKEN  = os.environ.get("KRA_API_TOKEN", "")   # Bearer token if required
TIMEOUT    = int(os.environ.get("KRA_TIMEOUT", "60"))


# ---------------------------------------------------------------------------
# Data readers
# ---------------------------------------------------------------------------

def read_from_csv(csv_path: str) -> list[dict]:
    """Return a list of parsed digio_kra_request dicts from a CSV dump."""
    csv.field_size_limit(10_000_000)
    records = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                req_json = json.loads(row["digio_kra_request"])
                old_req  = req_json.get("register_pan_request", req_json)
                records.append({
                    "user_id":    row.get("user_id", ""),
                    "kid":        row.get("kid", ""),
                    "old_req":    old_req,
                })
            except (json.JSONDecodeError, KeyError) as exc:
                log.warning("Skipping row (parse error): %s", exc)
    return records


def read_from_db(pan_no: str | None = None) -> list[dict]:
    """
    Read from PostgreSQL.  Requires psycopg2 (`pip install psycopg2-binary`)
    and DB_URL env var.

    Optionally filter by pan_no / user_id.
    """
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        log.error("psycopg2 not installed.  Run: pip install psycopg2-binary")
        sys.exit(1)

    query = "SELECT user_id, kid, digio_kra_request FROM digio_kra_details"
    params: tuple = ()
    if pan_no:
        query += " WHERE user_id = %s"
        params = (pan_no,)

    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    records = []
    for row in rows:
        try:
            req_json = row["digio_kra_request"]
            if isinstance(req_json, str):
                req_json = json.loads(req_json)
            old_req = req_json.get("register_pan_request", req_json)
            records.append({
                "user_id": row["user_id"],
                "kid":     row["kid"],
                "old_req": old_req,
            })
        except (json.JSONDecodeError, KeyError) as exc:
            log.warning("Skipping row (parse error): %s", exc)
    return records


# ---------------------------------------------------------------------------
# API caller
# ---------------------------------------------------------------------------

def call_api(payload: dict) -> dict:
    """POST payload to the KRA registration endpoint and return the response."""
    headers = {"Content-Type": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    log.info("POST %s  (unique_request_id=%s)", API_URL,
             payload.get("unique_request_id"))
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=TIMEOUT)
    log.info("Response status: %s", resp.status_code)
    resp.raise_for_status()
    return resp.json()


def to_curl(payload: dict) -> str:
    """Return a curl command string for the given payload."""
    body = json.dumps(payload, indent=2)
    token_flag = f" \\\n  -H 'Authorization: Bearer {API_TOKEN}'" if API_TOKEN else ""
    return (
        f"curl -s -X POST '{API_URL}' \\\n"
        f"  -H 'Content-Type: application/json'{token_flag} \\\n"
        f"  -d '\n{body}\n'"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="KRA registration service")
    parser.add_argument("--csv",      help="Path to CSV dump (for local testing)")
    parser.add_argument("--pan",      help="Filter by PAN / user_id")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Print payload + curl without calling the API")
    args = parser.parse_args()

    # ---- load records ----
    if args.csv:
        records = read_from_csv(args.csv)
        if args.pan:
            records = [r for r in records if r["user_id"] == args.pan]
    elif DB_URL:
        records = read_from_db(pan_no=args.pan)
    else:
        log.error("Provide --csv <path> or set DB_URL env var.")
        sys.exit(1)

    if not records:
        log.warning("No records found.")
        return

    log.info("Processing %d record(s).", len(records))

    for rec in records:
        request_id = str(uuid.uuid4())
        payload    = build_api_payload(rec["old_req"], request_id=request_id)

        if args.dry_run:
            print("\n" + "=" * 70)
            print(f"user_id : {rec['user_id']}")
            print(f"kid     : {rec['kid']}")
            print("\n--- Payload (base64 doc fields truncated for display) ---")
            display = json.loads(json.dumps(payload))   # deep copy
            inner   = display["common_kra_registration_request"]
            for doc_field in ("kyc_document", "aadhaar_document",
                              "aadhaar_xml", "pan_copy"):
                if doc_field in inner:
                    inner[doc_field] = f"<base64 {len(inner[doc_field])} chars>"
            print(json.dumps(display, indent=2))
            print("\n--- curl (doc fields truncated) ---")
            print(to_curl(display))
        else:
            try:
                response = call_api(payload)
                log.info("user_id=%s  response=%s", rec["user_id"],
                         json.dumps(response)[:200])
            except requests.HTTPError as exc:
                log.error("HTTP error for user_id=%s: %s", rec["user_id"], exc)
            except requests.RequestException as exc:
                log.error("Request failed for user_id=%s: %s", rec["user_id"], exc)


if __name__ == "__main__":
    main()
