"""Trigger build-robust-windows and wait for result."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


REPO = "hcwhan/workflows"
WORKFLOW = "build-robust-windows.yml"
ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, text=True, capture_output=True, check=False, **kwargs)


def gh_json(args: list[str]) -> object:
    proc = run(["gh", *args, "--json", "databaseId,status,conclusion,url"])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout)
    return json.loads(proc.stdout)[0]


def main() -> int:
    proc = run(["gh", "workflow", "run", WORKFLOW, "-R", REPO])
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        return proc.returncode

    time.sleep(5)
    listed = run([
        "gh", "run", "list",
        "-R", REPO,
        "-w", WORKFLOW,
        "-L", "1",
        "--json", "databaseId,status,conclusion,url",
    ])
    if listed.returncode != 0:
        sys.stderr.write(listed.stderr or listed.stdout)
        return listed.returncode

    run_info = json.loads(listed.stdout)[0]
    run_id = str(run_info["databaseId"])
    print(f"Run: {run_info['url']}", flush=True)

    watch = subprocess.run(["gh", "run", "watch", run_id, "-R", REPO])
    if watch.returncode != 0:
        return watch.returncode

    final = gh_json(["run", "view", run_id, "-R", REPO])
    conclusion = final.get("conclusion")
    print(f"Conclusion: {conclusion}", flush=True)
    return 0 if conclusion == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
