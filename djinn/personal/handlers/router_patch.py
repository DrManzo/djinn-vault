"""
Router Patch — Phase Beta command bindings for djinn-personal-gateway.
Drop this into your existing Telegram bot handler's dispatch block.
All commands route to the Phase Beta handlers.

Example integration:
    from djinn.personal.handlers.router_patch import dispatch
    result = dispatch(command, args, ollama_client)
    await message.reply(result)
"""
from . import (
    cmd_school, cmd_deadline_add, cmd_deadline_done, cmd_lsat,
    cmd_log, cmd_reflect,
    cmd_flare, cmd_weight,
    cmd_step, cmd_sponsor_contact, cmd_craving, cmd_meeting,
    cmd_write, cmd_aethoria, cmd_aethoria_goal, cmd_gym,
)


def dispatch(command: str, args: list[str], ollama_client=None) -> str:
    """
    Central dispatch for all Phase Beta PA commands.
    command: the command string without leading slash, e.g. 'log', 'craving'
    args:    remaining tokens after the command
    """
    match command:
        # Academic
        case "school":
            return cmd_school()
        case "deadline":
            if args and args[0] == "add" and len(args) >= 4:
                return cmd_deadline_add(args[1], args[2], args[3])
            if args and args[0] == "done" and len(args) >= 3:
                return cmd_deadline_done(args[1], args[2])
            return "Usage: /deadline add [course] [task] [date] | /deadline done [course] [task]"
        case "lsat":
            return cmd_lsat(args)

        # Black Book
        case "log":
            text = " ".join(args) if args else None
            return cmd_log(text)
        case "reflect":
            return cmd_reflect(ollama_client)

        # Health
        case "flare":
            return cmd_flare(args)
        case "weight":
            return cmd_weight(args)

        # Recovery
        case "step":
            return cmd_step(args)
        case "sponsor" | "sponsor-contact":
            note = " ".join(args)
            return cmd_sponsor_contact(note)
        case "craving":
            return cmd_craving(args, ollama_client)
        case "meeting":
            return cmd_meeting(args)

        # Creative + Physical
        case "write":
            return cmd_write(args)
        case "aethoria":
            return cmd_aethoria(args)
        case "aethoria-goal":
            return cmd_aethoria_goal(" ".join(args))
        case "gym":
            return cmd_gym()

        case _:
            return f"Unknown command: /{command}"
