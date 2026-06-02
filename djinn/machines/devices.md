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
| **USB mode** | AFC (Apple File Conduit) + tethering |
| **GVFS mount** | `afc://00008130-00163086018A001C/` |
| **gPhoto2 mount** | `gphoto2://Apple_Inc._iPhone_0000813000163086018A001C/` |
| **Connected to** | Salomon (bus 3, dev 5) |

### Network via tethering

When USB tethering is active on the iPhone:

| Field | Value |
|-------|-------|
| **Interface** | `enx12a2d37a331b` (Salomon) |
| **Salomon IP** | `172.20.10.3/28` |
| **iPhone gateway IP** | `172.20.10.1` |
| **Subnet** | `172.20.10.0/28` |
| **Provides** | Cellular internet to Salomon |

### Notes

- iPhone is currently providing cellular data via USB tether (active as of 2026-06-02)
- AFC mount allows direct file access (photos, etc.) if needed
- Media backup not yet run — use `ifuse` or `gphoto2` if needed

---

*— Claude, 2026-06-02*
