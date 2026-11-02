# Evals for the `robotcode` skill

Behavioral tests for the [`robotcode` skill](../../plugins/robotcode/skills/robotcode/). They don't check exact output — they check that an agent with the skill loaded **reaches for the right `robotcode` command** and avoids the habits the skill warns against (grepping `.robot` files, loading `output.xml`, writing a test for an exploratory task, guessing keyword args instead of using `robotcode doc`).

Each case targets one behavior. They're ordered **simplest first** — from "just run it" through inventory and lookups to the debugger ("why does this fail?"). The harness runs them with several agents, because what goes wrong differs: Copilot's `view` reads only part of a large file, Codex's sandbox rules out sessions, and Haiku needs more guidance than Opus.

## Cases (simple → complex)

| # | Case | Checks |
| --- | --- | --- |
| 01 | run-tests | runs via `robotcode robot -i smoke`, reports counts |
| 02 | results-summary | inspects a finished run with `results`, not raw `output.xml` |
| 03 | results-diff | `results diff` baseline vs current to find the regression |
| 04 | inventory-discover-not-grep | `discover`, never grep over `.robot` |
| 05 | doc-first | `robotcode doc` before generic knowledge / web |
| 06 | analyze-before-run | `analyze code` (static) before executing |
| 07 | repl-explore-no-file | a "watch me" task driven live in a REPL, no test file written |
| 08 | debug-why-test-fails | debug the **actual** failing test live — don't paste it into a REPL |
| 09 | debug-break-at-line | line breakpoint + inspect variables in scope, live |
| 10 | repl-interactive-breakpoint | break into a keyword you build in a REPL |
| 11 | suite-name-from-paths | selects a suite by a name from `discover`, not by the project's folder |
| 12 | results-search-value | `results log --search` for whether a value occurred, not grep on `output.xml` |
| 13 | repl-try-a-keyword | a plain "try it out" goes to the REPL, not to a throwaway test or a fixed list of inputs |
| 14 | repl-block | a `FOR` block goes in as a whole, with its `END` |
| 15 | debug-session-started-earlier | finds a session that is already open, reads its result and restarts it |
| 16 | debug-second-breakpoint | the whole suite under the debugger, with a breakpoint set during the run |
| 17 | session-in-own-sandbox | where each command has a sandbox of its own, the agent stays inside it and says what it could do |
| 18 | run-one-test-by-longname | one test by its longname, not by handing over the `.robot` file |
| 19 | global-option-before-subcommand | a profile goes before the subcommand |
| 20 | missing-extra-asks-first | `No such command`: asks before installing the extra |

(`02`, `03` and `12` need finished runs, which `./setup.sh` makes; the harness runs it in each copy of the fixture. `07` needs a browser library — see the [fixture README](fixtures/demo-project/README.md).)

## How an eval is shaped

