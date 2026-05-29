# robotcode

> RobotCode CLI plugin for Robot Framework library, resource, keyword, project, and result workflows.

This plugin teaches AI coding agents how to drive the [`robotcode`](https://robotcode.io) CLI in a Robot Framework project — picking the right command, respecting `robot.toml` / profiles, using `libdoc` for keyword lookup, the REPL for live exploration, and `results` instead of raw `output.xml`. Once installed, the agent recognises Robot Framework requests ("run the smoke tests", "what failed?", "what does this keyword do?", "try this in a REPL") and reaches for the project-local CLI instead of guessing.

## Prerequisites

- A Robot Framework project with [`robotcode`](https://robotcode.io/01_quickstart/) available in the project's Python environment (e.g. `pip install robotcode[all]`). The plugin guides the agent in using `robotcode`; it does not install or wrap the CLI itself.
- An AI agent that supports the [Open Plugin Specification](https://open-plugins.com/plugin-builders/specification). See [supported agents](https://open-plugins.com/supported-agents) for the current list.

## Install

Add the parent marketplace once, then install this plugin from it:

```sh
# Claude Code
claude plugin marketplace add robotcodedev/robotframework-agent-plugins
claude plugin install robotcode@robotframework-agent-plugins

# GitHub Copilot CLI
copilot plugin marketplace add robotcodedev/robotframework-agent-plugins
copilot plugin install robotcode@robotframework-agent-plugins
```

For Codex, VS Code Copilot Chat, and other Open-Plugins-compliant agents, see the [marketplace README](../../README.md).

> Using the [RobotCode VS Code extension](https://marketplace.visualstudio.com/items?itemName=d-biehl.robotcode)? It already bundles this plugin via `contributes.chatPlugins` — no separate install needed for VS Code Copilot Chat.

## What's inside

A single Skill:

| Path | Purpose |
| --- | --- |
| [`skills/robotcode/SKILL.md`](skills/robotcode/SKILL.md) | Entry point — picking the right mode (explore, author, run, inspect, analyze, discover, look up), CLI overview, output formats, profiles/tags/suites, gotchas. |
| [`skills/robotcode/references/install.md`](skills/robotcode/references/install.md) | Installing RobotCode into the project's environment, choosing extras (`runner`, `analyze`, `repl`), and recovering from `Error: No such command 'X'`. |
| [`skills/robotcode/references/authoring.md`](skills/robotcode/references/authoring.md) | Writing tests and reusable keywords — reuse → prototype → analyze → run. |
| [`skills/robotcode/references/repl.md`](skills/robotcode/references/repl.md) | Interactive REPL for exploration and step-by-step development. |
| [`skills/robotcode/references/workflows.md`](skills/robotcode/references/workflows.md) | Multi-step recipes — run-and-report, investigate failures, lint changed files, manage suppressions. |
| [`skills/robotcode/references/results.md`](skills/robotcode/references/results.md) | Inspecting finished runs with `robotcode results` instead of parsing `output.xml`. |
| [`skills/robotcode/references/large-projects.md`](skills/robotcode/references/large-projects.md) | Filtering, aggregation, and bounded queries for large suites. |

The agent decides when to activate the skill from the description in `SKILL.md`'s frontmatter — no slash command, no explicit invocation needed.

## Updating

```sh
claude plugin marketplace update   # or your agent's equivalent
```

The marketplace [`robotcodedev/robotframework-agent-plugins`](https://github.com/robotcodedev/robotframework-agent-plugins) is the source of truth. Pull requests welcome — see the marketplace [CONTRIBUTING notes](../../README.md#contributing).

## Links

- RobotCode documentation — <https://robotcode.io>
- RobotCode CLI source — <https://github.com/robotcodedev/robotcode>
- Marketplace — <https://github.com/robotcodedev/robotframework-agent-plugins>

## License

Apache-2.0 — see [LICENSE](LICENSE).
