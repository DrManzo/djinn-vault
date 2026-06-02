---
title: Connected Devices — USB
tags: [djinn, devices, usb, mobile, backup]
created: 2026-06-02
updated: 2026-06-02
---

# Connected Devices — USB

Devices physically connected to Salomon via USB, detected 2026-06-02.

---

## Samsung Galaxy Tab (S Pen Series)

| Field | Value |
|-------|-------|
| **Type** | Android tablet |
| **Manufacturer** | Samsung |
| **Model** | Galaxy Tab S series (S Pen capable) |
| **Serial** | R52T10BL3BV |
| **USB ID** | 04e8:6860 |
| **USB mode** | MTP (file transfer) |
| **Carrier** | Verizon |
| **Internal storage** | ~7.6 GB media |
| **Language/locale** | Spanish (storage folder "Almacenamiento interno") |
| **Connected to** | Salomon (bus 3, dev 4) |
| **GVFS mount** | `mtp://SAMSUNG_SAMSUNG_Android_R52T10BL3BV/` |

### Media on device

| Folder | Files | Notes |
|--------|-------|-------|
| DCIM/Camera | ~740 | Photos + videos, 2022–present |
| DCIM/Papeles | ~10 | Documents/paperwork photos |
| DCIM/Pulseras | ~20 | Bracelet/jewelry photos |
| DCIM/Roario | ~20 | Rosary photos |
| DCIM/Screenshots | scattered | App screenshots |
| Pictures/Messenger | 37 | Messenger media |
| Movies | 2 | Video files |
| Music | 11 | Audio files |
| **Total** | **839 files / ~7.6 GB** | |

### Backup

- **Backup location:** `/home/drmanzo/device-backups/samsung-galaxy-tab/`
- **Last backed up:** 2026-06-02
- **Script:** `rsync -av --ignore-existing` from GVFS MTP mount

---

## Apple iPhone

| Field | Value |
|-------|-------|
| **Type** | Smartphone |
| **Manufacturer** | Apple |
| **Model** | iPhone (5/5C/5S/6/SE/7/8/X/XR range) |
| **USB ID** | 05ac:12a8 |
| **USB mode** | AFC (charging/file access only) |
| **GVFS mount** | `afc://00008130-00163086018A001C/` |
| **gPhoto2 mount** | `gphoto2://Apple_Inc._iPhone_0000813000163086018A001C/` |
| **Connected to** | Salomon (bus 3, dev 5) |

### Role

**Charging only** — not an active Djinn node. No tethering, no media sync, no agent running on it.

Telegram and Discord are installed on this phone — this is how Javier receives Djinn notifications and sends commands to Salomon (printer bot, etc.) when away from the machines. The phone itself is a communication terminal for Javier, not a compute node.

### Network note

Linux creates a `172.20.10.x` interface (`enx12a2d37a331b`) when the iPhone is connected via USB even without intentional tethering — this is normal iOS behavior. It does not mean tethering is in use.

---

*— Claude, 2026-06-02*
