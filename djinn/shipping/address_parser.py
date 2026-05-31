"""
djinn/shipping/address_parser.py

Freeform US address string → ParsedAddress dataclass.
No external API dependencies. Fully standalone and testable.

Usage:
    from djinn.shipping.address_parser import parse_address, ParsedAddress

    addr = parse_address("123 Main St, San Bernardino CA 92401")
    if addr.parse_confidence < 0.6:
        # AddressParseWarning already raised — check manual review queue
        pass
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# State normalization table
# ---------------------------------------------------------------------------

_STATE_MAP: dict[str, str] = {
    # Full name → abbreviation
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
    # Already-abbreviated pass-through (uppercase)
    **{v: v for v in [
        "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID",
        "IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS",
        "MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK",
        "OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV",
        "WI","WY","DC",
    ]},
}

_VALID_ABBREVIATIONS = set(v for v in _STATE_MAP.values())


# ---------------------------------------------------------------------------
# Warning type
# ---------------------------------------------------------------------------

class AddressParseWarning(UserWarning):
    """
    Raised when parse_confidence < 0.6.
    The address is still returned but must be queued for manual review
    before any EasyPost label is purchased.
    """


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ParsedAddress:
    street:           Optional[str]   = None   # e.g. "123 Main St Apt 4"
    city:             Optional[str]   = None
    state:            Optional[str]   = None   # always 2-letter abbreviation
    zip_code:         Optional[str]   = None   # 5-digit or ZIP+4
    country:          str             = "US"
    parse_confidence: float           = 0.0    # 0.0–1.0
    raw_input:        str             = ""
    warnings:         list[str]       = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience: EasyPost-ready dict
    # ------------------------------------------------------------------
    def to_easypost_dict(self) -> dict:
        """Return a dict suitable for easypost.Address.create(**addr.to_easypost_dict())."""
        return {
            "street1": self.street or "",
            "city":    self.city   or "",
            "state":   self.state  or "",
            "zip":     self.zip_code or "",
            "country": self.country,
        }

    def is_complete(self) -> bool:
        """True when all four required fields are present."""
        return all([self.street, self.city, self.state, self.zip_code])


# ---------------------------------------------------------------------------
# State normalizer
# ---------------------------------------------------------------------------

def normalize_state(raw: str) -> Optional[str]:
    """
    Accept full state name ("California") or abbreviation ("CA") and
    return the 2-letter abbreviation, or None if unrecognized.
    """
    if not raw:
        return None
    key = raw.strip().lower()
    # Try full-name lookup
    if key in _STATE_MAP:
        return _STATE_MAP[key]
    # Try uppercase abbreviation lookup
    upper = raw.strip().upper()
    if upper in _STATE_MAP:
        return _STATE_MAP[upper]
    return None


# ---------------------------------------------------------------------------
# Core parser
# ---------------------------------------------------------------------------

# Patterns
_ZIP_RE      = re.compile(r'\b(\d{5})(?:-\d{4})?\b')
_STATE_RE    = re.compile(
    r'\b(' + '|'.join(
        re.escape(k) for k in sorted(_STATE_MAP, key=len, reverse=True)
    ) + r')\b',
    re.IGNORECASE,
)
_STREET_RE   = re.compile(
    r'^(\d+\s+[\w\s\.]+?(?:st|street|ave|avenue|blvd|boulevard|rd|road|'
    r'dr|drive|ln|lane|ct|court|way|pl|place|cir|circle|hwy|highway)'
    r'(?:\s+(?:apt|suite|ste|unit|#)\s*[\w\d-]+)?)',
    re.IGNORECASE,
)


def _score(addr: ParsedAddress) -> float:
    """Return confidence as ratio of populated required fields (0.0–1.0)."""
    fields = [addr.street, addr.city, addr.state, addr.zip_code]
    filled = sum(1 for f in fields if f)
    return filled / len(fields)


def parse_address(raw: str) -> ParsedAddress:
    """
    Parse a freeform US address string into a ParsedAddress.

    Strategy (greedy extraction, no ML):
    1. Normalize separators (newline / comma → single token stream)
    2. Extract ZIP code by regex
    3. Extract state by regex (full name or abbreviation)
    4. Remaining tokens before state = city candidate
    5. Leading digits + street suffix = street candidate
    6. Score confidence; emit AddressParseWarning if < 0.6

    Parameters
    ----------
    raw : str
        Freeform address from Discord, Telegram, Etsy, or clipboard paste.

    Returns
    -------
    ParsedAddress
        Always returned; check parse_confidence before using.
    """
    addr = ParsedAddress(raw_input=raw)
    if not raw or not raw.strip():
        addr.warnings.append("Empty input")
        warnings.warn("Empty address input", AddressParseWarning, stacklevel=2)
        return addr

    # 1. Normalize
    text = raw.strip()
    text = re.sub(r'[\r\n]+', ', ', text)      # newlines → commas
    text = re.sub(r',+', ',', text)             # collapse double commas
    text = re.sub(r'\s+', ' ', text)            # collapse whitespace

    working = text

    # 2. ZIP
    zip_match = _ZIP_RE.search(working)
    if zip_match:
        addr.zip_code = zip_match.group(0)      # keep ZIP+4 if present
        working = working[:zip_match.start()] + working[zip_match.end():]

    # 3. State
    state_match = _STATE_RE.search(working)
    if state_match:
        raw_state = state_match.group(0)
        addr.state = normalize_state(raw_state)
        working = working[:state_match.start()] + working[state_match.end():]
        if addr.state is None:
            addr.warnings.append(f"Unrecognized state token: '{raw_state}'")

    # 4. Split remaining into tokens, derive city + street
    parts = [p.strip() for p in working.split(',') if p.strip()]

    # City is typically the last non-empty token after stripping zip/state
    if len(parts) >= 2:
        addr.street = parts[0]
        addr.city   = parts[-1]
    elif len(parts) == 1:
        # Ambiguous: could be street+city crammed together
        chunk = parts[0]
        street_match = _STREET_RE.match(chunk)
        if street_match:
            addr.street = street_match.group(0).strip()
            remainder   = chunk[street_match.end():].strip().lstrip(',')
            if remainder:
                addr.city = remainder
            else:
                addr.warnings.append("City could not be separated from street")
        else:
            # No street pattern — treat whole chunk as city, flag it
            addr.city = chunk
            addr.warnings.append("Street number/suffix not detected")

    # 5. Clean up street (remove trailing commas/whitespace)
    if addr.street:
        addr.street = addr.street.strip(', ')
    if addr.city:
        addr.city = addr.city.strip(', ')

    # 6. Score
    addr.parse_confidence = _score(addr)

    if addr.parse_confidence < 0.6:
        msg = (
            f"Low-confidence address parse ({addr.parse_confidence:.0%}) for: '{raw}'. "
            "Queued for manual review — do not purchase label until verified."
        )
        addr.warnings.append(msg)
        warnings.warn(msg, AddressParseWarning, stacklevel=2)

    return addr


# ---------------------------------------------------------------------------
# CLI smoke-test  (python -m djinn.shipping.address_parser)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    samples = [
        "123 Main St, San Bernardino, CA 92401",
        "456 Oak Avenue\nLos Angeles\nCalifornia 90001",
        "789 Elm Blvd Apt 3 Denver CO 80203",
        "just some random text no address here",
        "1000 Broadway, New York, NY 10001-1234",
        "321 Pine Rd Suite 5, Houston, Texas, 77002",
    ]
    for s in samples:
        result = parse_address(s)
        print(
            f"IN : {s!r}\n"
            f"OUT: street={result.street!r} city={result.city!r} "
            f"state={result.state!r} zip={result.zip_code!r} "
            f"conf={result.parse_confidence:.0%}\n"
            f"{'WARN: ' + str(result.warnings) if result.warnings else ''}\n"
        )
