"""Small pre-Git gate; does not claim a full credential/dependency audit."""
import argparse
import ast
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".local", "__pycache__", ".venv", "node_modules"}
CODE = {".py", ".js", ".css", ".swift", ".ts", ".tsx"}
FORBIDDEN = {".mp4", ".mov", ".wav", ".mp3", ".zip", ".sqlite", ".db", ".pem", ".key", ".log"}
SECRET = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|AIza[0-9A-Za-z_-]{35}|"
                    r"\bgh[pousr]_[A-Za-z0-9]{30,}|\bsk-[A-Za-z0-9_-]{35,}")


def files(staged):
    if staged:
        result = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
                                cwd=ROOT, capture_output=True, check=True)
        return [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]
    return [p for p in ROOT.rglob("*") if p.is_file() and not EXCLUDED.intersection(p.relative_to(ROOT).parts)]


def check(path, staged=False):
    relative = path.relative_to(ROOT)
    issues = []
    if path.is_symlink():
        return [f"{relative}: symlink requires explicit review"]
    if path.suffix in FORBIDDEN or set(relative.parts) & {"private", "artifacts", "backups", "dist"}:
        return [f"{relative}: runtime/private artifact is not source"]
    if path.name.startswith(".env") and path.name != ".env.example":
        return [f"{relative}: environment secret file"]
    if any(word in path.name.lower() for word in ("cookies", "storage-state", "client_secret")):
        return [f"{relative}: account/session file"]
    if staged:
        result = subprocess.run(["git", "show", ":" + relative.as_posix()], cwd=ROOT,
                                capture_output=True, check=True)
        text = result.stdout.decode("utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    if SECRET.search(text):
        issues.append(f"{relative}: possible secret; values withheld")
    if path.suffix in CODE and len(text.splitlines()) > 250:
        issues.append(f"{relative}: exceeds 250 code lines")
    if path.suffix == ".py":
        tree = ast.parse(text, filename=str(relative))
        for item in ast.walk(tree):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.end_lineno - item.lineno + 1 > 60:
                issues.append(f"{relative}:{item.lineno}: function exceeds 60 lines")
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    paths = files(args.staged)
    issues = [issue for path in paths for issue in check(path, args.staged)]
    print("\n".join(issues) if issues else f"PASS: {len(paths)} source files; line/secret/artifact checks.")
    return bool(issues)


if __name__ == "__main__":
    sys.exit(main())
