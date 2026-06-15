FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV MESA_GL_VERSION_OVERRIDE=4.5

# ── System dependencies ────────────────────────────────────────────────────────
# Notes on 22.04 → 24.04 package changes:
#   - libfuse2 is now libfuse2t64 on 24.04 (transitional rename)
#   - libasound2 is now libasound2t64 on 24.04 (transitional rename)
#   - libxss1 dropped from Ubuntu 24.04 main; replaced by libxss1 in universe
#     (still installable, just needs universe — enabled by default on 24.04)
#   - libxcb-util1 renamed to libxcb-util1 (same, still present)
#   - All other package names are unchanged
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

# ── App setup ──────────────────────────────────────────────────────────────────
WORKDIR /app

# Copy entrypoint
COPY entrypoint.py /app/entrypoint.py

# Output dir
RUN mkdir -p /output /input /profiles

ENTRYPOINT ["python3", "/app/entrypoint.py"]
