#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys


HELP_TEXT = """Usage: python3 scripts/run_pipeline.py

Runs the key validator and optionally publishes the generated list if
PUBLISH_TARGET_REPO is set in the environment.
"""


def run(*args: str) -> int:
    proc = subprocess.run(args, check=False)
    return proc.returncode


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        print(HELP_TEXT)
        return 0

    checker_cmd = [
        sys.executable,
        "scripts/check_key_list.py",
        "--output",
        os.getenv("OUTPUT_PATH", "artifacts/short-key-list.txt"),
        "--report",
        os.getenv("REPORT_PATH", "artifacts/check-report.json"),
        "--limit",
        os.getenv("KEY_LIST_LIMIT", os.getenv("WHITELIST_LIMIT", "200")),
        "--workers",
        os.getenv("WORKERS", "4"),
        "--port-base",
        os.getenv("PORT_BASE", "21080"),
    ]
    if os.getenv("TCP_PRECHECK", "").lower() in {"1", "true", "yes"}:
        checker_cmd.append("--tcp-precheck")

    check_exit = run(*checker_cmd)
    if check_exit != 0:
        return check_exit

    target_repo = os.getenv("PUBLISH_TARGET_REPO", "").strip()
    if not target_repo:
        return 0

    publish_cmd = [
        sys.executable,
        "scripts/publish_key_list.py",
        "--source",
        os.getenv("OUTPUT_PATH", "artifacts/short-key-list.txt"),
        "--target-repo",
        target_repo,
        "--target-file",
        os.getenv("PUBLISH_TARGET_FILE", "data/short-key-list.txt"),
        "--commit-message",
        os.getenv("PUBLISH_COMMIT_MESSAGE", "Update short key list"),
    ]
    if os.getenv("PUSH_AFTER_PUBLISH", "").lower() in {"1", "true", "yes"}:
        publish_cmd.append("--push")
    return run(*publish_cmd)


if __name__ == "__main__":
    raise SystemExit(main())
