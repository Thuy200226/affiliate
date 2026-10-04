"""Start the local console; no installs, imports or publisher activation."""
import argparse
import fcntl
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/control-api/src"))
from affiliate_control.application import Application
from affiliate_control.config import Settings
from affiliate_control.http import make_server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--bind", default="127.0.0.1")
    args = parser.parse_args()
    os.umask(0o077)
    settings = Settings(runtime=args.runtime_root.resolve() if args.runtime_root else None,
                        port=args.port, bind=args.bind)
    settings.state.mkdir(exist_ok=True, mode=0o700)
    with (settings.state / "server.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        app = Application(settings)
        server = make_server(app)
        app.store.recover()
        print(f"Console ready: http://127.0.0.1:{args.port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
