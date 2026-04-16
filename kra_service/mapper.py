"""
mapper.py
---------
Maps fields from the old `register_pan_request` structure (stored in the
`digio_kra_request` column of the database) to the new
`common_kra_registration_request` structure required by the
{BASE_URL}/v3/client/kyc/kra/app/register endpoint.
"""

import uuid


# ---------------------------------------------------------------------------
# Field mapping: old key -> new key  (None means "keep same key", value means rename)
# ---------------------------------------------------------------------------
SIMPLE_FIELD_MAP = {
    # identity / PAN
    "uid_no":          "uid_no",
    "pan_no":          "pan_no",
    "dob_date":        "dob_date",
    "gender":          "gender",
    "martial_status":  "martial_status",
    "mob_no":          "mob_no",
    "email":           "email",
    "nationality":     "nationality",

    # name fields
    "name":            "applicant_name",
    "father_name":     "father_name",

    # permanent address
    "per_add1":        "per_add1",
    "per_add2":        "per_add2",
    "per_city":        "per_city",
    "per_pincode":     "per_pincode",
    "per_state":       "per_state",
    "per_country":     "per_country",
    "per_add_proof":   "per_add_proof",
    "per_add_flag":    "per_add_flag",

    # correspondence / communication address  (old cor_* -> new comm_*)
    "cor_add1":        "comm_addr1",
    "cor_add2":        "comm_addr2",
    "cor_add3":        "comm_addr3",
    "cor_city":        "comm_city",
    "cor_pincode":     "comm_pincode",
    "cor_state":       "comm_state",
    "cor_country":     "comm_country",
    "cor_add_proof":   "comm_addr_proof",
    "cor_add_ref":     "comm_ident_no",

    # IPV
    "ipv_flag":        "ipv_flag",
    "ipv_date":        "ipv_date",

    # KYC meta
    "kyc_mode":        "kyc_mode",
    "kyc_type":        "kyc_type",
    "kyc_date":        "kyc_date",
    "mobile_flag":     "mobile_flag",
    "email_flag":      "email_flag",
    "otp_ref_no":      "otp_ref_no",

    # KRA / POS
    "kra_code":        "kra_code",
    "pos_code":        "pos_code",
    "update_flag":     "update_flag",

    # exemption
    "app_exmt":           "app_exmt",
    "app_exmt_id_proof":  "app_exmt_id_proof",

    # residential / proof
    "res_status":      "app_residential_status",
    "doc_proof":       "doc_proof",

    # documents (base64)
    "pan_copy":           "pan_copy",
    "kyc_document":       "kyc_document",
    "aadhaar_document":   "aadhaar_document",
    "aadhaar_xml":        "aadhaar_xml",

    # optional / additional
    "income":          "income",
    "occupation":      "occupation",
    "net_worth":       "net_worth",
    "net_worth_date":  "net_worth_date",
    "fax_no":          "fax_no",
    "uid_token":       "uid_token",
    "vid_no":          "vid_no",
    "uidai_refno":     "uidai_refno",
    "aadhaar_passcode":"aadhaar_passcode",
    "aadhaar_digit":   "aadhaar_digit",
    "internal_ref":    "internal_ref",
    "branch_code":     "branch_code",
    "app_no":          "app_no",
    "reg_no":          "reg_no",
}


def map_request(old_req: dict) -> dict:
    """
    Convert a `register_pan_request` dict to a `common_kra_registration_request`
    dict.  Fields not in the mapping are silently skipped.  Fields that are
    empty strings / None are omitted from the output.
    """
    new = {}
    for old_key, new_key in SIMPLE_FIELD_MAP.items():
        value = old_req.get(old_key)
        if value is not None and value != "" and value != "NULL":
            new[new_key] = value

    # fatca_additional_details and additional_details are arrays – carry them
    # through if present in the old request
    for array_field in ("fatca_additional_details", "additional_details"):
        if old_req.get(array_field):
            new[array_field] = old_req[array_field]

    return new


def build_api_payload(old_req: dict, request_id: str | None = None) -> dict:
    """
    Wrap the mapped request in the outer envelope expected by the new API.
    """
    return {
        "common_kra_registration_request": map_request(old_req),
        "unique_request_id": request_id or str(uuid.uuid4()),
        "api_request_type": "stateless",
        "service_provider": "NDML",
        "kra_providers": "NDML",
    }
