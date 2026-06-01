# EasyPost API Integration & US Address Parser — Spec for accounting.py

**Assigned:** Marcus → Claude  
**Date:** 2026-05-31  
**Scope:** EasyPost shipping API integration + US address parsing for the Djinn 3D print shop accounting module.

---

## Module 1 — US Address Parser

### Purpose

Parse raw freeform address strings from customer ledger inputs (Discord DMs, Telegram messages, Etsy orders) into structured USPS-normalized fields before passing to EasyPost.

---

### Data Types

```python
@dataclass
class ParsedAddress:
    raw_input:     str          # Original freeform string, preserved as-is
    name:          str          # Recipient full name
    company:       str | None   # Optional company or handle
    street1:       str          # Primary street line (number + street name)
    street2:       str | None   # Apt / Suite / Unit — None if absent
    city:          str
    state:         str          # 2-letter USPS state code (e.g., "CA")
    zip5:          str          # 5-digit ZIP code (zero-padded string, NOT int)
    zip4:          str | None   # 4-digit ZIP+4 suffix — None if not provided
    country:       str          # Default: "US"
    parse_confidence: float     # 0.0–1.0 — regex-based field confidence
    parse_errors:  list[str]    # List of field names that failed to parse
```

### Field Validation Rules

| Field | Validation | Failure Behavior |
|---|---|---|
| `street1` | Must contain a numeric house number | Append `"street1"` to `parse_errors` |
| `state` | Must be in the 50-state + DC + territory list | Append `"state"` to `parse_errors` |
| `zip5` | Must match `^\d{5}$` | Append `"zip5"` to `parse_errors` |
| `zip4` | Must match `^\d{4}$` if present | Set to `None` if malformed |
| `country` | Hardcoded to `"US"` for this shop | No validation needed |

### Formulas

```
parse_confidence = (fields_parsed_cleanly / total_expected_fields)

total_expected_fields = 5   # street1, city, state, zip5, name
```

If `parse_confidence < 0.6`, raise `AddressParseWarning` and queue for manual review before shipping label is generated.

---

### Function Signatures

```python
def parse_address(raw: str) -> ParsedAddress:
    """
    Parse a freeform US address string into structured fields.
    Uses regex heuristics. Does NOT call EasyPost — pure local parsing.
    Returns ParsedAddress with parse_confidence and parse_errors populated.
    """

def normalize_state(state_raw: str) -> str | None:
    """
    Accept full state name ("California") or abbreviation ("CA").
    Returns 2-letter USPS code or None if unrecognized.
    """

def format_address_block(addr: ParsedAddress) -> str:
    """
    Format ParsedAddress into a printable USPS-style address block.
    Returns multiline string:
        {name}
        {street1}[ {street2}]
        {city}, {state} {zip5}[-{zip4}]
    """
```

---

## Module 2 — EasyPost API Integration

### Purpose

Create shipments, buy labels, and track packages for completed print jobs. Integrates with `job` and `invoice` tables from `accounting.py`.

---

### Environment Variables

```bash
# ~/.config/djinn/easypost.env
EASYPOST_API_KEY=EZTKxxxxxxxxxxxxxxxxxxxxxxxx   # Live key from EasyPost dashboard
EASYPOST_TEST_MODE=false                        # Set true during dev — uses test key
CARRIER_ACCOUNT_USPS=ca_xxxxxxxxxxxxxxxxxxxxxxxx  # Optional: pin to your USPS account
```

Never commit this file. It must be in `.gitignore`.

---

### Data Types

