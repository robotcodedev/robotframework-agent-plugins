# robotframework-agent-plugins

A curated marketplace of [Agent Plugins](https://agent-plugins.org/) for Robot Framework — Skills (and more plugin components over time) that extend AI coding agents like Claude Code, GitHub Copilot, and Codex with Robot Framework expertise.

## Plugins in this marketplace

| Plugin | What it does |
| --- | --- |
| [`robotcode`](plugins/robotcode/) | Teaches AI coding agents to drive `robotcode` properly in Robot Framework projects. |

More plugins are planned — Browser Library, RequestsLibrary, and general Robot Framework patterns.

## Before you install

Plugins from this marketplace follow the [Agent Plugins specification](https://agent-plugins.org/specification): each has a `plugin.json` with `$schema` in its folder and its skills under `skills/`. The [compatible clients](https://agent-plugins.org/compatible-clients) page lists the agents that support it. Claude Code isn't on that list, but it installs the plugins from this repository's marketplace file for Claude Code.

The specification covers the plugin, not how it is installed. Every agent has its own marketplace file and its own commands to add a marketplace and install a plugin, and this repository has the marketplace files of the agents below. Pick the section for your agent.

## Install per agent

### Claude Code

```sh
claude plugin marketplace add robotcodedev/robotframework-agent-plugins
claude plugin install robotcode@robotframework-agent-plugins
```

To update, refresh the marketplace and then the plugin:

```sh
claude plugin marketplace update robotframework-agent-plugins
claude plugin update robotcode@robotframework-agent-plugins
```

To install a specific release, see [Versions and pinning](#versions-and-pinning).

### GitHub Copilot CLI

```sh
copilot plugin marketplace add robotcodedev/robotframework-agent-plugins
copilot plugin install robotcode@robotframework-agent-plugins
```

See [GitHub Copilot CLI plugin marketplaces](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace).

### GitHub Copilot Chat (VS Code)

Add the marketplace to your User Settings:

```jsonc
// settings.json
"chat.plugins.marketplaces": [
  "robotcodedev/robotframework-agent-plugins"
]
```

Then install plugins from the Extensions view's *Chat Plugins* section.

> The [RobotCode VS Code extension](https://marketplace.visualstudio.com/items?itemName=d-biehl.robotcode) already ships the `robotcode` plugin built-in via `contributes.chatPlugins` — you only need this marketplace if you want to mix in future plugins from it.

### Codex

```sh
codex plugin marketplace add robotcodedev/robotframework-agent-plugins
codex plugin add robotcode@robotframework-agent-plugins
```

See [Codex plugin docs](https://developers.openai.com/codex/plugins).

### Other agents

An agent that supports Agent Plugins can load a plugin folder such as [`plugins/robotcode/`](plugins/robotcode/) as it is, but how it installs one differs: from a marketplace, a Git repository or a local folder. For agents with plugin marketplaces, the pattern is usually the same:

1. Register the marketplace by repository — `<tool> plugin marketplace add robotcodedev/robotframework-agent-plugins` (or via the agent's settings / UI).
2. Install an individual plugin — `<tool> plugin install <plugin>@robotframework-agent-plugins`.

Consult your agent's documentation for the exact command name and any required preview/beta flags.

## Versions and pinning

The `main` branch holds the released state of every plugin, so installing without a ref gives you the latest release. Development happens on the `next` branch.

Every plugin release is tagged `<plugin>--v<version>`, for example `robotcode--v2.7.0`. To install a specific release, pin the marketplace to its tag:

| Agent | Pin the marketplace to a tag |
| --- | --- |
| Claude Code | `claude plugin marketplace add robotcodedev/robotframework-agent-plugins#<tag>` |
| GitHub Copilot CLI | `copilot plugin marketplace add robotcodedev/robotframework-agent-plugins#<tag>` |
| GitHub Copilot Chat (VS Code) | `"chat.plugins.marketplaces": ["robotcodedev/robotframework-agent-plugins#<tag>"]` |
| Codex | `codex plugin marketplace add robotcodedev/robotframework-agent-plugins --ref <tag>` |

Then install the plugin as usual. A pinned marketplace stays on that release and receives no updates. To switch to another release, remove the marketplace, add it again with the new tag, and reinstall the plugin.

To try unreleased changes, pin to `next` the same way.

## Repository layout

```
.plugin/marketplace.json          ← marketplace catalog (source)
.claude-plugin/marketplace.json   ← Claude Code copy (same schema, tool-specific path)
.agents/plugins/marketplace.json  ← Codex copy (different schema, tool-specific path)
plugins/
└── robotcode/
    ├── plugin.json               ← Agent Plugins manifest with $schema (source)
    ├── .plugin/plugin.json       ← legacy Open Plugins copy, without $schema
    ├── .codex-plugin/plugin.json ← legacy Codex copy, without $schema
    └── skills/robotcode/
        ├── SKILL.md
        └── references/
```

Each plugin is its own directory under `plugins/`. Its `plugin.json` follows the [Agent Plugins manifest](https://agent-plugins.org/plugin-authors/manifest), and the agents below read it first. The legacy copies in `.plugin/` and `.codex-plugin/` are for agent versions that don't read it yet, such as VS Code before 1.131, and will be dropped later. The marketplace catalog is duplicated at tool-specific paths because each agent reads only its own location:

| Tool | Marketplace path | Plugin manifest it reads |
| --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `<plugin>/plugin.json` |
| GitHub Copilot CLI | `.plugin/marketplace.json` | `<plugin>/plugin.json`, else `<plugin>/.plugin/plugin.json` |
| GitHub Copilot Chat (VS Code) | `.plugin/marketplace.json` of the repository in `chat.plugins.marketplaces` | `<plugin>/plugin.json` from VS Code 1.131 on, `<plugin>/.plugin/plugin.json` before |
| Codex | `.agents/plugins/marketplace.json` (Codex-specific schema: `source` object, `policy`, `category`, `interface`) | `<plugin>/plugin.json`, else `<plugin>/.codex-plugin/plugin.json` |

## Contributing

Contributions are welcome — new plugins, improvements to existing ones, bug reports, and docs. In short, to submit a plugin: add it under `plugins/<your-plugin>/` (with `plugin.json`, a `README.md`, and a `LICENSE`), register it in the source catalog [`.plugin/marketplace.json`](.plugin/marketplace.json), run `python scripts/sync_manifests.py` to generate the tool-specific copies, and open a PR.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide — plugin requirements, manifest generation, evals, commit conventions, and signed-commit setup. By participating you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Apache-2.0
