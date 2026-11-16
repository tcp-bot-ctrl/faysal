# ═══════════════════════════════════════════════════════════════
# license_guard.py — LALA DIGITAL key check (stdlib only, no pip)
# ═══════════════════════════════════════════════════════════════
import os
import sys
import json
import time
import uuid
import asyncio
import hashlib
import subprocess
import webbrowser
import urllib.request
import urllib.error

# ── CHANGE THESE TWO ──────────────────────────────────────────
API_URL  = "https://round-field-88c9.porigaming50.workers.dev"   # Cloudflare Worker URL
KEY_PAGE = "https://tcpkey.netlify.app"
       # GitHub Pages URL
# ──────────────────────────────────────────────────────────────

DEVICE_FILE = os.path.join(os.path.expanduser("~"), ".lala_device")
RECHECK_EVERY = 300  # seconds

C = "\033[1;36m"; G = "\033[1;32m"; Y = "\033[1;33m"; R = "\033[1;31m"; P = "\033[1;35m"; X = "\033[0m"

MESSAGES = {
    "invalid_key":   "Invalid key. Check it and try again.",
    "used_by_other": "This key is already used on another device.",
    "expired":       "This key has expired. Generate a new one.",
    "bad_json":      "Invalid request.",
}


def device_id():
    try:
        with open(DEVICE_FILE, "r") as f:
            raw = f.read().strip()
    except OSError:
        raw = ""
    if not raw:
        raw = uuid.uuid4().hex
        try:
            with open(DEVICE_FILE, "w") as f:
                f.write(raw)
        except OSError:
            pass
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _post(path, data, timeout=15):
    """Returns dict, or None on network error."""
    req = urllib.request.Request(
        API_URL + path,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "lala-bot/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except Exception:
            return {"ok": False, "error": f"http_{e.code}"}
    except Exception:
        return None


def open_key_page():
    print(f"\n{C}Opening key page:{X} {KEY_PAGE}")
    # সুপার ফাস্ট ওপেন করার জন্য নেটিভ অ্যান্ড্রয়েড am start কমান্ড ব্যবহার করা হয়েছে
    try:
        subprocess.Popen(
            ["am", "start", "-a", "android.intent.action.VIEW", "-d", KEY_PAGE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        try:
            webbrowser.open(KEY_PAGE)
        except Exception:
            print(f"{Y}Could not open a browser. Open the link above manually.{X}")


def _fmt(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m:02d}m {s:02d}s"


def require_license():
    """Blocks until a valid key is entered. Returns (remaining_seconds, key)."""
    print(f"\n{P}{'═' * 50}{X}")
    print(f"{Y}{'LALA DIGITAL — KEY REQUIRED'.center(50)}{X}")
    print(f"{P}{'═' * 50}{X}\n")

    dev = device_id()
    env_key = os.environ.get("LALA_KEY", "").strip()

    if not env_key:
        while True:
            ans = input(f"{C}Do you have a key? (Y/N): {X}").strip().lower()
            if ans in ("y", "yes"):
                break
            if ans in ("n", "no"):
                open_key_page()
                print(f"{Y}Generate your key on the page, then paste it below.{X}")
                break

    for attempt in range(5):
        key = env_key or input(f"{C}Enter your key: {X}").strip().upper()
        res = _post("/verify", {"key": key, "device": dev})
        if res is None:
            print(f"{R}✘ Cannot reach the key server. Check your internet.{X}")
        elif res.get("ok"):
            rem = int(res["remaining"])
            print(f"{G}✔ Key accepted. Time left: {_fmt(rem)}{X}\n")
            return rem, key
        else:
            print(f"{R}✘ {MESSAGES.get(res.get('error'), 'Key check failed.')}{X}")
            if res.get("error") == "expired":
                open_key_page()
        env_key = ""  # an env key that failed must not loop forever

    sys.exit(1)


async def watchdog(remaining, key):
    """Returns when the key time is over (or the server says the key is no longer valid)."""
    dev = device_id()
    loop = asyncio.get_running_loop()
    deadline = time.monotonic() + remaining
    last_notice = time.monotonic()

    while True:
        left = deadline - time.monotonic()
        if left <= 0:
            return
        await asyncio.sleep(min(RECHECK_EVERY, left))

        res = await loop.run_in_executor(None, _post, "/verify", {"key": key, "device": dev})
        if res is not None:
            if not res.get("ok"):
                return
            deadline = time.monotonic() + int(res["remaining"])  # stay in sync with server

        if time.monotonic() - last_notice >= 1800:
            last_notice = time.monotonic()
            print(f"{C}ℹ Key time left: {_fmt(max(0, deadline - time.monotonic()))}{X}")


def show_expired():
    print(f"\n{P}{'═' * 50}{X}")
    print(f"{R}{'YOUR KEY TIME HAS ENDED'.center(50)}{X}")
    print(f"{P}{'═' * 50}{X}")
    print(f"{Y}The bot has been stopped. Generate a new key here:{X}")
    print(f"{C}{KEY_PAGE}{X}\n")
