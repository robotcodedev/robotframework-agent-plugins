#!/usr/bin/env python3
"""Minimal eval harness for the `robotcode` Agent Skill.

There is no official skill-eval runner (Anthropic's Skill best-practices say to
build your own), so this is a small, transparent one. For each case and each
agent it:

  1. runs the query as a headless session of that agent, in a fresh copy of the
     target project,
  2. extracts *which tools the agent chose* from its transcript (shell commands
     it ran, files it wrote, its last message), then
  3. checks the machine-verifiable parts of the case — `must_run`,
     `must_not_run`, `must_not_create`, `must_answer` (all Python regex,
     case-insensitive) and, with `drive`, how it drove the REPL or the debugger.

The free-text `expected_behavior` rubric is printed for you (or an LLM judge) to
assess — the harness does not grade it. The signal this skill cares about is
behavioral (which `robotcode` command the agent reached for), and that is what
the checks capture.

Usage:
    ./run.py --plugin-dir ../../plugins/robotcode \\
        [--agent claude:haiku --agent copilot --agent codex] [--case 08] [--repeat 3] [--jobs 4]

Without `--plugin-dir` the agent uses the skill it has installed. On Linux each
run sits in one bubblewrap sandbox around the whole agent, with all of the
agent's questions turned off: only the run's folder and the agent's own
configuration are writable. See the README for the other sandbox modes.

Exit code: 0 if every run passes its checks, 1 otherwise.
"""

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

CASES_DIR = Path(__file__).parent / "cases"
DEFAULT_PROJECT = Path(__file__).parent / "fixtures" / "demo-project"

GREEN, RED, YELLOW, DIM, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m",
)

# What an outer agent session leaves in the environment. robotcode would take a
# run for one of that agent, and the agent under test for a nested session.
OUTER_AGENT_VARS = re.compile(
    r"^(CLAUDE|CODEX|COPILOT|CURSOR|OPENCODE|GEMINI_CLI|ANTIGRAVITY|AUGMENT|CLINE|VSCODE_"
    r"|ELECTRON_RUN_AS_NODE$|AI_AGENT$|AGENT$|ROBOTCODE_|VIRTUAL_ENV$)"
)
KEEP_VARS = {"CLAUDE_CONFIG_DIR", "CODEX_HOME", "COPILOT_HOME"}

SKILL_FILE = "skills/robotcode/SKILL.md"
WRITES_TEST_FILE = re.compile(r"(?:>>?|\btee\s+(?:-a\s+)?)\s*(\S+\.(?:robot|resource))\b")


@dataclass
class Transcript:
    """What one agent session did, whichever agent it was."""

    commands: list[str] = field(default_factory=list)
    written: list[str] = field(default_factory=list)
    final: str = ""
    skill_loaded: bool = False
    error: str = ""


@dataclass
class Run:
    """One session of one agent on one case."""

    query: str
    model: str
    plugin_dir: str | None
    sandbox: str
    allow_all: bool
    add_dirs: list[str]
    project: Path
    out_dir: Path


