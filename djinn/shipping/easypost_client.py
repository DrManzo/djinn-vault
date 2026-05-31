"""
djinn/shipping/easypost_client.py

EasyPost shipping integration for the Djinn 3D-print shop pipeline.

Lifecycle:
    1. parse_address()        → ParsedAddress   (address_parser.py)
    2. get_rates()            → list[Rate]       confirm cost before purchase
    3. create_shipment()      → Shipment         buy label
    4. download_label()       → Path             save PDF immediately (24h expiry)
    5. DB rows written        → shipment + tracking_event tables

Config:
    ~/.config/djinn/shop.json     — shop origin address + EasyPost API key path
    ~/.config/djinn/easypost.env  — EASYPOST_API_KEY=<key>  (chmod 600)

Never hard-code the API key or origin address.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import easypost  # pip install easypost
import requests

from djinn.shipping.address_parser import ParsedAddress, AddressParseWarning

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

CONFIG_DIR   = Path(os.environ.get("DJINN_CONFIG", Path.home() / ".config" / "djinn"))
SHOP_JSON    = CONFIG_DIR / "shop.json"
EP_ENV_FILE  = CONFIG_DIR / "easypost.env"
ERROR_LOG    = Path(os.environ.get("DJINN_VAULT", Path.home() / "Obsidian")) / "djinn" / "printer" / "error_log.md"
LABEL_DIR    = CONFIG_DIR / "labels"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class EasyPostError(Exception):
    """
    Raised on any EasyPost API failure.
    Handler contract:
        1. Append entry to error_log.md
        2. Send Telegram alert to Javier
        3. Re-raise so the caller can halt the job
    """


# ---------------------------------------------------------------------------
# Config loaders
# ---------------------------------------------------------------------------

def _load_api_key() -> str:
    """Read EASYPOST_API_KEY from ~/.config/djinn/easypost.env."""
    if not EP_ENV_FILE.exists():
        raise EasyPostError(
            f"EasyPost env file not found: {EP_ENV_FILE}. "
            "Create it with: echo 'EASYPOST_API_KEY=<key>' > {EP_ENV_FILE} && chmod 600 {EP_ENV_FILE}"
        )
    for line in EP_ENV_FILE.read_text().splitlines():
        if line.startswith("EASYPOST_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise EasyPostError("EASYPOST_API_KEY not found in easypost.env")


def _load_origin() -> dict:
    """
    Load shop origin address from ~/.config/djinn/shop.json.

    Expected shape:
    {
        "name":    "Javier Manzo",
        "company": "Djinn Prints",
        "street1": "123 Main St",
        "city":    "San Bernardino",
        "state":   "CA",
        "zip":     "92401",
        "country": "US",
        "phone":   "9095550000"
    }
    """
    if not SHOP_JSON.exists():
        raise EasyPostError(
            f"Shop config not found: {SHOP_JSON}. "
            "Create it with your shop origin address."
        )
    return json.loads(SHOP_JSON.read_text())


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Rate:
    rate_id:   str
    carrier:   str        # e.g. "USPS"
    service:   str        # e.g. "Priority"
    rate_usd:  float
    days:      Optional[int]


@dataclass
class Shipment:
    shipment_id:    str
    tracking_code:  str
    label_url:      str           # expires 24 hours after creation
    selected_rate:  Rate
    job_id:         int
    created_at:     datetime


# ---------------------------------------------------------------------------
# EasyPost client
# ---------------------------------------------------------------------------

class DjinnShipping:
    """
    Thin wrapper around the EasyPost Python SDK.
    Instantiate once per session; reuses the API key and origin address.

    Example
    -------
    ship = DjinnShipping()
    rates = ship.get_rates(to_address, job_id=42)
    cheapest = min(rates, key=lambda r: r.rate_usd)
    shipment = ship.create_shipment(to_address, rate=cheapest, job_id=42, parcel=parcel)
    label_path = ship.download_label(shipment)
    ship.save_to_db(shipment, db_path)
    """

    def __init__(self) -> None:
        self._api_key = _load_api_key()
        self._origin  = _load_origin()
        easypost.api_key = self._api_key
        LABEL_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Rates
    # ------------------------------------------------------------------

    def get_rates(
        self,
        to_addr: ParsedAddress,
        parcel: dict,
        job_id: int,
    ) -> list[Rate]:
        """
        Fetch available carrier rates WITHOUT purchasing a label.
        Always call this before create_shipment so Javier can confirm cost.

        Parameters
        ----------
        to_addr : ParsedAddress
            Output of parse_address(). Must have parse_confidence >= 0.6.
        parcel : dict
            EasyPost parcel spec, e.g.:
            {"length": 10, "width": 8, "height": 4, "weight": 16}  # oz
        job_id : int
            FK to the job table — for logging only at this stage.

        Returns
        -------
        list[Rate]
            Sorted cheapest → most expensive.
        """
        if to_addr.parse_confidence < 0.6:
            raise EasyPostError(
                f"Address confidence {to_addr.parse_confidence:.0%} < 60% for job {job_id}. "
                "Verify address before requesting rates."
            )
        try:
            ep_shipment = easypost.Shipment.create(
                to_address   = to_addr.to_easypost_dict(),
                from_address = self._origin,
                parcel       = parcel,
            )
        except Exception as exc:
            self._handle_error(exc, job_id, "get_rates")
            raise  # unreachable but satisfies type checkers

        rates = [
            Rate(
                rate_id  = r.id,
                carrier  = r.carrier,
                service  = r.service,
                rate_usd = float(r.rate),
                days     = getattr(r, "delivery_days", None),
            )
            for r in ep_shipment.rates
        ]
        return sorted(rates, key=lambda r: r.rate_usd)

    # ------------------------------------------------------------------
    # 2. Purchase label
    # ------------------------------------------------------------------

    def create_shipment(
        self,
        to_addr: ParsedAddress,
        rate: Rate,
        parcel: dict,
        job_id: int,
    ) -> Shipment:
        """
        Buy the label for a previously-fetched Rate.
        Writes nothing to the DB — call save_to_db() after.

        ⚠ Label URL expires 24 hours after creation.
           Call download_label() immediately.
        """
        try:
            ep_shipment = easypost.Shipment.create(
                to_address   = to_addr.to_easypost_dict(),
                from_address = self._origin,
                parcel       = parcel,
            )
            ep_shipment.buy(rate={"id": rate.rate_id})
        except Exception as exc:
            self._handle_error(exc, job_id, "create_shipment")
            raise

        return Shipment(
            shipment_id   = ep_shipment.id,
            tracking_code = ep_shipment.tracking_code,
            label_url     = ep_shipment.postage_label.label_url,
            selected_rate = rate,
            job_id        = job_id,
            created_at    = datetime.now(timezone.utc),
        )

    # ------------------------------------------------------------------
    # 3. Download label (must be called before 24h expiry)
    # ------------------------------------------------------------------

    def download_label(self, shipment: Shipment) -> Path:
        """
        Fetch the label PDF from EasyPost and save it locally.
        Returns the local path.

        Labels expire 24 hours after creation — call this immediately
        after create_shipment().
        """
        dest = LABEL_DIR / f"label_job{shipment.job_id}_{shipment.shipment_id}.pdf"
        try:
            resp = requests.get(shipment.label_url, timeout=30)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            log.info("Label saved: %s", dest)
        except Exception as exc:
            self._handle_error(exc, shipment.job_id, "download_label")
            raise
        return dest

    # ------------------------------------------------------------------
    # 4. Persist to SQLite
    # ------------------------------------------------------------------

    def save_to_db(self, shipment: Shipment, db_path: Path) -> None:
        """
        Write shipment row to the `shipment` table.
        Schema is defined in db_schema.sql — run that first.
        """
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO shipment
                    (shipment_id, job_id, tracking_code, carrier, service,
                     rate_usd, label_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    shipment.shipment_id,
                    shipment.job_id,
                    shipment.tracking_code,
                    shipment.selected_rate.carrier,
                    shipment.selected_rate.service,
                    shipment.selected_rate.rate_usd,
                    shipment.label_url,
                    shipment.created_at.isoformat(),
                ),
            )
            log.info("Shipment %s saved to DB for job %d", shipment.shipment_id, shipment.job_id)

    def record_tracking_event(
        self,
        db_path: Path,
        shipment_id: str,
        job_id: int,
        status: str,
        detail: str,
        event_time: Optional[datetime] = None,
    ) -> None:
        """Append a tracking status update to the tracking_event table."""
        ts = (event_time or datetime.now(timezone.utc)).isoformat()
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT INTO tracking_event
                    (shipment_id, job_id, status, detail, event_time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (shipment_id, job_id, status, detail, ts),
            )

    # ------------------------------------------------------------------
    # Error handler
    # ------------------------------------------------------------------

    def _handle_error(self, exc: Exception, job_id: int, context: str) -> None:
        """
        Log to error_log.md and send Telegram alert.
        Contract: always called before re-raising EasyPostError.
        """
        ts  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        msg = f"[{ts}] EasyPostError in {context} | job_id={job_id} | {exc}"
        log.error(msg)

        # Append to vault error log
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ERROR_LOG, "a") as f:
            f.write(f"\n### {ts} — EasyPost {context} (job {job_id})\n\n")
            f.write(f"- **Error:** `{exc}`\n")
            f.write(f"- **Context:** {context}\n")
            f.write(f"- **Job ID:** {job_id}\n")

        # Telegram alert (non-blocking best-effort)
        self._telegram_alert(msg)

    @staticmethod
    def _telegram_alert(message: str) -> None:
        """Best-effort Telegram ping — failure here must not mask the original error."""
        try:
            env_path = CONFIG_DIR / "printer-bot.env"
            if not env_path.exists():
                return
            token = None
            chat_id = None
            for line in env_path.read_text().splitlines():
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                if line.startswith("TELEGRAM_CHAT_ID="):
                    chat_id = line.split("=", 1)[1].strip()
            if token and chat_id:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": chat_id, "text": f"🚨 Djinn Shipping Error\n{message}"},
                    timeout=5,
                )
        except Exception:
            pass  # Never let Telegram failure shadow the real error
