"""Redact captured payloads into committable fixtures.

Reads every JSON file in captures/, replaces free-text and traceable values
with deterministic synthetic tokens, and writes the result to
tests/fixtures/redacted/ for review before it becomes a committed fixture.
The same input value always maps to the same token, so relationships inside
one payload survive redaction.
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
CAPTURES = REPO / "captures"
OUTPUT = REPO / "tests" / "fixtures" / "redacted"
NAMESPACE = uuid.UUID("7b19a5cb-63b1-5d64-9a54-77d64c8ac2f5")

REDACTED_KEYS = {
    "name",
    "displayname",
    "internal_name",
    "internal_remark",
    "external_remark",
    "remark",
    "description",
    "details",
    "serial",
    "ref",
    "reference",
    "number",
    "qrcodes",
    "qrcodes_of_serial_numbers",
    "serial_number_ids",
    "street",
    "house_number",
    "postal_code",
    "city",
    "state_province",
    "location_in_warehouse",
    "country_of_origin",
    "api_client",
    "conditions",
    "tags",
    "shop_description_short",
    "shop_description_long",
    "shop_seo_title",
    "shop_seo_keyword",
    "shop_seo_description",
    "color",
    "path",
    "licenseplate",
    "contact_name",
    "contact_phone",
    "contact_mailing_number",
    "contact_mailing_country",
    "contact_mailing_postalcode",
    "contact_mailing_city",
    "contact_mailing_street",
    "contact_person_lastname",
    "contact_person_email",
    "contact_person_middle_name",
    "contact_person_first_name",
    "location_name",
    "location_phone",
    "location_mailing_number",
    "location_mailing_country",
    "location_mailing_postalcode",
    "location_mailing_city",
    "location_mailing_street",
    "name_external",
    "invoice_reference",
    "remark_planner",
    "remark_client",
    "remark_crew",
    "subject",
    "filename",
    "integration_reference_id",
    "export_message",
    "projects_json",
    "accounting_code",
    "housenumber",
    "unit_number",
    "district",
    "addressline2",
    "extraaddressline",
    "state",
    "birthdate",
    "passport_number",
    "emergency_contact",
    "driving_license",
    "contract",
    "bank",
    "company_name",
    "vat_code",
    "coc_code",
    "firstname",
    "middle_name",
    "lastname",
    "email",
    "phone",
    "vt_fullname",
    "external_reference",
    "naam",
    "ext_name_line",
    "surfix",
    "surname",
    "vendor_accounting_code",
    "mailing_city",
    "mailing_street",
    "mailing_number",
    "mailing_unit_number",
    "mailing_district",
    "mailing_extra_address_line",
    "mailing_postalcode",
    "mailing_state",
    "visit_city",
    "visit_street",
    "visit_number",
    "visit_unit_number",
    "visit_district",
    "visit_extra_address_line",
    "visit_postalcode",
    "visit_state",
    "invoice_city",
    "invoice_street",
    "invoice_number",
    "invoice_unit_number",
    "invoice_district",
    "invoice_extra_address_line",
    "invoice_postalcode",
    "invoice_state",
    "phone_1",
    "phone_2",
    "email_1",
    "email_2",
    "website",
    "VAT_code",
    "fiscal_code",
    "commerce_code",
    "purchase_number",
    "bic",
    "bank_account",
    "projectnote",
    "projectnote_title",
    "contact_warning",
    "postalcode",
    "mobilephone",
    "location_details",
}


def synthetic(key: str, value: str) -> str:
    """Derive one stable synthetic replacement for one sensitive value."""
    token = uuid.uuid5(NAMESPACE, f"{key}:{value}").hex[:12]
    if key in {"serial", "qrcodes", "qrcodes_of_serial_numbers"}:
        return f"SYN-{token}"
    if key in {"city", "street", "state_province"}:
        return f"Place {token}"
    return f"Synthetic {token}"


def redact(value: Any) -> Any:
    """Walk one payload and replace every sensitive string in place."""
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if key in REDACTED_KEYS and isinstance(item, str) and item:
                if key in {"qrcodes", "qrcodes_of_serial_numbers", "tags", "serial_number_ids"}:
                    result[key] = ",".join(
                        synthetic(key, part.strip())
                        for part in item.replace("\n", ",").split(",")
                        if part.strip()
                    )
                else:
                    result[key] = synthetic(key, item)
            else:
                result[key] = redact(item)
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def main() -> int:
    """Redact every capture into tests/fixtures/redacted/."""
    if not CAPTURES.is_dir():
        print("captures/ does not exist yet, run scripts/capture_data.py first", file=sys.stderr)
        return 1
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in sorted(CAPTURES.glob("*.json")):
        payload = json.loads(path.read_text())
        (OUTPUT / path.name).write_text(json.dumps(redact(payload), indent=2))
        print(f"redacted {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