class Claude:
    binary = "claude"
    has_own_sandbox = True
    # Its shell tool runs a command to its end, or in the background with nothing to write to it.
    writes_to_running_commands = False
    keeps_in_runtime_folder = ()

    def install_skill(self, project, plugin_dir):
        # An installed release of the plugin must not compete with --plugin-dir.
        (project / ".claude").mkdir(exist_ok=True)
        (project / ".claude" / "settings.json").write_text(
            json.dumps({"enabledPlugins": {"robotcode@robotframework-agent-plugins": False}})
        )

    def command(self, run):
        cmd = ["-p", run.query, "--output-format", "stream-json", "--verbose", "--strict-mcp-config", "--no-chrome"]
        if run.model:
            cmd += ["--model", run.model]
        if run.plugin_dir:
            cmd += ["--plugin-dir", run.plugin_dir]
        if run.sandbox == "own":
            cmd += ["--settings", json.dumps({"sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True}})]
            cmd += ["--permission-mode", "auto", "--permission-prompts", "none"]
        elif run.sandbox == "whole" or run.allow_all:
            cmd += ["--dangerously-skip-permissions"]
        return cmd

    def writable(self, env):
        config = env.get("CLAUDE_CONFIG_DIR")
        return [Path(config)] if config else [Path.home() / ".claude", Path.home() / ".claude.json"]

    def parse(self, events):
        t = Transcript()
        for ev in events:
            if ev.get("type") == "result" and ev.get("is_error"):
                t.error = str(ev.get("result") or ev.get("subtype"))
            if ev.get("type") != "assistant":
                continue
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "text" and block["text"].strip():
                    t.final = block["text"]
                if block.get("type") != "tool_use":
                    continue
                name, inp = block.get("name", ""), block.get("input", {}) or {}
                if name == "Bash" and inp.get("command"):
                    outside = "[outside sandbox] " if inp.get("dangerouslyDisableSandbox") else ""
                    t.commands.append(outside + inp["command"])
                elif name in ("Write", "Edit", "NotebookEdit") and inp.get("file_path"):
                    t.written.append(inp["file_path"])
                elif (name == "Skill" and "robotcode" in str(inp.get("skill"))) or (
                    name == "Read" and str(inp.get("file_path")).endswith(SKILL_FILE)
                ):
                    t.skill_loaded = True
        return t


class Copilot:
    binary = "copilot"
    has_own_sandbox = True
    # `bash`, `read_bash` and `stop_bash`: nothing writes to a running command (Copilot CLI 1.0.105).
    writes_to_running_commands = False
    # Its login lies in the keyring.
    keeps_in_runtime_folder = ("bus",)

    def install_skill(self, project, plugin_dir):
        pass

    def command(self, run):
        cmd = ["-p", run.query, "--output-format", "json", "--no-ask-user"]
        if run.model:
            cmd += ["--model", run.model]
        if run.plugin_dir:
            cmd += ["--plugin-dir", run.plugin_dir]
        if run.sandbox == "own":
            cmd += ["--sandbox"]
            for path in run.add_dirs:
                cmd += ["--add-dir", path]
        if run.sandbox != "none" or run.allow_all:
            cmd += ["--allow-all-tools"]
        return cmd

    def writable(self, env):
        return [Path(env.get("COPILOT_HOME") or Path.home() / ".copilot")]

    def parse(self, events):
        t = Transcript()
        for ev in events:
            kind, data = ev.get("type"), ev.get("data", {}) or {}
            if "error" in str(kind):
                t.error = str(data.get("message") or data)
            if kind != "assistant.message":
                continue
            if data.get("content"):
                t.final = data["content"]
            for request in data.get("toolRequests", []):
                args = request.get("arguments") or {}
                if not isinstance(args, dict):
                    continue
                name = request.get("name")
                if args.get("command"):
                    t.commands.append(args["command"])
                if name in ("create", "edit", "write") and args.get("path"):
                    t.written.append(args["path"])
                if (name == "skill" and "robotcode" in str(args)) or (
                    name == "view" and str(args.get("path")).endswith(SKILL_FILE)
                ):
                    t.skill_loaded = True
        return t


def copy_skill_to_project(project, plugin_dir):
    """For the agents that find skills in the project and have no option to load a plugin from a folder."""
    target = project / ".agents" / "skills" / "robotcode"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(Path(plugin_dir) / "skills" / "robotcode", target)


class Codex:
    binary = "codex"
    has_own_sandbox = True
    # `exec_command` keeps a command running and `write_stdin` writes to it. The transcript
    # shows the command, not these inputs, so going one input at a time can't be checked there.
    writes_to_running_commands = True
    keeps_in_runtime_folder = ()

    def install_skill(self, project, plugin_dir):
        copy_skill_to_project(project, plugin_dir)

    def command(self, run):
        # In the sandbox around the whole agent its own, one for each command, has to be off,
        # or sessions can't outlive their command.
        full = run.sandbox == "whole" or (run.sandbox == "none" and run.allow_all)
        mode = "danger-full-access" if full else "workspace-write"
        cmd = ["exec", "--json", "--sandbox", mode, "-C", str(run.project)]
        if run.model:
            cmd += ["--model", run.model]
        if run.plugin_dir:
            # An installed release of the plugin must not compete with the copy in the project.
            cmd += ["-c", 'plugins={"robotcode@robotframework-agent-plugins"={enabled=false}}']
        return [*cmd, run.query]

    def writable(self, env):
        return [Path(env.get("CODEX_HOME") or Path.home() / ".codex")]

    def parse(self, events):
        t = Transcript()
        seen = set()
        for ev in events:
            if ev.get("type") == "error":
                t.error = str(ev.get("message"))
            item = ev.get("item", {})
            # A command that still runs when the agent ends, like a debugger left at a stop, has no "completed".
            if ev.get("type") in ("item.started", "item.completed") and item.get("type") == "command_execution":
                if item.get("id") not in seen:
                    seen.add(item.get("id"))
                    t.commands.append(item.get("command", ""))
                if SKILL_FILE in item.get("command", ""):
                    t.skill_loaded = True
            if ev.get("type") != "item.completed":
                continue
            if item.get("type") == "agent_message":
                t.final = item.get("text", "")
            elif item.get("type") == "file_change":
                t.written += [c.get("path", "") for c in item.get("changes", [])]
        return t


class OpenCode:
    binary = "opencode"
    has_own_sandbox = False
    # Its `shell` tool runs a command to its end (opencode 2.2.4).
    writes_to_running_commands = False
    keeps_in_runtime_folder = ()

    def install_skill(self, project, plugin_dir):
        copy_skill_to_project(project, plugin_dir)

    def command(self, run):
        # --standalone: not through a background service that runs outside the sandbox.
        cmd = ["run", "--standalone", "--format", "json"]
        if run.sandbox != "none" or run.allow_all:
            cmd += ["--auto"]
        if run.model:
            cmd += ["--model", run.model]
        return [*cmd, run.query]

    def writable(self, env):
        # Its login lies in its data folder, so the runs show up in the user's list of sessions.
        home = Path.home()
        return [home / folder / "opencode" for folder in (".local/share", ".cache", ".local/state", ".config")]

    def parse(self, events):
        t = Transcript()
        for ev in events:
            if ev.get("type") == "error":
                t.error = str((ev.get("error") or {}).get("message") or ev.get("error"))
            part = ev.get("part") or {}
            if ev.get("type") == "text" and part.get("text"):
                t.final = part["text"]
            if ev.get("type") != "tool_use":
                continue
            tool, inp = part.get("tool", ""), (part.get("state") or {}).get("input") or {}
            path = str(inp.get("path") or inp.get("filePath"))
            if tool in ("shell", "bash") and inp.get("command"):
                t.commands.append(inp["command"])
            elif tool in ("write", "edit"):
                t.written.append(path)
            elif (tool == "skill" and "robotcode" in str(inp)) or (tool == "read" and path.endswith(SKILL_FILE)):
                t.skill_loaded = True
        return t


AGENTS = {"claude": Claude(), "copilot": Copilot(), "codex": Codex(), "opencode": OpenCode()}


def clean_env(venv, xdg_config):
    env = {k: v for k, v in os.environ.items() if k in KEEP_VARS or not OUTER_AGENT_VARS.match(k)}
    if venv:
        scripts = Path(venv) / ("Scripts" if os.name == "nt" else "bin")
        env["PATH"] = os.pathsep.join((str(scripts), env.get("PATH", "")))
        env["VIRTUAL_ENV"] = str(venv)
    # So that a user-global robot.toml doesn't count.
    env["XDG_CONFIG_HOME"] = str(xdg_config)
    if os.name != "nt":
        env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    return env


def copy_project(source, project, env):
    """A fresh copy with its finished runs, in a git repository, as agents expect of a project."""
    skipped = shutil.ignore_patterns("results", "__pycache__", ".robotcode_cache", ".venv", ".git")
    shutil.copytree(source, project, ignore=skipped)
    bash = shutil.which("bash", path=env.get("PATH"))
    if (project / "setup.sh").exists() and bash:
        subprocess.run([bash, "setup.sh"], cwd=project, env=env, capture_output=True, check=False)
    git = ["git", "-c", "user.name=Demo", "-c", "user.email=demo@example.com"]
    git += ["-c", "commit.gpgsign=false", "-c", "core.hooksPath="]
    subprocess.run([*git, "init", "--quiet", "--initial-branch=main"], cwd=project, capture_output=True, check=False)
    subprocess.run([*git, "add", "--all"], cwd=project, capture_output=True, check=False)
    subprocess.run([*git, "commit", "--quiet", "-m", "The project"], cwd=project, capture_output=True, check=False)


def needed_from_home(env):
    """What in the home folder runs the agent and robotcode: the PATH and the environment's interpreter."""
    paths = [os.path.normpath(p) for p in env.get("PATH", "").split(os.pathsep)]
    if env.get("VIRTUAL_ENV"):
        python = Path(env["VIRTUAL_ENV"]) / "bin" / "python"
        while python.is_symlink():
            python = python.parent / os.readlink(python)
        # Under the name its link uses, which can be a link to a folder itself, and the real one.
        paths += [str(python.parents[1]), str(python.resolve().parents[1])]
    return [p for p in dict.fromkeys(paths) if Path(p).is_relative_to(Path.home()) and Path(p).exists()]


def around_whole_agent(agent, run, env):
    """One sandbox around the whole agent: a private /tmp, home and runtime folder, little else visible."""
    # With its questions off an agent reads what it likes, and what it reads goes to its model.
    wrap = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp"]
    wrap += ["--tmpfs", str(Path.home())]
    # The other runs stay out of sight: an agent that looks around would read their transcripts.
    wrap += ["--tmpfs", str(run.out_dir)]
    for path in (run.plugin_dir, env.get("VIRTUAL_ENV"), *needed_from_home(env), *run.add_dirs):
        if path:
            wrap += ["--ro-bind", str(path), str(path)]
    for path in (run.project, env["XDG_CONFIG_HOME"]):
        wrap += ["--bind", str(path), str(path)]
    for path in agent.writable(env):
        if path.exists():
            wrap += ["--bind", str(path), str(path)]
    runtime = Path(env["XDG_RUNTIME_DIR"])
    wrap += ["--unshare-pid", "--die-with-parent", "--perms", "0700", "--tmpfs", str(runtime)]
    for name in agent.keeps_in_runtime_folder:
        if (runtime / name).exists():
            wrap += ["--bind", str(runtime / name), str(runtime / name)]
    return [*wrap, "--chdir", str(run.project)]


def run_agent(cmd, cwd, env, timeout, transcript, stderr):
    """Runs one session. The transcript goes to a file, so a run that hangs still shows what it did."""
    with open(transcript, "w") as out, open(stderr, "w") as err:
        proc = subprocess.Popen(
            cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True
        )
        try:
            proc.wait(timeout=timeout)
            return False
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                proc.kill()
            else:
                os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            return True


def read_events(path):
    events = []
    for line in Path(path).read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def check(patterns, haystacks):
    """Return (matched, unmatched) — each pattern tested (regex, IGNORECASE) against all haystacks."""
    matched, unmatched = [], []
    for pat in patterns or []:
        rx = re.compile(pat, re.IGNORECASE)
        (matched if any(rx.search(h) for h in haystacks) else unmatched).append(pat)
    return matched, unmatched


def evaluate(case, t):
    """Apply must_run / must_not_run / must_not_create / must_answer. Return the failures."""
    failures = []
    written = t.written + [m.group(1) for c in t.commands for m in WRITES_TEST_FILE.finditer(c)]
    _, missing = check(case.get("must_run"), t.commands)
    for pat in missing:
        failures.append(f"must_run not satisfied: /{pat}/")
    forbidden, _ = check(case.get("must_not_run"), t.commands)
    for pat in forbidden:
        failures.append(f"must_not_run matched (forbidden command ran): /{pat}/")
    forbidden_files, _ = check(case.get("must_not_create"), written)
    for pat in forbidden_files:
        failures.append(f"must_not_create matched (forbidden file written): /{pat}/")
    _, missing = check(case.get("must_answer"), [t.final])
    for pat in missing:
        failures.append(f"must_answer not satisfied: /{pat}/")
    return failures


LIVE = re.compile(r"\brobotcode\s+(?:-\S+(?:\s+[^-\s]\S*)?\s+)*(repl|robot-debug|run-debug)\b")
FED = re.compile(r"\|\s*(?:timeout\s+\S+\s+)?(?:\S*/)?robotcode\b|<<|\brobotcode\b[^|\n]*<\s*\S|tail\s+-f")
SEND = re.compile(r"""session\s+send\s+\S+\s+(?:'((?:[^']|'\\'')*)'|"((?:[^"\\]|\\.)*)")""")
STEP = re.compile(r"\s*\.(next|n|step|s|continue|c|return|r|until)\b")
SEND_IN_LOOP = re.compile(r"\bfor\b[^\n]*;\s*do\b[^\n]*session\s+send")
STILL_OPEN = re.compile(r"\b((still|stays?|remains?) open|(still |is |been |remains? |stays? )paused)\b", re.IGNORECASE)


def check_driving(kind, t, agent):
    """How the agent drove the REPL or the debugger (`drive` of a case): the part of the rubric a program can tell."""
    text = "\n".join(t.commands)
    failures = []
    in_session = re.search(rf"session\s+start\s+{kind}\b", text) and re.search(r"session\s+send\b", text)
    wanted = {"repl": {"repl"}, "debug": {"robot-debug", "run-debug"}}[kind]
    live = [
        c for c in t.commands
        if not re.search(r"session\s+(start|send)\b", c) and "--help" not in c
        and any(m.group(1) in wanted for m in LIVE.finditer(c))
    ]
    fed = [c for c in live if FED.search(c)]
    bare = [c for c in live if c not in fed]
    if not in_session and not live:
        failures.append(f"neither a session nor the prompt of `{kind}`")
    if fed:
        failures.append("fed it a fixed list of inputs instead of reading each answer")
    if "mkfifo" in text:
        failures.append("built a FIFO instead of using a session")
    if bare and not agent.writes_to_running_commands:
        failures.append("started it bare, without a way to write to it")
    if any(len([i for i in inputs if STEP.match(i)]) >= 2 or SEND_IN_LOOP.search(c)
           for c, inputs in ((c, [a or b for a, b in SEND.findall(c)]) for c in t.commands)):
        failures.append("sent several steps at once instead of reading each answer")
    if in_session and not re.search(r"session\s+stop\b", text) and not STILL_OPEN.search(t.final):
        failures.append("left the session open without saying so")
    return failures


def run_once(case_path, case, spec, n, args, out_dir):
    """Runs one case with one agent. Returns (failures, error, transcript)."""
    name, _, model = spec.partition(":")
    agent = AGENTS[name]
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", spec)
    run_dir = out_dir / f"{case_path.stem}--{slug}--{n}"
    run_dir.mkdir(parents=True)
    project = run_dir / "project"
    (run_dir / "xdg").mkdir()
    env = clean_env(args.venv, run_dir / "xdg")
    if not shutil.which("robotcode", path=env.get("PATH")):
        return [], "robotcode is not on PATH; activate its environment or use --venv", Transcript()
    copy_project(args.project, project, env)
    if args.plugin_dir:
        agent.install_skill(project, args.plugin_dir)

    sandbox = case.get("sandbox") or args.sandbox
    if sandbox == "own" and not agent.has_own_sandbox:
        return [], f"{agent.binary} has no sandbox of its own", Transcript()
    # Haiku hardly loads the skill by itself, so its users are told to name it.
    query = f"Use the robotcode skill. {case['query']}" if "haiku" in model else case["query"]
    run = Run(query, model, args.plugin_dir, sandbox, args.allow_all, args.add_dir, project, out_dir)
    binary = shutil.which(agent.binary, path=env.get("PATH"))
    if not binary:
        return [], f"{agent.binary} is not on PATH", Transcript()
    cmd = [binary, *agent.command(run)]
    if case.get("prepare"):
        # In the same sandbox, so that a session it opens is there for the agent.
        script = "{\n" + "\n".join(case["prepare"]) + '\n} >/dev/null 2>&1 </dev/null\nexec "$@"'
        cmd = ["bash", "-c", script, "--", *cmd]
    if sandbox == "whole":
        cmd = around_whole_agent(agent, run, env) + cmd

    transcript_file = run_dir / "transcript.jsonl"
    timed_out = run_agent(cmd, project, env, args.timeout, transcript_file, run_dir / "stderr.txt")
    t = agent.parse(read_events(transcript_file))

    if sandbox != "whole":
        # In the sandbox its sessions end with it.
        stop = ["robotcode", "session", "stop", "--project"]
        subprocess.run(stop, cwd=project, env=env, capture_output=True, check=False)
    if not args.keep:
        shutil.rmtree(project, ignore_errors=True)

    if t.error:
        # Not logged in, out of credits: says nothing about the skill, even if the session had begun.
        return [], t.error, t
    if not t.commands and not t.final:
        stderr = (run_dir / "stderr.txt").read_text(errors="replace").strip()
        return [], stderr[-300:] or "no transcript", t
    failures = evaluate(case, t)
    if case.get("skills") and args.plugin_dir and not t.skill_loaded:
        failures.append("the skill wasn't loaded")
    if case.get("drive"):
        failures += check_driving(case["drive"], t, agent)
    if timed_out:
        failures.append(f"timed out after {args.timeout} s")
    return failures, "", t


def main():
    ap = argparse.ArgumentParser(description="Run robotcode skill evals.")
    ap.add_argument("--project", default=str(DEFAULT_PROJECT),
                    help="robot project to copy for each run (default: bundled fixtures/demo-project)")
    ap.add_argument("--agent", action="append", metavar="NAME[:MODEL]",
                    help=f"agent to run, repeatable; one of {', '.join(AGENTS)}, e.g. claude:haiku (default: claude)")
    ap.add_argument("--case", action="append",
                    help="run only cases whose filename starts with this (e.g. 01), repeatable")
    ap.add_argument("--repeat", type=int, default=1,
                    help="runs per case and agent; models answer differently each time")
    ap.add_argument("--jobs", type=int, default=1, help="runs at the same time; only with --sandbox whole")
    ap.add_argument("--sandbox", choices=("whole", "own", "none"), default="whole" if shutil.which("bwrap") else "none",
                    help="whole: one bubblewrap sandbox around the agent (default where bwrap exists); "
                         "own: the agent's own sandbox for each command; none: no sandbox")
    ap.add_argument("--allow-all", action="store_true",
                    help="turn the agent's questions off with --sandbox none; only on a disposable machine")
    ap.add_argument("--venv", help="the environment with robotcode, if it isn't on PATH")
    ap.add_argument("--add-dir", action="append", default=[],
                    help="a folder a sandbox must show: for Copilot's --sandbox the Python installation, "
                         "for the whole sandbox what the environment needs from the home folder "
                         "(e.g. the sources of an editable install)")
    ap.add_argument("--timeout", type=int, default=300, help="per-run timeout (s)")
    ap.add_argument("--plugin-dir", help="load the plugin from this folder, to test a skill that is not released")
    ap.add_argument("--out", help="folder for the transcripts (default: a new temporary folder)")
    ap.add_argument("--keep", action="store_true", help="keep the copy of the project of each run")
    args = ap.parse_args()

    specs = args.agent or ["claude"]
    for spec in specs:
        if spec.partition(":")[0] not in AGENTS:
            ap.error(f"unknown agent {spec}; one of {', '.join(AGENTS)}")
    if args.jobs > 1 and args.sandbox != "whole":
        ap.error("--jobs needs --sandbox whole: outside of it `session list` shows the sessions of the other runs")
    if args.sandbox == "whole" and not shutil.which("bwrap"):
        ap.error("--sandbox whole needs bubblewrap (bwrap); use --sandbox own, or none with --allow-all")
    args.plugin_dir = str(Path(args.plugin_dir).resolve()) if args.plugin_dir else None
    args.venv = str(Path(args.venv).absolute()) if args.venv else None
    args.project = str(Path(args.project).resolve())
    out_dir = Path(args.out).resolve() if args.out else Path(tempfile.mkdtemp(prefix="robotcode-evals-"))
    out_dir.mkdir(parents=True, exist_ok=True)

    case_paths = sorted(CASES_DIR.glob("*.json"))
    if args.case:
        case_paths = [c for c in case_paths if any(c.name.startswith(prefix) for prefix in args.case)]
    if not case_paths:
        print("no matching cases", file=sys.stderr)
        return 2
    cases = {path: json.loads(path.read_text()) for path in case_paths}

    print_lock = threading.Lock()
    results = {}

    def one(path, spec, n):
        failures, error, t = run_once(path, cases[path], spec, n, args, out_dir)
        with print_lock:
            results[(path, spec, n)] = (failures, error)
            print(f"\n{BOLD}━━ {path.stem} ━━{RESET}  {spec} #{n}")
            if error:
                print(f"  {RED}ERROR{RESET} could not run session: {error}", flush=True)
                return
            for c in t.commands:
                print(f"    $ {c.splitlines()[0]}" + (" …" if "\n" in c else ""))
            if t.written:
                print(f"  {DIM}files written:{RESET} " + ", ".join(t.written))
            if failures:
                print(f"  {RED}FAIL{RESET}")
                for f in failures:
                    print(f"    - {f}")
            else:
                print(f"  {GREEN}PASS{RESET}")
            sys.stdout.flush()

    runs = [(path, spec, n) for path in case_paths for spec in specs for n in range(1, args.repeat + 1)]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for future in [pool.submit(one, *run) for run in runs]:
            future.result()

    width = max(len(path.stem) for path in case_paths) + 2
    columns = [max(len(spec), args.repeat * 2 + 3) + 2 for spec in specs]
    print(f"\n{BOLD}{'':{width}}" + "".join(f"{spec:{c}}" for spec, c in zip(specs, columns)) + RESET)
    for path in case_paths:
        row = f"{path.stem:{width}}"
        for spec, c in zip(specs, columns):
            mine = [results[(path, spec, n)] for n in range(1, args.repeat + 1)]
            passed = sum(1 for failures, error in mine if not failures and not error)
            errors = sum(1 for _, error in mine if error)
            cell = f"{passed}/{args.repeat}" + (f" {errors}E" if errors else "")
            color = GREEN if passed == args.repeat else RED
            row += f"{color}{cell:{c}}{RESET}"
        print(row)

    print(f"\n{YELLOW}rubric — judge manually{RESET} {DIM}(transcripts in {out_dir}){RESET}")
    for path in case_paths:
        print(f"\n{BOLD}{path.stem}{RESET}  {DIM}{cases[path].get('focus', '')}{RESET}")
        print(f"  query: {cases[path]['query']}")
        for b in cases[path].get("expected_behavior", []):
            print(f"    [ ] {b}")

    passed = sum(1 for failures, error in results.values() if not failures and not error)
    failed = len(results) - passed
    print(f"\n{BOLD}{passed} passed, {failed} failed{RESET} (checks only; rubric is manual)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
