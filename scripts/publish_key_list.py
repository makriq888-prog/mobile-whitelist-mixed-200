#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False)


def git_output(repo: Path, *args: str) -> str:
    proc = git(repo, *args)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy checked key list into a git repo and optionally push it.")
    parser.add_argument("--source", type=Path, default=Path("artifacts/short-key-list.txt"))
    parser.add_argument("--target-repo", type=Path, required=True)
    parser.add_argument("--target-file", default="data/short-key-list.txt")
    parser.add_argument("--commit-message", default="Update short key list")
    parser.add_argument("--branch", help="Branch to publish to. Defaults to the target repo current branch.")
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()

    remote_url = git_output(args.target_repo, "config", "--get", "remote.origin.url")
    branch = args.branch or git_output(args.target_repo, "branch", "--show-current")
    if not branch:
        branch = "main"

    with tempfile.TemporaryDirectory(prefix="publish-key-list-") as tmpdir:
        publish_repo = Path(tmpdir) / "repo"
        clone = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, remote_url, str(publish_repo)],
            text=True,
            capture_output=True,
            check=False,
        )
        if clone.returncode != 0:
            raise SystemExit(clone.stderr.strip() or clone.stdout.strip() or "git clone failed")

        target_path = publish_repo / args.target_file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.source, target_path)

        add = git(publish_repo, "add", args.target_file)
        if add.returncode != 0:
            raise SystemExit(add.stderr.strip() or "git add failed")

        diff = git(publish_repo, "diff", "--cached", "--quiet")
        if diff.returncode == 0:
            print("No changes to publish")
            return 0
        if diff.returncode not in (0, 1):
            raise SystemExit(diff.stderr.strip() or "git diff failed")

        commit = git(publish_repo, "commit", "-m", args.commit_message)
        if commit.returncode != 0:
            raise SystemExit(commit.stderr.strip() or commit.stdout.strip() or "git commit failed")
        print(commit.stdout.strip())

        if args.push:
            push = git(publish_repo, "push", "origin", branch)
            if push.returncode != 0:
                raise SystemExit(push.stderr.strip() or push.stdout.strip() or "git push failed")
            print(push.stdout.strip() or "pushed")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
