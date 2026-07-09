FROM ubuntu:25.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV MESA_GL_VERSION_OVERRIDE=4.5

# ── System dependencies ────────────────────────────────────────────────────────
# Notes on 24.04 → 25.04 package changes:
#   - libfuse2t64, libasound2t64 carry forward unchanged on 25.04
#   - t64 ABI transition packages (libfuse2t64, libasound2t64, etc.) are stable
#   - fontconfig 2.17.1+ required to avoid font-related segfault in CrealityPrint
#   - All other package names are unchanged from 24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libfuse2t64 \
    libgl1 \
    libgl1-mesa-dri \
    libglib2.0-0 \
    libdbus-1-3 \
    libnss3 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxrandr2 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxss1 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-util1 \
    libasound2t64 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libstdc++6 \
    libatomic1 \
    libdeflate0 \
    liblerc4 \
    libmspack0t64 \
    libegl1 \
    libopengl0 \
    libcairo-gobject2 \
    libgtk-3-0t64 \
    libgdk-pixbuf-2.0-0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libjavascriptcoregtk-4.1-0 \
    libopus0 \
    libsecret-1-0 \
    libsoup-3.0-0 \
    libspeexdsp1 \
    libsrtp2-1 \
    libusrsctp2 \
    libwayland-client0 \
    libwayland-cursor0 \
    libwayland-egl1 \
    libwayland-server0 \
    libwebkit2gtk-4.1-0 \
    libx264-164 \
    python3 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Download and extract Creality Print AppImage ───────────────────────────────
WORKDIR /tmp
RUN curl -L \
    "https://github.com/CrealityOfficial/CrealityPrint/releases/download/v7.1.1/CrealityPrint-V7.1.1.4472-x86_64-Release.AppImage" \
    -o CrealityPrint.AppImage \
    && chmod +x CrealityPrint.AppImage

# Extract AppImage to avoid FUSE requirement inside Docker
RUN ./CrealityPrint.AppImage --appimage-extract \
    && mv squashfs-root /opt/creality-print \
    && rm CrealityPrint.AppImage

# ── Replace system libfontconfig with host version ────────────────────────────
# Ubuntu 25.04 ships fontconfig 2.15.0, but CrealityPrint crashes (SIGSEGV at
# null ptr) with any fontconfig < 2.17.1. Copy the host's 2.17.1 lib in.
COPY libfontconfig.so.1.16.1 /lib/x86_64-linux-gnu/libfontconfig.so.1

# ── App setup ──────────────────────────────────────────────────────────────────
WORKDIR /app

# Copy entrypoint
COPY entrypoint.py /app/entrypoint.py

# Output dir
RUN mkdir -p /output /input /profiles
# CrealityPrint writes crash dumps to /tmp/ then renames to /log/.
# Symlink so rename is on the same filesystem.
RUN ln -sf /tmp /log

ENTRYPOINT ["python3", "/app/entrypoint.py"]
