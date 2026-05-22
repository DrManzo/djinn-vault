#!/usr/bin/env python3
"""Djinn Printer Telegram Bot — runs on Typhon (always-on)."""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime

import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

MOONRAKER_URL = os.environ.get("MOONRAKER_URL", "http://192.168.1.114:7125")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    log.error("TELEGRAM_BOT_TOKEN not set")
    sys.exit(1)

headers = {"X-Api-Key": os.environ.get("MOONRAKER_API_KEY", "")}


async def moonraker_get(path: str) -> dict:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f"{MOONRAKER_URL}{path}", timeout=10) as resp:
            return await resp.json()


async def moonraker_post(path: str, data: dict = None) -> dict:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            f"{MOONRAKER_URL}{path}", json=data or {}, timeout=10
        ) as resp:
            return await resp.json()


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🖨️ Djinn Printer Bot active\n\n"
        "/print &lt;filename&gt; — Start print\n"
        "/print_status — Current status\n"
        "/print_cancel — Cancel print\n"
        "/print_queue — List files\n"
        "/print_log — Last 5 jobs"
    )


async def handle_print(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /print <filename.gcode>")
        return
    filename = context.args[0]
    if not filename.endswith(".gcode"):
        filename += ".gcode"

    try:
        result = await moonraker_post(
            "/printer/print/start", {"filename": filename}
        )
        if "error" in result:
            msg = result["error"].get("message", str(result["error"]))
            await update.message.reply_text(f"❌ {msg}")
        else:
            await update.message.reply_text(f"🖨️ Started: {filename}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await moonraker_get("/printer/objects/query?print_stats&extruder&heater_bed")
        stats = data["result"]["status"]
        ps = stats["print_stats"]

        dur_min = int(ps.get("print_duration", 0) // 60)
        remaining = int(ps.get("total_duration", 0) // 60)
        filament = ps.get("filament_used", 0) / 1000

        ext = stats.get("extruder", {})
        bed = stats.get("heater_bed", {})

        lines = [
            f"🖨️ State: {ps.get('state', '?')}",
            f"File: {ps.get('filename', 'none')}",
            f"Duration: {dur_min}m / ~{remaining}m",
            f"Filament: {filament:.1f}m",
            f"Nozzle: {ext.get('temperature', '?'):.0f}°C (target {ext.get('target', '?'):.0f}°C)",
            f"Bed: {bed.get('temperature', '?'):.0f}°C (target {bed.get('target', '?'):.0f}°C)",
        ]
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"❌ Status failed: {e}")


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await moonraker_post("/printer/print/cancel")
        await update.message.reply_text("⏹️ Print cancelled")
    except Exception as e:
        await update.message.reply_text(f"❌ Cancel failed: {e}")


async def handle_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await moonraker_get("/server/files/list?root=gcodes")
        files = data.get("result", [])
        lines = ["📂 Available gcodes:"]
        for f in sorted(files, key=lambda x: x["path"]):
            size_mb = f.get("size", 0) / 1_000_000
            lines.append(f"  • {os.path.basename(f['path'])} ({size_mb:.0f}MB)")
        msg = "\n".join(lines) if len(lines) > 1 else "No files found"
        # Telegram 4096 char limit
        if len(msg) > 4000:
            msg = msg[:4000] + "\n... (truncated)"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Queue failed: {e}")


async def handle_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await moonraker_get("/server/history/list?limit=5")
        entries = data.get("result", {}).get("jobs", [])
        if not entries:
            await update.message.reply_text("No job history")
            return
        lines = ["📋 Last 5 jobs:"]
        for j in entries:
            name = os.path.basename(j.get("filename", "?"))
            state = j.get("status", "?")
            dur = int(j.get("print_duration", 0) // 60)
            lines.append(f"  • {name} — {state} ({dur}m)")
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"❌ Log failed: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("help", handle_start))
    app.add_handler(CommandHandler("print", handle_print))
    app.add_handler(CommandHandler("print_status", handle_status))
    app.add_handler(CommandHandler("print_cancel", handle_cancel))
    app.add_handler(CommandHandler("print_queue", handle_queue))
    app.add_handler(CommandHandler("print_log", handle_log))

    log.info("Djinn Printer Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
