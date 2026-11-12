# ═══════════════════════════════════════════════════════════════
# main.py — LALA DIGITAL  |  TCP BOT
# © 2026 LALA DIGITAL — All rights reserved
# ═══════════════════════════════════════════════════════════════

import asyncio
import time
import sys
import os
import json
import datetime
from cfonts import render

import login_engine
import bot_core

from bot_core import (
    TcPOnLine, TcPChaT,
    build_ob55_online_auth, create_auth_token_chat,
    bot_uid, ToKen, region
)
import random

# --- EXPIRY CHECK (Until November 30, 2026) ---
# Timestamp for 2026-11-30 23:59:59 (Bangladesh Time / UTC+6)
EXPIRE_TS = 1796035199.0 
EXPIRE_STR = "2026-11-30 23:59:59"

_now = time.time()
if _now > EXPIRE_TS:
    print("=" * 50)
    print("❌ This script has EXPIRED.")
    print(f"   Expired at : {EXPIRE_STR}")
    print(f"   Current    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    sys.exit(1)


# Login credentials are stored separately in uid-pass-svr.json
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uid-pass-svr.json")


def load_login_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        raise RuntimeError("uid-pass-svr.json file not found.")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in uid-pass-svr.json: {exc}")

    uid = str(config.get("uid", "")).strip()
    password = str(config.get("pass", "")).strip()
    region_value = str(config.get("region", "")).strip()

    if not uid or not password or not region_value:
        raise RuntimeError("uid-pass-svr.json must contain non-empty uid, pass and region fields.")

    return uid, password, region_value


def log(level, message):
    icons = {
        "INFO":  ("\033[1;36m", "ℹ"),
        "OK":    ("\033[1;32m", "✔"),
        "WAIT":  ("\033[1;33m", "⏳"),
        "WARN":  ("\033[1;33m", "⚠"),
        "ERROR": ("\033[1;31m", "✘"),
        "BOT":   ("\033[1;35m", "★"),
    }
    color, icon = icons.get(level, ("\033[1;37m", "•"))
    reset = "\033[0m"
    ts = time.strftime("%H:%M:%S")
    print(f"\033[1;90m[{ts}]{reset} {color}{icon} {level:<5}{reset} │ {message}")


def print_banner():
    """Display LALA DIGITAL in large letters with brief information below."""
    os.system("clear")
    print()
    print(render("LALA", colors=["red", "white"], align="center"))
    print(render("DIGITAL", colors=["yellow", "white"], align="center"))
    print()
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print(f"\033[1;33m{'TCP BOT  •  PREMIUM'.center(60)}\033[0m")
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print(f"\033[1;37m{'EVO  •  TEAM  •  MATCH  •  ONLINE'.center(60)}\033[0m")
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print(f"\033[1;36m{'© LALA DIGITAL PREMIUM'.center(60)}\033[0m")
    print(f"\033[1;35m{'═' * 60}\033[0m")
    print()


def print_box(title, lines, color="\033[1;35m"):
    width = 58
    reset = "\033[0m"
    print(f"\n{color}┌{'─' * width}┐{reset}")
    print(f"{color}│{reset} {title.center(width - 1)}{color}│{reset}")
    print(f"{color}├{'─' * width}┤{reset}")
    for line in lines:
        print(f"{color}│{reset} {line:<{width - 1}}{color}│{reset}")
    print(f"{color}└{'─' * width}┘{reset}")


def print_line(title, value, icon="➤"):
    print(f"  {icon} \033[1;36m{title:<14}\033[0m : \033[1;33m{value}\033[0m")


async def MaiiiinE():
    global bot_uid, ToKen, region

    print_banner()
    try:
        Uid, Pw, REGION_PREF = load_login_config()
    except RuntimeError as e:
        log("ERROR", str(e))
        return

    log("INFO", "Login process is starting...")
    log("INFO", f"Target region: {REGION_PREF}")

    try:
        result = await login_engine.do_login(Uid, Pw, REGION_PREF)
    except Exception as e:
        log("ERROR", f"Login error: {e}")
        return

    if not result:
        log("ERROR", "Login failed.")
        await asyncio.sleep(10)
        return

    bot_core.bot_uid = result["bot_uid"]
    bot_core.ToKen = result["token"]
    bot_core.region = result["region"]

    key         = result["key"]
    iv          = result["iv"]
    timestamp   = result["timestamp"]
    online_ip   = result["online_ip"]
    online_port = result["online_port"]
    chat_ip     = result["chat_ip"]
    chat_port   = result["chat_port"]
    acc_name    = result["account_name"]
    clan_id     = result.get("clan_id")
    clan_data   = result.get("clan_data")

    os.system("clear")

    RESET  = "\033[0m"
    CYAN   = "\033[1;36m"
    GREEN  = "\033[1;32m"
    PURPLE = "\033[1;35m"

    # ── Display only your name in large letters ──
    print()
    print(render("LALA", colors=["red", "white"], align="center"))
    print(render("DIGITAL", colors=["yellow", "white"], align="center"))
    print()
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print(f"\033[1;33m{'BOT ONLINE'.center(60)}\033[0m")
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print()

    print_box("ACCOUNT INFORMATION", [
        f"UID          : {result['bot_uid']}",
        f"NAME         : {acc_name}",
        f"REGION       : {result['region']}",
        f"CLAN ID      : {clan_id or 'None'}",
        f"CHAT SERVER  : {chat_ip}:{chat_port}",
        f"GAME SERVER  : {online_ip}:{online_port}",
    ], GREEN)

    print_box("BOT STATUS", [
        "LOGIN SUCCESSFUL",
        "AUTHENTICATION READY",
        "TCP CONNECTION INITIALIZING",
    ], PURPLE)

    log("INFO", "Generating authentication token...")

    ChatAutH = create_auth_token_chat(
        int(result["bot_uid"]), result["token"],
        int(timestamp), key, iv
    )
    OnlineAutH, _ = build_ob55_online_auth(
        int(result["bot_uid"]), result["token"],
        int(timestamp), key, iv
    )

    log("OK", "Authentication token ready.")
    log("WAIT", "Connecting to chat server...")

    ready_event = asyncio.Event()
    t1 = asyncio.create_task(
        TcPChaT(
            chat_ip, chat_port, ChatAutH, key, iv,
            ready_event, result["region"],
            clan_id=clan_id,
            clan_data=clan_data,
        )
    )

    await ready_event.wait()
    log("OK", "Chat server connected successfully.")
    await asyncio.sleep(1)

    log("WAIT", "Connecting to online server...")
    t2 = asyncio.create_task(
        TcPOnLine(online_ip, online_port, key, iv, OnlineAutH)
    )

    print()
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print(render("LALA", colors=["red", "white"], align="center"))
    print(render("DIGITAL", colors=["yellow", "white"], align="center"))
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print_line("Owner",   "MR LALA")
    print_line("Region",  result['region'])
    print_line("Bot UID", result['bot_uid'])
    print_line("Name",    acc_name)
    print_line("Clan",    str(clan_id) if clan_id else "None")
    print_line("Status",  "\033[1;32m● RUNNING\033[0m")
    print(f"{PURPLE}{'═' * 60}{RESET}")
    print()

    await asyncio.gather(t1, t2)


async def StarTinG():
    attempt = 0
    while True:
        # Check expiry continuously on every restart attempt
        if time.time() > EXPIRE_TS:
            log("ERROR", "Script expiration date reached. Stopping bot.")
            sys.exit(1)
            
        attempt += 1
        try:
            log("BOT", f"Starting session #{attempt}")
            # Extended session timeout to 24 hours per session (24 * 60 * 60)
            await asyncio.wait_for(MaiiiinE(), timeout=24 * 60 * 60)
        except asyncio.TimeoutError:
            log("WARN", "Session ended. Restarting...")
            await asyncio.sleep(3)
        except KeyboardInterrupt:
            log("WARN", "Bot has been stopped.")
            sys.exit(0)
        except Exception as e:
            log("ERROR", f"Error: {e}")
            await asyncio.sleep(5)


if __name__ == '__main__':
    try:
        asyncio.run(StarTinG())
    except KeyboardInterrupt:
        print("\nBot has been stopped.")
