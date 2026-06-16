"""
TASK-075–079 — djinn-personal-gateway command handlers (Phase Beta)

Wire these into the existing python-telegram-bot handler registration
in your djinn-personal-gateway/bot.py.

Usage pattern:
    from djinn.personal.gateway_handlers import register_handlers
    register_handlers(application)

All handlers follow the existing Phase Alpha pattern:
    async def handler(update, context) -> None
"""

from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes

from .modules.deadlines import (
    add_deadline, get_weekly_view, complete_deadline,
    get_lsat_status, log_lsat_session, set_lsat_goal,
)
from .modules.blackbook import log_entry, can_reflect, get_reflect_prompt_via_ollama
from .modules.flare import set_flare, clear_flare, log_weight, get_health_summary
from .modules.recovery import (
    step_status, start_step, advance_step,
    log_sponsor_contact, log_craving, craving_week_pattern,
    log_meeting, meetings_week,
)
from .modules.creative import (
    log_writing_session, get_aethoria_status, set_aethoria_goal, log_gym,
)


# ── TASK-075: Academic Deadlines ─────────────────────────────────────

async def school_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show full 7-day academic view."""
    await update.message.reply_text(get_weekly_view(), parse_mode="Markdown")


async def deadline_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /deadline add COURSE "Task label" YYYY-MM-DD
    /deadline done ID
    """
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage:\n"
            "/deadline add COURSE \"label\" YYYY-MM-DD\n"
            "/deadline done ID"
        )
        return

    sub = args[0].lower()
    if sub == "add" and len(args) >= 4:
        course, label, due = args[1], " ".join(args[2:-1]), args[-1]
        await update.message.reply_text(add_deadline(course, label, due))
    elif sub == "done" and len(args) == 2:
        try:
            await update.message.reply_text(complete_deadline(int(args[1])))
        except ValueError:
            await update.message.reply_text("ID must be a number.")
    else:
        await update.message.reply_text("Usage: /deadline add COURSE \"label\" YYYY-MM-DD  or  /deadline done ID")


async def lsat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /lsat              — status
    /lsat done LR      — log session by section type
    /lsat goal text    — set week goal
    """
    args = context.args
    if not args:
        await update.message.reply_text(get_lsat_status(), parse_mode="Markdown")
        return
    sub = args[0].lower()
    if sub == "done" and len(args) >= 2:
        await update.message.reply_text(log_lsat_session(args[1], " ".join(args[2:])))
    elif sub == "goal" and len(args) >= 2:
        await update.message.reply_text(set_lsat_goal(" ".join(args[1:])))
    else:
        await update.message.reply_text(get_lsat_status(), parse_mode="Markdown")


# ── TASK-076: Black Book ─────────────────────────────────────────────

async def log_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /log text          — immediate capture, no friction
    /log               — prompts "What's on your mind?"
    """
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("What's on your mind?")
        return
    await update.message.reply_text(log_entry(text))


async def reflect_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gated at 3+ entries. Uses local Ollama only."""
    await update.message.reply_text(get_reflect_prompt_via_ollama())


# ── TASK-077: Flare Flag ─────────────────────────────────────────────

async def flare_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /flare             — flag flare day
    /flare clear       — clear flag
    """
    args = context.args
    if args and args[0].lower() == "clear":
        await update.message.reply_text(clear_flare())
    else:
        note = " ".join(args) if args else ""
        await update.message.reply_text(set_flare(note))


async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show health summary (weight, flare count)."""
    await update.message.reply_text(get_health_summary())


async def weight_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /weight 238.5
    """
    if not context.args:
        await update.message.reply_text("Usage: /weight 238.5")
        return
    try:
        lbs = float(context.args[0])
        await update.message.reply_text(log_weight(lbs))
    except ValueError:
        await update.message.reply_text("Weight must be a number. e.g. /weight 238.5")


# ── TASK-078: Recovery Cluster ───────────────────────────────────────

