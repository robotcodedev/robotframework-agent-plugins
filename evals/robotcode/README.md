# Evals for the `robotcode` skill

Behavioral tests for the [`robotcode` skill](../../plugins/robotcode/skills/robotcode/). They don't check exact output — they check that an agent with the skill loaded **reaches for the right `robotcode` command** and avoids the habits the skill warns against (grepping `.robot` files, loading `output.xml`, writing a test for an exploratory task, guessing keyword args instead of using `libdoc`).

Each case targets one behavior. They're ordered **simplest first** — from "just run it" through inventory and lookups to the debugger ("why does this fail?").

## Cases (simple → complex)

| # | Case | Checks |
| --- | --- | --- |
| 01 | run-tests | runs via `robotcode robot -i smoke`, reports counts |
| 02 | results-summary | inspects a finished run with `results`, not raw `output.xml` |
| 03 | results-diff | `results diff` baseline vs current to find the regression |
| 04 | inventory-discover-not-grep | `discover`, never grep over `.robot` |
| 05 | libdoc-first | `libdoc` before generic knowledge / web |
| 06 | analyze-before-run | `analyze code` (static) before executing |
| 07 | repl-explore-no-file | a "watch me" task in the REPL, no test file written |
| 08 | debug-why-test-fails | debug the **actual** failing test with `robot-debug` — don't paste it into a REPL |
| 09 | debug-break-at-line | line breakpoint + inspect variables in scope |
| 10 | repl-interactive-breakpoint | break into a keyword you build at the REPL prompt |

(`02` and `03` need `./setup.sh` run first; `07` needs a browser library — see the [fixture README](fixtures/demo-project/README.md).)

## How an eval is shaped

One JSON file per case in [`cases/`](cases/). The first three fields are the standard Skill-eval shape from [Anthropic's best-practices guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); the `must_*` fields are this harness's machine-checkable additions.

| Field | Meaning |
| --- | --- |
| `skills` | Skills that should be active (`["robotcode"]`). |
| `query` | The user request to send the agent. |
| `files` | Fixtures the case assumes exist in the project (informational — you provide them). |
| `expected_behavior` | Free-text rubric — **judged by you or an LLM**, not by the harness. |
| `must_run` | Regexes that **should** match a command the agent ran (e.g. `robotcode (robot-debug\|run-debug)`). |
| `must_not_run` | Regexes that must **not** match any command (e.g. `cat …output\.xml`). |
| `must_not_create` | Regexes on written file paths that must **not** match (e.g. `\.robot$`). |

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

[`run.py`](run.py) drives a headless `claude -p` session per case, extracts the **Bash commands** and **files written** from the `stream-json` transcript, and applies the `must_*` regex checks. The `expected_behavior` rubric is printed for you to tick off. It defaults to the bundled [`fixtures/demo-project`](fixtures/demo-project/) — a self-contained, offline Robot project built for these cases (see its [README](fixtures/demo-project/README.md)).

```bash
cd evals/robotcode
./fixtures/demo-project/setup.sh          # once — runs the suites so the results/diff cases have finished runs

./run.py --allow-all                      # all cases against the bundled fixture
./run.py --case 01 --allow-all            # just one case

# test across the models you ship for
./run.py --case 01 --model opus   --allow-all
./run.py --case 01 --model sonnet --allow-all
./run.py --case 01 --model haiku  --allow-all
```

`--project DIR` points it at a different project instead. Exit code is 0 only if every case passes its regex checks (the rubric stays manual).

**Prerequisites**

- `claude` CLI on `PATH`, with the **robotcode skill available** to it (install the plugin — see the [marketplace README](../../README.md) — or run where it is already loaded).
- `robotcode` installed in the target project's environment (`pip install robotcode[all]`). The bundled fixture needs nothing else and runs offline.
- `--allow-all` adds `--dangerously-skip-permissions` so bash isn't gated — fine for the throwaway fixture; be careful pointing `--project` at a real project, since the harness really executes the commands the agent chooses.
- **Cases 02 and 03** (results, diff) need finished runs — run `fixtures/demo-project/setup.sh` first. **Case 07** needs a browser library installed (SeleniumLibrary or Browser) — the only non-offline case.

### 3. Add an LLM judge (optional)

The harness only grades the objective `must_*` checks. For the `expected_behavior` rubric, capture the full transcript and hand it plus the rubric to a grader model for a pass/fail verdict — useful when behavior is fuzzier than "which command ran".

## Caveats

- **Regex checks are necessary, not sufficient.** They confirm the agent reached for the right command; the rubric covers the rest (did it report counts first? step through the debugger interactively and resume? avoid hanging?).
- **Test across models.** The guide recommends Haiku, Sonnet, and Opus — a skill that works on Opus may need more guidance for Haiku.
- **Evals are the source of truth for changes.** When you edit the skill, re-run the affected cases and compare; add a new case whenever you find a behavior the skill should enforce but doesn't.

## Adding a case

Copy any file in [`cases/`](cases/), give it the next number, write the `query` and `expected_behavior`, and add `must_run` / `must_not_run` / `must_not_create` for the behavioral signal. Keep one behavior per case.
