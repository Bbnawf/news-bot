import os, sys, time, requests, json

os.environ["TELEGRAM_BOT_TOKEN"] = "8387787315:AAHVhFQt7Wv9J9JsCA_CchdwKY21fg6XTCU"
os.environ["TELEGRAM_CHANNEL_ID"] = "@ksbskehwb"

from news_bot import (
    load_json, save_json, SETTINGS_FILE, POSTED_FILE,
    process_commands, BOT_TOKEN, CHANNEL_ID
)

print("""
╔══════════════════════════════╗
║  بوت أخبار الأنمي والألعاب   ║
║  وضع: استجابة فورية 🌐       ║
║  للخروج: Ctrl+C              ║
╚══════════════════════════════╝
""")

while True:
    try:
        settings = load_json(SETTINGS_FILE, {
            "owner_id": 5381442151, "owner_username": "Ozzrr",
            "interval_minutes": 15, "max_age_days": 2, "max_per_run": 3,
            "channel_id": "@ksbskehwb", "sources": {}, "extra_sources": {},
            "translate_enabled": True, "emoji_enabled": True,
            "whitelist_enabled": True, "mal_check_enabled": True,
            "update_offset": 0, "run_now": False, "last_full_run": 0, "_init_sent": False
        })

        old_offset = settings.get("update_offset", 0)
        settings = process_commands(settings)
        new_offset = settings.get("update_offset", 0)

        if settings.get("_commands_processed"):
            save_json(SETTINGS_FILE, settings)
            gh_token = os.environ.get("GITHUB_TOKEN", "")
            if gh_token:
                try:
                    requests.post(
                        "https://api.github.com/repos/Bbnawf/news-bot/actions/workflows/277043592/dispatches",
                        headers={"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github.v3+json"},
                        json={"ref": "main"}, timeout=10
                    )
                except: pass
        else:
            save_json(SETTINGS_FILE, settings)

    except KeyboardInterrupt:
        print("\n[STOP] بإذن الله")
        break
    except Exception as e:
        print(f"[ERR] {e}")

    time.sleep(1.5)