```python
@dataclass
class ShipmentRequest:
    job_id:          int                 # FK → job.job_id
    customer_id:     str                 # FK → customer.customer_id
    to_address:      ParsedAddress       # Parsed + verified destination
    from_address:    ParsedAddress       # Shop origin address (loaded from config)
    weight_oz:       float               # Package weight in ounces
    length_in:       float               # Box length in inches
    width_in:        float               # Box width in inches
    height_in:       float               # Box height in inches
    service:         str                 # e.g., "First", "Priority", "GroundAdvantage"
    carrier:         str                 # e.g., "USPS", "UPS", "FedEx"
    reference:       str | None          # Optional: job_id string for tracking ("JOB-042")
    insurance_value: float               # USD — 0.0 if no insurance needed

@dataclass
class ShipmentRecord:
    shipment_id:     str                 # EasyPost shipment object ID: "shp_xxx"
    tracking_code:   str                 # Carrier tracking number
    label_url:       str                 # Presigned URL to PDF/PNG label — expires in 24h
    label_file_path: str | None          # Local path after download, None until saved
    rate_id:         str                 # EasyPost rate ID used: "rate_xxx"
    carrier:         str
    service:         str
    rate_usd:        float               # Postage cost in USD
    insurance_usd:   float               # Insurance cost in USD (0.0 if not purchased)
    total_cost_usd:  float               # rate_usd + insurance_usd
    estimated_delivery: str | None       # ISO date string "YYYY-MM-DD" or None
    status:          str                 # "created", "purchased", "in_transit", "delivered", "error"
    created_at:      str                 # ISO datetime string
    job_id:          int                 # FK → job.job_id
    customer_id:     str                 # FK → customer.customer_id

@dataclass
class TrackingEvent:
    shipment_id:     str                 # FK → shipment_record.shipment_id
    event_time:      str                 # ISO datetime string from EasyPost
    status:          str                 # "pre_transit", "in_transit", "out_for_delivery", "delivered", "failure", "return_to_sender"
    detail:          str                 # EasyPost status detail string
    location_city:   str | None
    location_state:  str | None
    location_zip:    str | None
```

---

### Database Tables

#### Table: `shipment`

| Field | Type | Description |
|---|---|---|
| `shipment_id` | `TEXT` (PK) | EasyPost `shp_xxx` ID |
| `job_id` | `INT` | FK → `job.job_id` |
| `customer_id` | `TEXT` | FK → `customer.customer_id` |
| `tracking_code` | `TEXT` | Carrier tracking number |
| `label_url` | `TEXT` | EasyPost presigned label URL |
| `label_file_path` | `TEXT` \| `NULL` | Local path after download |
| `carrier` | `TEXT` | e.g., `"USPS"` |
| `service` | `TEXT` | e.g., `"Priority"` |
| `rate_usd` | `FLOAT` | Postage cost |
| `insurance_usd` | `FLOAT` | Insurance cost (0.0 if none) |
| `total_cost_usd` | `FLOAT` | `rate_usd + insurance_usd` |
| `weight_oz` | `FLOAT` | Package weight |
| `estimated_delivery` | `TEXT` \| `NULL` | ISO date or NULL |
| `status` | `TEXT` | `created` \| `purchased` \| `in_transit` \| `delivered` \| `error` |
| `created_at` | `TEXT` | ISO datetime |

#### Table: `tracking_event`

| Field | Type | Description |
|---|---|---|
| `event_id` | `INT` (PK, autoincrement) | Internal row ID |
| `shipment_id` | `TEXT` | FK → `shipment.shipment_id` |
| `event_time` | `TEXT` | ISO datetime from carrier |
| `status` | `TEXT` | EasyPost status string |
| `detail` | `TEXT` | Human-readable status detail |
| `location_city` | `TEXT` \| `NULL` | |
| `location_state` | `TEXT` \| `NULL` | |
| `location_zip` | `TEXT` \| `NULL` | |

---

### Key Formulas

```
total_cost_usd = rate_usd + insurance_usd

# Profit impact: subtract shipping from net income if shop pays postage
net_income_adj = net_income - SUM(shipment.total_cost_usd) WHERE shipped_by_shop = TRUE

# Shipping cost recovery: how much of shipping was charged back to customer
shipping_recovery_pct = (SUM(invoice.shipping_charged) / SUM(shipment.total_cost_usd)) * 100
```

---

### Function Signatures

