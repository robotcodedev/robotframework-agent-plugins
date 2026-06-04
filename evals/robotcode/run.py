#!/usr/bin/env python3
"""Minimal eval harness for the `robotcode` Agent Skill.

There is no official skill-eval runner (Anthropic's Skill best-practices say to
build your own), so this is a small, transparent one. For each case it:

  1. runs the query as a headless Claude Code session in a target project, and
  2. extracts *which tools the agent chose* from the stream-json transcript
     (Bash commands it ran, files it wrote), then
  3. checks the machine-verifiable parts of the case — `must_run`,
     `must_not_run`, `must_not_create` (all Python regex, case-insensitive).

The free-text `expected_behavior` rubric is printed for you (or an LLM judge) to
assess — the harness does not grade it. The signal this skill cares about is
behavioral (which `robotcode` command the agent reached for), and that is what
the regex checks capture.

Usage:
    ./run.py --project /path/to/robot-project [--case 01] [--model sonnet] [--allow-all]

The skill must be available to the `claude` CLI in that project (install the
plugin from the marketplace, or run where it is already loaded). `--allow-all`
adds `--dangerously-skip-permissions` so bash isn't gated — only do that against
a disposable fixture project. Cases that name a fixture under `files` need that
fixture to exist in the project (or adapt the query).

Exit code: 0 if every case passes its regex checks, 1 otherwise.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CASES_DIR = Path(__file__).parent / "cases"
DEFAULT_PROJECT = Path(__file__).parent / "fixtures" / "demo-project"

GREEN, RED, YELLOW, DIM, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m",
)


def run_claude(query, project, model, allow_all, timeout):
    """Run one headless Claude Code session; return the stream-json lines (list of dicts)."""
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose"]
    if model:
        cmd += ["--model", model]
    if allow_all:
        cmd += ["--dangerously-skip-permissions"]
    try:
        proc = subprocess.run(
            cmd, cwd=project, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"
    events = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not events:
        return None, (proc.stderr.strip() or "no transcript")
    return events, None


def extract_tools(events):
    """Pull (bash_commands, written_files) out of assistant tool_use blocks."""
    commands, written = [], []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []):
            if block.get("type") != "tool_use":
                continue
            name, inp = block.get("name", ""), block.get("input", {}) or {}
            if name == "Bash" and inp.get("command"):
                commands.append(inp["command"])
            elif name in ("Write", "Edit", "NotebookEdit") and inp.get("file_path"):
                written.append(inp["file_path"])
    return commands, written


def check(patterns, haystacks):
    """Return (matched, unmatched) — each pattern tested (regex, IGNORECASE) against all haystacks."""
    matched, unmatched = [], []
    for pat in patterns or []:
        rx = re.compile(pat, re.IGNORECASE)
        (matched if any(rx.search(h) for h in haystacks) else unmatched).append(pat)
    return matched, unmatched


def evaluate(case, commands, written):
    """Apply must_run / must_not_run / must_not_create. Return (ok, failures)."""
    failures = []
    _, missing = check(case.get("must_run"), commands)
    for pat in missing:
        failures.append(f"must_run not satisfied: /{pat}/")
    forbidden, _ = check(case.get("must_not_run"), commands)
    for pat in forbidden:
        failures.append(f"must_not_run matched (forbidden command ran): /{pat}/")
    forbidden_files, _ = check(case.get("must_not_create"), written)
    for pat in forbidden_files:
        failures.append(f"must_not_create matched (forbidden file written): /{pat}/")
    return not failures, failures


def main():
    ap = argparse.ArgumentParser(description="Run robotcode skill evals.")
    ap.add_argument("--project", default=str(DEFAULT_PROJECT),
                    help="robot project dir to run the agent in (default: bundled fixtures/demo-project)")
    ap.add_argument("--case", help="run only cases whose filename starts with this (e.g. 01)")
    ap.add_argument("--model", help="claude model (e.g. haiku, sonnet, opus) — test all three")
    ap.add_argument("--allow-all", action="store_true", help="add --dangerously-skip-permissions")
    ap.add_argument("--timeout", type=int, default=300, help="per-case timeout (s)")
    args = ap.parse_args()

    cases = sorted(CASES_DIR.glob("*.json"))
    if args.case:
        cases = [c for c in cases if c.name.startswith(args.case)]
    if not cases:
        print("no matching cases", file=sys.stderr)
        return 2

    passed = failed = 0
    for path in cases:
        case = json.loads(path.read_text())
        print(f"\n{BOLD}━━ {path.stem} ━━{RESET}  {DIM}{case.get('focus','')}{RESET}")
        print(f"  query: {case['query']}")

        events, err = run_claude(
            case["query"], args.project, args.model, args.allow_all, args.timeout
        )
        if events is None:
            print(f"  {RED}ERROR{RESET} could not run session: {err}")
            failed += 1
            continue

        commands, written = extract_tools(events)
        ok, failures = evaluate(case, commands, written)

        print(f"  {DIM}commands run:{RESET}")
        for c in commands:
            print(f"    $ {c.splitlines()[0]}" + (" …" if "\n" in c else ""))
        if written:
            print(f"  {DIM}files written:{RESET} " + ", ".join(written))

        if ok:
            print(f"  {GREEN}PASS{RESET} (regex checks)")
            passed += 1
        else:
            print(f"  {RED}FAIL{RESET}")
            for f in failures:
                print(f"    - {f}")
            failed += 1

        print(f"  {YELLOW}rubric — judge manually:{RESET}")
        for b in case.get("expected_behavior", []):
            print(f"    [ ] {b}")

    print(f"\n{BOLD}{passed} passed, {failed} failed{RESET} (regex checks only; rubric is manual)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
