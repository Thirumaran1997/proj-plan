# KRA Registration Service

A lightweight Python service that reads KYC records from the database (PostgreSQL) or a CSV dump, maps them from the old `register_pan_request` format to the new `common_kra_registration_request` format, and calls the `/v3/client/kyc/kra/app/register` endpoint.

## Files

| File | Purpose |
|------|---------|
| `mapper.py` | Field-mapping logic (`register_pan_request` → `common_kra_registration_request`) |
| `service.py` | CLI service: reads DB / CSV, builds payload, calls API |
| `payload.json` | Ready-to-use JSON payload built from the real `digio_kra_request` DB record |
| `curl_example.sh` | Shell script that POSTs `payload.json` to the API endpoint |
| `requirements.txt` | Python dependencies |

## Field Mapping

| Old field (`register_pan_request`) | New field (`common_kra_registration_request`) |
|------------------------------------|----------------------------------------------|
| `name` | `applicant_name` |
| `cor_add1 / cor_add2 / cor_add3` | `comm_addr1 / comm_addr2 / comm_addr3` |
| `cor_city / cor_pincode / cor_state / cor_country` | `comm_city / comm_pincode / comm_state / comm_country` |
| `cor_add_proof` | `comm_addr_proof` |
| `cor_add_ref` | `comm_ident_no` |
| `res_status` | `app_residential_status` |
| All other fields | Same name |

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run with the included payload (curl)

```bash
export BASE_URL="https://your-api-host.com"
export KRA_API_TOKEN="your-bearer-token"   # if needed
bash curl_example.sh
```

The `payload.json` file already contains the fully-mapped request (including base64 document fields) derived from the `digio_kra_request` database record for PAN `EXGPD9203K`.

### 3. Run the service with a CSV dump (dry-run)

```bash
python service.py --csv ../data-1776257662670.csv --dry-run
```

### 4. Run the service against a live PostgreSQL database

```bash
export DB_URL="postgresql://user:password@host:5432/dbname"
export BASE_URL="https://your-api-host.com"
export KRA_API_TOKEN="your-bearer-token"
python service.py
```

Filter by a specific PAN number:

```bash
python service.py --pan EXGPD9203K
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | API base URL | `https://api.example.com` |
| `KRA_API_TOKEN` | Bearer token (optional) | _(empty)_ |
| `DB_URL` | PostgreSQL connection string | _(empty)_ |
| `KRA_TIMEOUT` | HTTP timeout in seconds | `60` |
