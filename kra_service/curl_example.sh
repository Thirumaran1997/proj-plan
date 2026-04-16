#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# curl_example.sh
# Working curl for POST /v3/client/kyc/kra/app/register
# Generated from digio_kra_request (PAN: EXGPD9203K, Name: Kabita Devi)
#
# Usage:
#   export BASE_URL="https://your-api-host.com"
#   export KRA_API_TOKEN="your-bearer-token"   # if required
#   bash curl_example.sh
#
# The request body is in payload.json (same directory).
# base64 document fields (kyc_document, aadhaar_document, pan_copy) are
# already embedded in payload.json from the digio_kra_request DB record.
# ---------------------------------------------------------------------------

set -euo pipefail

BASE_URL="${BASE_URL:-https://api.example.com}"
ENDPOINT="${BASE_URL}/v3/client/kyc/kra/app/register"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PAYLOAD_FILE="${SCRIPT_DIR}/payload.json"

if [ ! -f "$PAYLOAD_FILE" ]; then
  echo "ERROR: payload.json not found at $PAYLOAD_FILE" >&2
  exit 1
fi

AUTH_ARGS=()
if [ -n "${KRA_API_TOKEN:-}" ]; then
  AUTH_ARGS=(-H "Authorization: Bearer ${KRA_API_TOKEN}")
fi

echo "Calling: POST ${ENDPOINT}"
curl -s -X POST "${ENDPOINT}" \
  -H "Content-Type: application/json" \
  "${AUTH_ARGS[@]}" \
  -d @"${PAYLOAD_FILE}" | python3 -m json.tool
