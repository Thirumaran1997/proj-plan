# KYC Document Extraction Report

## Request Metadata
| Field | Value |
|-------|-------|
| PAN | `EXGPD9203K` |
| Applicant | Kabita Devi |
| Application Date | 14/04/2026 |
| KYC Mode | 5 |
| KRA Code | CVL KRA |

## Extracted Documents

| Field | File | Type | Base64 chars | Decoded size (bytes) | SHA-256 | Status |
|-------|------|------|:---:|:---:|------|:---:|
| `kyc_document` | [kyc_document.jpg](./kyc_document.jpg) | JPEG | 409,484 | 307,111 | `94693ef98b4edf2b…` | ✅ valid |
| `aadhaar_document` | [aadhaar_document.pdf](./aadhaar_document.pdf) | PDF | 833,020 | 624,763 | `7a15d3707b54cc51…` | ✅ valid |

## Validation Details

### kyc_document (JPEG)
- Base64 encoding: **valid** (`len % 4 == 0`, strict decode passed)
- JPEG SOI marker: `FFD8FF` ✅
- JPEG EOI marker: `FFD9` ✅
- No corruption detected.

### aadhaar_document (PDF)
- Base64 encoding: **valid** (`len % 4 == 0`, strict decode passed)
- PDF header: `%PDF-1.6` ✅
- PDF EOF marker: `%%EOF` present ✅
- No corruption detected.

## Fields NOT present in request

| Expected field | Status |
|----------------|--------|
| `aadhaar_xml` | ❌ Not passed |
| `aadhar_xml` | ❌ Not passed |
| `aadhar_document` (alt spelling) | ❌ Not passed |

> **Note:** If the API contract requires an Aadhaar XML field, it is currently absent from this request payload.