```python
def create_shipment(req: ShipmentRequest) -> ShipmentRecord:
    """
    POST /shipments to EasyPost.
    Verifies to_address, selects lowest rate matching req.carrier + req.service.
    Purchases label immediately.
    Saves ShipmentRecord to DB table `shipment`.
    Returns ShipmentRecord.
    Raises EasyPostError on API failure.
    """

def get_rates(req: ShipmentRequest) -> list[dict]:
    """
    POST /shipments to EasyPost WITHOUT purchasing.
    Returns raw list of rate objects for user to inspect.
    Use this before create_shipment when caller wants to confirm cost first.
    """

def download_label(record: ShipmentRecord, dest_dir: str) -> str:
    """
    Downloads label PDF from record.label_url.
    Saves to dest_dir/{shipment_id}.pdf.
    Updates shipment.label_file_path in DB.
    Returns local file path.
    Note: label_url expires in 24h — download immediately after purchase.
    """

def track_shipment(shipment_id: str) -> list[TrackingEvent]:
    """
    GET /trackers from EasyPost by tracking_code.
    Upserts new events into DB table `tracking_event`.
    Updates shipment.status in `shipment` table.
    Returns list of all TrackingEvent for this shipment.
    """

def verify_address(addr: ParsedAddress) -> ParsedAddress:
    """
    POST /addresses with verify=True to EasyPost.
    Returns a new ParsedAddress with USPS-corrected fields.
    Updates parse_confidence to 1.0 on clean verify.
    Raises AddressVerificationError if EasyPost returns deliverability=false.
    """

def get_shipping_summary(period_start: str, period_end: str) -> dict:
    """
    Query `shipment` table for date range.
    Returns:
        {
            "total_shipments": int,
            "total_cost_usd": float,
            "avg_cost_usd": float,
            "carrier_breakdown": dict[str, int],   # {"USPS": 12, "UPS": 3}
            "delivered_count": int,
            "in_transit_count": int,
            "error_count": int
        }
    """
```

---

### EasyPost API Reference (Critical Endpoints)

| Action | Method | Endpoint | Notes |
|---|---|---|---|
| Create + buy shipment | `POST` | `/v2/shipments` | Set `service` + `carrier` in body |
| Get rates only | `POST` | `/v2/shipments` | Call before buy for price check |
| Buy label | `POST` | `/v2/shipments/{id}/buy` | Pass `rate.id` in body |
| Verify address | `POST` | `/v2/addresses` | Add `?verify[]=delivery` param |
| Create tracker | `POST` | `/v2/trackers` | Pass `tracking_code` + `carrier` |
| Get tracker | `GET` | `/v2/trackers/{id}` | Poll for status updates |

**Base URL:** `https://api.easypost.com`  
**Auth:** HTTP Basic — API key as username, empty password.  
**Rate limit:** 120 req/min on live key; 30 req/min on test key.

---

### Error Handling Contract

```python
class EasyPostError(Exception):
    """Raised on non-2xx EasyPost API response."""
    status_code: int
    error_code:  str    # EasyPost error.code string
    message:     str

class AddressParseWarning(UserWarning):
    """Raised when parse_confidence < 0.6 — not fatal, queues for review."""

class AddressVerificationError(Exception):
    """Raised when EasyPost returns deliverability=false."""
```

All EasyPost calls must be wrapped in try/except. On `EasyPostError`, log to `error_log.md` (same format as printer errors), set `shipment.status = "error"`, and notify via Telegram bot (`/print_status` equivalent for shipping).

---

### Integration with accounting.py

The `shipment` table joins to `job` and `invoice` on `job_id`. When building the monthly report, include:

| Monthly Report Addition | Formula |
|---|---|
| `total_shipping_cost` | `SUM(shipment.total_cost_usd)` for period |
| `avg_shipping_cost` | `total_shipping_cost / total_shipments` |
| Updated `net_income` | `gross_profit - operating_expense - total_shipping_cost` |

Add `total_shipping_cost` and `avg_shipping_cost` as new fields to the `monthly_report` table defined in the accounting spec.

---

### Config File — Shop Origin Address

```json
// ~/.config/djinn/shop.json
{
  "name": "Djinn Forge",
  "street1": "YOUR STREET HERE",
  "street2": null,
  "city": "San Bernardino",
  "state": "CA",
  "zip5": "92401",
  "phone": "YOUR PHONE",
  "email": "YOUR EMAIL"
}
```

Load this at module init. Never hardcode the origin address in `accounting.py`.

---

## Dependency Install

```bash
pip install easypost
```

EasyPost's official Python SDK (`easypost>=9.0.0`) wraps all REST calls. Use the SDK instead of raw `requests` calls — it handles auth, retries, and response parsing.

```python
import easypost
client = easypost.EasyPostClient(api_key=os.environ["EASYPOST_API_KEY"])
```

---

## Implementation Order (Recommended)

1. `parse_address()` — local only, no API key needed, testable immediately
2. `verify_address()` — first EasyPost call, validate credentials
3. `get_rates()` — confirm shipment creation works before buying anything
4. `create_shipment()` — full buy flow
5. `download_label()` — label persistence
6. `track_shipment()` — tracking loop
7. `get_shipping_summary()` — reporting integration