One JSON file per case in [`cases/`](cases/). The first three fields are the standard Skill-eval shape from [Anthropic's best-practices guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); the `must_*` fields are this harness's machine-checkable additions.

| Field | Meaning |
| --- | --- |
| `skills` | Skills that should be active (`["robotcode"]`). |
| `query` | The user request to send the agent. |
| `files` | Fixtures the case assumes exist in the project (informational — you provide them). |
| `expected_behavior` | Free-text rubric — **judged by you or an LLM**, not by the harness. |
| `must_run` | Regexes that **should** match a command the agent ran (e.g. `robotcode session start debug`). |
| `must_not_run` | Regexes that must **not** match any command (e.g. `cat …output\.xml`). |
| `must_not_create` | Regexes on written file paths that must **not** match (e.g. `\.robot$`). |
| `must_answer` | Regexes that **should** match the agent's last message: the right way to a wrong answer is still wrong. |
| `drive` | `repl` or `debug`, for a case on driving one of them. The harness then also checks the way, see below. |
| `prepare` | Shell lines to run before the agent starts, in the same sandbox (e.g. to open a session). |
| `sandbox` | `own` for a case that needs the agent's own sandbox, whatever `--sandbox` says. |

All regexes are Python `re.search`, case-insensitive.

## Running them — there is no official runner

Per the best-practices guide, *"there is not currently a built-in way to run these evaluations."* Two ways to do it here:

### 1. Manually (no setup — the "Claude A / Claude B" loop)

Open a **fresh** Claude Code session in a real (or fixture) Robot Framework project with the skill installed, paste a case's `query`, and watch what it does:

- Did the skill trigger at all?
- Do the commands it runs satisfy `must_run` / avoid `must_not_run`?
- Does its behavior match every `expected_behavior` bullet?

Best for a quick read on a few cases, and the most faithful to real usage.

### 2. With the harness (`run.py`)

[`run.py`](run.py) runs a headless session of each agent per case, extracts the **shell commands**, **files written** and **last message** from its transcript, and applies the checks. The `expected_behavior` rubric is printed for you to tick off. Each run gets a fresh copy of the project; it defaults to the bundled [`fixtures/demo-project`](fixtures/demo-project/) — a self-contained, offline Robot project built for these cases (see its [README](fixtures/demo-project/README.md)).

```bash
cd evals/robotcode

# all cases with Claude Code, with the skill of this working copy
./run.py --plugin-dir ../../plugins/robotcode

# one case across agents and models
./run.py --plugin-dir ../../plugins/robotcode --case 08 \
  --agent claude:opus --agent claude:sonnet --agent claude:haiku --agent copilot --agent codex

# models answer differently each time: several runs of each, four at a time
./run.py --plugin-dir ../../plugins/robotcode --case 13 --agent claude:haiku --repeat 5 --jobs 4
```

At the end it prints a table of how many runs of each case and agent passed; `1E` marks a run that couldn't start (not logged in, out of credits). Transcripts stay in the folder that `--out` names, by default a new temporary one. `--project DIR` points it at a different project. Exit code is 0 only if every run passes its checks (the rubric stays manual).

| `--agent` | Model, for example | Where the skill comes from with `--plugin-dir` |
| --- | --- | --- |
| `claude` | `claude:haiku` | its `--plugin-dir`; an installed copy of the plugin is turned off in the project |
| `copilot` | `copilot:gpt-6.1-terra` | its `--plugin-dir` |
| `codex` | `codex:gpt-6-astra` | copied to `.agents/skills` in the project; an installed copy of the plugin is turned off |
| `opencode` | `opencode:github-copilot/gemini-3.8-flash` | copied to `.agents/skills` in the project |

**Sandboxes.** The agents can't ask for permission in a headless run, and the harness really executes the commands they choose. `--sandbox` says what keeps them in check:

| `--sandbox` | What it means |
| --- | --- |
| `whole` | One [bubblewrap](https://github.com/containers/bubblewrap) sandbox around the agent, the default where `bwrap` exists: a private `/tmp`, home and runtime folder. All of the agent's questions are off, and sessions work. Each run is apart from the others, so `--jobs` works. |
| `own` | The agent's own sandbox for each command (Claude Code's `sandbox` setting, Copilot's `--sandbox`, Codex's `workspace-write`), where a session can't outlive its command. Copilot's needs `--add-dir` for the Python installation. opencode has none, so these runs count as `1E`. |
| `none` | No sandbox, for a system without `bwrap`. Add `--allow-all` to turn the agent's questions off, only on a disposable machine. |

With its questions off an agent reads what it likes, and what it reads goes to its model. So in `whole` it sees of your home folder only the agent's own configuration, the folders on `PATH`, the environment of `--venv` with its interpreter and what `--add-dir` names; only the configuration and its copy of the project are writable, and the other runs are out of sight. Name anything else the environment needs with `--add-dir`, such as the sources of an editable install. The configuration stays visible with its history of sessions, because the login lies there: give the agent one of its own (`CLAUDE_CONFIG_DIR`, `CODEX_HOME`, `COPILOT_HOME`) if that matters. In `own` and `none` nothing of this holds.

**The way, with `drive`.** A right answer can come from a wrong way, so a case with `drive` also fails if the agent:

- uses neither a session nor the prompt of `robotcode repl` / `robot-debug`,
- feeds it a fixed list of inputs (`printf … | robotcode repl`, a heredoc) or builds a FIFO,
- starts it bare although its shell tool can't write to a running command (only Codex's can),
- sends several debugger steps in one shell command or in a shell loop, without reading the answers,
- leaves a session open without saying so.

**Prerequisites**

- The CLIs of the agents you name on `PATH` and logged in. A run costs what a session of that agent costs, and Codex's take a few minutes each. Set `CLAUDE_CONFIG_DIR` to run Claude Code with a configuration of its own.
- `robotcode` installed (`pip install robotcode[all]`) and on `PATH`, or its environment given with `--venv`. The bundled fixture needs nothing else and runs offline.
- **Case 07** needs a browser library installed (SeleniumLibrary or Browser), and **case 20** downloads `robotcode[runner]` from PyPI into its copy of the project. All others run offline.

### 3. Add an LLM judge (optional)

The harness only grades the objective checks. For the `expected_behavior` rubric, hand the transcript from `--out` plus the rubric to a grader model for a pass/fail verdict — useful when behavior is fuzzier than "which command ran".

## Caveats

- **Regex checks are necessary, not sufficient.** They confirm the agent reached for the right command; the rubric covers the rest (did it report counts first? step through the debugger interactively and resume? avoid hanging?).
- **Test across models and agents.** The guide recommends Haiku, Sonnet, and Opus — a skill that works on Opus may need more guidance for Haiku. One run says little: compare several with `--repeat`.
- **A Haiku model gets the skill named.** It hardly loads the skill by itself, so RobotCode's guide tells its users to name it, and the harness starts its prompts with *Use the robotcode skill.* Its runs say how well it follows the skill, not whether it finds it.
- **The transcript of Codex hides what it writes to a running command.** It shows `robotcode repl`, not the inputs that follow, so going one input at a time can only be checked in a session.
- **Evals are the source of truth for changes.** When you edit the skill, re-run the affected cases and compare; add a new case whenever you find a behavior the skill should enforce but doesn't.

## Adding a case

Copy any file in [`cases/`](cases/), give it the next number, write the `query` and `expected_behavior`, and add `must_run` / `must_not_run` / `must_not_create` / `must_answer` / `drive` for the behavioral signal. Ask as a user would: a query that says "work in one session, step by step" hides what the skill has to teach. Keep one behavior per case.

## Adding an agent

Add a class to `AGENTS` in [`run.py`](run.py): its binary, whether its shell tool writes to a running command, how the skill gets to it, its command line, the folders it must write, and how to read its transcript.
