# TASK: forge-slicer GLIBC Fix

**Date:** 2026-06-14  
**Reported by:** Javier  
**Status:** Fix committed — pending validation by Marcus

---

## Symptom

`djinn-model-slice 3` fails. Container runs, entrypoint executes, `CrealityPrint` binary exits with code 127. Empty stderr.

---

## Root Cause

The Dockerfile used `FROM ubuntu:22.04` (GLIBC 2.35). The extracted `CrealityPrint` v7.1.1 AppImage binary requires **GLIBC 2.38** and **GLIBCXX 3.4.32** (GCC 13 libstdc++).

`ldd` output from the container:
```
CrealityPrint: /lib/x86_64-linux-gnu/libm.so.6: version `GLIBC_2.38' not found
CrealityPrint: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.38' not found
CrealityPrint: /lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.32' not found
```

Exit code 127 is the dynamic linker's failure code — the binary loads but its required symbol versions are absent, so the OS refuses to execute it.

Host (Salomon) runs GLIBC 2.43 — no mismatch on host. Only inside the container.

---

## Fix

### Base image bump: ubuntu:22.04 → ubuntu:24.04

| Distro | GLIBC | GCC/libstdc++ | Status |
|---|---|---|---|
| Ubuntu 22.04 | 2.35 | GCC 11 (GLIBCXX 3.4.29) | ❌ too old |
| Ubuntu 24.04 | 2.39 | GCC 13 (GLIBCXX 3.4.32) | ✅ satisfies requirement |
| Ubuntu 25.04 | 2.41 | GCC 14 | ✅ works but edge/newer |

Ubuntu 24.04 LTS is the minimal sufficient bump. It ships GLIBC 2.39 and GCC 13's libstdc++ (GLIBCXX 3.4.32), which satisfies both linker requirements.

### Package renames on 24.04

Two packages changed names in 24.04 due to the `t64` ABI transition (time_t 64-bit migration):

| 22.04 name | 24.04 name | Reason |
|---|---|---|
| `libfuse2` | `libfuse2t64` | t64 ABI transition |
| `libasound2` | `libasound2t64` | t64 ABI transition |

All other package names (`xvfb`, `libgl1`, `libxcb-*`, etc.) are unchanged and install cleanly on 24.04.

`libstdc++6` is added explicitly to ensure the GCC 13 runtime is present (it is usually a dependency of other packages but making it explicit prevents version ambiguity).

### Corrected Dockerfile diff

```diff
-FROM ubuntu:22.04
+FROM ubuntu:24.04
 
 ...
 
-    libfuse2 \
+    libfuse2t64 \
 
-    libasound2 \
+    libasound2t64 \
 
+    libstdc++6 \
```

Full corrected Dockerfile committed at:
`djinn/printer/forge-slicer/Dockerfile`

---

## Rebuild & Verify

```bash
# 1. Rebuild
docker build -t forge-slicer:latest ~/Obsidian/djinn/printer/forge-slicer/

# 2. Quick linker check — should print entrypoint help, NOT exit 127
docker run --rm forge-slicer --help

# 3. ldd sanity check inside container
docker run --rm --entrypoint ldd forge-slicer \
    /opt/creality-print/bin/CrealityPrint | grep -E "not found|GLIBC"
# Expected: no output (all symbols resolved)

# 4. Smoke test
bash ~/Obsidian/djinn/printer/forge-slicer/slice.sh \
    ~/printer-files/queue/plate_job3.stl proto pla | python3 -m json.tool
# Expected: {"success": true, "filament_g": ..., "print_time_s": ...}

# 5. Full pipeline
djinn-model-slice 3
```

---

## If ldd Still Shows Missing Symbols

If after the 24.04 bump the AppImage's *bundled* libstdc++ inside `/opt/creality-print/` is older than the system's, the AppImage may load the wrong one. Try forcing system libs:

```bash
# Inside the container, check which libstdc++ AppRun picks up:
docker run --rm --entrypoint ldd forge-slicer /opt/creality-print/AppRun | grep stdc

# If it points to a bundled old one, override at runtime:
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```

Add that `ENV` line to the Dockerfile if needed and rebuild.

---

## Files Changed

- `djinn/printer/forge-slicer/Dockerfile` — base image bump + package renames
- `djinn/research/marcus/TASK-forge-slicer-glibc-fix.md` — this file

**entrypoint.py, slice.sh, build.sh, and all profiles: untouched.**

---

*Fix by Marcus (Perplexity) — 2026-06-14*
