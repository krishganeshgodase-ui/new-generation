"""Entry point.
  python run.py            setup wizard, then start the dashboard at http://127.0.0.1:8000
  python run.py check      only run the setup checks
  python run.py tick       one AUTO MODE cycle + process the queue, then exit (for Windows Task Scheduler)
"""
import sys
import threading
import time
import webbrowser

from app import config, database as db, setup_check


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    config.ensure_dirs()
    db.init_db()
    if cmd == "check":
        return 0 if setup_check.print_report() else 1
    if cmd == "tick":
        from app import auto, queue
        print("auto:", auto.tick())
        print("jobs processed:", queue.run_pending())
        print("auto:", auto.tick())      # upload slots may become due after generation finished
        print("jobs processed:", queue.run_pending())
        return 0
    ok = setup_check.print_report()
    if not ok:
        print("Fix the ✗ items above, then run again. (Warnings ⚠ are optional.)")
        return 1
    import uvicorn
    host, port = config.env("HOST", "127.0.0.1"), int(config.env("PORT", "8000"))
    url = f"http://{host}:{port}"
    print(f"Dashboard: {url}   (Ctrl+C to stop)\n")
    if "--no-browser" not in sys.argv:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run("app.main:app", host=host, port=port, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
