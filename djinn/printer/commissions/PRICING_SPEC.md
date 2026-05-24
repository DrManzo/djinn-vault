# FairPrintAgent — Commission Pricing Spec

**Script:** `djinn-print-quote`  
**History log:** `djinn/printer/commissions/quote-history.jsonl`

## Usage

```bash
djinn-print-quote '<json>'     # full spec
djinn-print-quote --coin       # Typhon's Forge coin preset
djinn-print-quote --quick      # interactive prompt
djinn-print-quote --json-out   # machine-readable JSON output
```

From Telegram/Discord:
- `quote <json>` — full quote
- `quote coin` — coin preset
- `quote help` — field reference

---

## Formula

```
base_cost = material + labor + depreciation + maintenance + electricity + extras
risk_adjusted = base_cost / success_rate
cost_floor = risk_adjusted × (1 + minimum_margin)
fair_market = wc×cost_floor + wm×market_median + wv×(cost_floor + value_premium)
premium_ceiling = fair_market × 1.15
```

## Job-type weights

| Type | Cost | Market | Value |
|------|-----:|-------:|------:|
| commodity_decor | 0.65 | 0.30 | 0.05 |
| functional_custom_part | 0.55 | 0.30 | 0.15 |
| design_heavy_oneoff | 0.40 | 0.25 | 0.35 |
| urgent_rush | 0.50 | 0.20 | 0.30 |

## Calliope defaults (pre-filled)

- Machine: $399, 5000hr lifespan, $0.10/hr maintenance
- Power: 180W @ $0.13/kWh
- Success rate: 92%, minimum margin: 30%
- Labor rate: $20/hr

## Key insight: design time amortization

Design time dominates one-off quotes. For repeat prints of the same design:
- Set `design_minutes: 0` after the first run
- The coin preset with 3hr design = $92.91 floor (one-off)
- Same coin, no design time = ~$8-10 floor (repeat batch)

## JSON schema

```json
{
  "job_type": "functional_custom_part",
  "piece_name": "my part",
  "quantity": 1,
  "material": {
    "spool_cost_usd": 22.0,
    "spool_weight_g": 1000,
    "part_weight_g": 20,
    "support_weight_g": 0,
    "waste_buffer_pct": 10
  },
  "print": {
    "print_time_hours": 1.0,
    "machine_power_w": 180,
    "electricity_rate_per_kwh": 0.13
  },
  "machine": {
    "purchase_price_usd": 399.0,
    "lifespan_hours": 5000,
    "maintenance_rate_per_hour": 0.10
  },
  "labor": {
    "prep_minutes": 10,
    "postprocess_minutes": 10,
    "design_minutes": 0,
    "hourly_rate_usd": 20.0
  },
  "extras": {
    "hardware_cost_usd": 0.0,
    "packaging_cost_usd": 0.50,
    "shipping_cost_usd": 0.0
  },
  "risk": {
    "success_rate": 0.92,
    "minimum_margin_pct": 0.30
  },
  "market": {
    "comparables": [
      {"price_usd": 15.00, "similarity": 0.85}
    ],
    "local_multiplier": 1.0,
    "customization_premium_pct": 0.10,
    "rush_premium_pct": 0.0
  }
}
```
