import subprocess
import time
import sys
import os

LOG_FILE = "forge.log"

def start_bot():
    log = open(LOG_FILE, "a")
    return subprocess.Popen(
        [sys.executable, "bot.py"],
        stdout=log,
        stderr=log
    )

if __name__ == "__main__":
    print("🔥 GoalForge Launcher Started")
    print(f"📋 Logs: {os.path.abspath(LOG_FILE)}")

    restart_count = 0

    while True:
        process = start_bot()
        print(f"🚀 Bot started (attempt #{restart_count + 1})")

        process.wait()
        restart_count += 1

        print(f"⚠ Bot stopped. Restarting in 5 seconds... (total restarts: {restart_count})")
        time.sleep(5)
