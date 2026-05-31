# djinn/shipping

Shipping pipeline for the Djinn 3D-print shop.

## Modules

| File | Purpose |
|------|----------|
| `address_parser.py` | Freeform US string → `ParsedAddress`. No API key needed. |
| `easypost_client.py` | EasyPost SDK wrapper — rates, labels, DB persistence. |
| `db_schema.sql` | SQLite schema for `shipment` + `tracking_event` tables. |

## Quickstart

```bash
# Install deps
pip install easypost requests

# Create secrets (never commit these)
mkdir -p ~/.config/djinn
echo 'EASYPOST_API_KEY=<your_test_key>' > ~/.config/djinn/easypost.env
chmod 600 ~/.config/djinn/easypost.env

# Create shop origin address
cat > ~/.config/djinn/shop.json << 'EOF'
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
EOF

# Init DB
sqlite3 ~/.config/djinn/djinn.db < djinn/shipping/db_schema.sql

# Smoke test address parser
python -m djinn.shipping.address_parser
```

## Full Pipeline Example

```python
from djinn.shipping.address_parser import parse_address
from djinn.shipping.easypost_client import DjinnShipping

# 1. Parse customer address from Discord/Telegram/Etsy
addr = parse_address("456 Oak Ave, Los Angeles, CA 90001")
assert addr.parse_confidence >= 0.6, "Low confidence — verify before proceeding"

# 2. Define parcel (measurements in inches, weight in oz)
parcel = {"length": 8, "width": 6, "height": 4, "weight": 12}

# 3. Get rates — review before buying
ship = DjinnShipping()
rates = ship.get_rates(addr, parcel, job_id=42)
for r in rates:
    print(f"{r.carrier} {r.service}: ${r.rate_usd:.2f} ({r.days}d)")

# 4. Buy cheapest label
cheapest = rates[0]
shipment = ship.create_shipment(addr, rate=cheapest, parcel=parcel, job_id=42)

# 5. Download label immediately — expires in 24h
from pathlib import Path
label_path = ship.download_label(shipment)
print(f"Label saved to: {label_path}")

# 6. Persist to DB
db = Path.home() / ".config" / "djinn" / "djinn.db"
ship.save_to_db(shipment, db)
```

## Config Files

| Path | Contents | Git-tracked? |
|------|----------|--------------|
| `~/.config/djinn/shop.json` | Shop origin address | ❌ Never |
| `~/.config/djinn/easypost.env` | `EASYPOST_API_KEY=...` | ❌ Never |
| `~/.config/djinn/djinn.db` | SQLite database | ❌ Never |
| `~/.config/djinn/labels/` | Downloaded label PDFs | ❌ Never |

## Error Handling

All EasyPost failures raise `EasyPostError`, which:
1. Appends a timestamped entry to `djinn/printer/error_log.md` in the vault
2. Sends a Telegram alert (best-effort, non-blocking)
3. Re-raises so the calling job halts cleanly

## DB Schema Notes

- `shipment.rate_usd` feeds the `monthly_shipping_summary` view
- The view produces `total_shipping_cost` and `avg_shipping_cost` per month
- Subtract `total_shipping_cost` from gross revenue in `monthly_report` to get true `net_income`
- Add `TELEGRAM_CHAT_ID=<your_id>` to `~/.config/djinn/printer-bot.env` to enable error alerts
