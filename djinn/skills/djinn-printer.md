# Skill: djinn-printer

**Owner:** Salomon (proxies through Typhon's network reach to printer)
**Purpose:** Control Ender-3 V3 Plus via Moonraker API through Telegram commands
**Status:** ⏳ Pending — awaiting printer WiFi setup

## Triggers

- Telegram: `/print`, `/print_status`, `/print_cancel`, `/print_queue`, `/print_log`
- Manual: `~/.local/bin/djinn-print <command>`

## Inputs

- `~/.config/djinn/printer.conf` — `PRINTER_IP=<ip>`
- Moonraker API at `http://<PRINTER_IP>:7125`
- `~/Obsidian/djinn/printer/queue/` — pending jobs
- `~/Obsidian/djinn/printer/active/` — current job
- `~/Obsidian/djinn/printer/completed/` — history

## Steps

See `workflows/printer.md` for full command logic.

## Outputs

- Job notes in `djinn/printer/{queue,active,completed}/`
- Telegram replies confirming action taken

## Dependencies

- `~/.local/bin/djinn-print`
- `~/.config/djinn/printer.conf` with `PRINTER_IP` set
- Printer on local WiFi, Moonraker accessible at port 7125

## Hardware Checklist (one-time setup)

- [ ] Connect Ender-3 V3 Plus to local WiFi (touchscreen → Settings → Network)
- [ ] Note printer IP, add to `~/.config/djinn/printer.conf` on Salomon + Typhon
- [ ] Test: `curl http://<ip>:7125/printer/objects/query?print_stats`
- [ ] Build enclosure before first print — bed 60-100°C, cats present
- [ ] Buy: flush cutters, 0.4mm nozzle pack, IPA 90%+