async def step_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /step              — current status
    /step start N      — start step N
    /step done         — advance to next step
    """
    args = context.args
    if not args:
        await update.message.reply_text(step_status())
        return
    sub = args[0].lower()
    if sub == "done":
        await update.message.reply_text(advance_step())
    elif sub == "start" and len(args) == 2:
        try:
            await update.message.reply_text(start_step(int(args[1])))
        except ValueError:
            await update.message.reply_text("Usage: /step start 1")
    else:
        await update.message.reply_text(step_status())


async def sponsor_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /sponsor-contact [optional note]
    """
    note = " ".join(context.args) if context.args else ""
    await update.message.reply_text(log_sponsor_contact(note))


async def craving_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /craving 7 work-stress   — log severity + tag
    /craving week            — Ollama pattern analysis (local only)
    """
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /craving [1-10] [optional tag]  or  /craving week")
        return
    if args[0].lower() == "week":
        await update.message.reply_text(craving_week_pattern())
        return
    try:
        severity = int(args[0])
        tag = " ".join(args[1:]) if len(args) > 1 else ""
        await update.message.reply_text(log_craving(severity, tag))
    except ValueError:
        await update.message.reply_text("Severity must be 1–10. e.g. /craving 6 evening")


async def meeting_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /meeting attended [name]  — log attended
    /meeting missed           — log missed
    /meeting week             — show week attendance
    """
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /meeting attended | missed | week")
        return
    sub = args[0].lower()
    if sub == "attended":
        name = " ".join(args[1:]) if len(args) > 1 else ""
        await update.message.reply_text(log_meeting(attended=True, name=name))
    elif sub == "missed":
        await update.message.reply_text(log_meeting(attended=False))
    elif sub == "week":
        await update.message.reply_text(meetings_week(), parse_mode="Markdown")
    else:
        await update.message.reply_text("Usage: /meeting attended | missed | week")


# ── TASK-079: Creative + Gym ─────────────────────────────────────────

async def write_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /write 30             — log 30-minute session
    /write 45 scene note  — log with scene note
    """
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /write [minutes] [optional scene note]")
        return
    try:
        minutes = int(args[0])
        note = " ".join(args[1:]) if len(args) > 1 else ""
        await update.message.reply_text(log_writing_session(minutes, note))
    except ValueError:
        await update.message.reply_text("Minutes must be a number. e.g. /write 30")


async def aethoria_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Aethoria streak + weekly status."""
    await update.message.reply_text(get_aethoria_status(), parse_mode="Markdown")


async def aethoria_goal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /aethoria-goal finish chapter 3 draft
    """
    if not context.args:
        await update.message.reply_text("Usage: /aethoria-goal [your goal for the week]")
        return
    await update.message.reply_text(set_aethoria_goal(" ".join(context.args)))


async def gym_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log today's trainer session."""
    await update.message.reply_text(log_gym())


# ── Registration ─────────────────────────────────────────────────────

def register_handlers(application: Application) -> None:
    """Call this from your bot.py after creating the Application."""
    # Academic
    application.add_handler(CommandHandler("school", school_cmd))
    application.add_handler(CommandHandler("deadline", deadline_cmd))
    application.add_handler(CommandHandler("lsat", lsat_cmd))

    # Black Book
    application.add_handler(CommandHandler("log", log_cmd))
    application.add_handler(CommandHandler("reflect", reflect_cmd))

    # Health
    application.add_handler(CommandHandler("flare", flare_cmd))
    application.add_handler(CommandHandler("health", health_cmd))
    application.add_handler(CommandHandler("weight", weight_cmd))

    # Recovery
    application.add_handler(CommandHandler("step", step_cmd))
    application.add_handler(CommandHandler("sponsor_contact", sponsor_cmd))
    application.add_handler(CommandHandler("craving", craving_cmd))
    application.add_handler(CommandHandler("meeting", meeting_cmd))

    # Creative + Gym
    application.add_handler(CommandHandler("write", write_cmd))
    application.add_handler(CommandHandler("aethoria", aethoria_cmd))
    application.add_handler(CommandHandler("aethoria_goal", aethoria_goal_cmd))
    application.add_handler(CommandHandler("gym", gym_cmd))
