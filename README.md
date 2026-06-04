# robotframework-agent-plugins

A curated [Open Plugins](https://open-plugins.com/) marketplace for Robot Framework — Skills (and more plugin components over time) that extend AI coding agents like Claude Code, GitHub Copilot, and Codex with Robot Framework expertise.

## Plugins in this marketplace

| Plugin | What it does |
| --- | --- |
| [`robotcode`](plugins/robotcode/) | Teaches AI coding agents to drive `robotcode` properly in Robot Framework projects. |

More plugins are planned — Browser Library, RequestsLibrary, and general Robot Framework patterns.

## Before you install

Plugins from this marketplace follow the [Open Plugin Specification](https://open-plugins.com/plugin-builders/specification). Check whether your agent currently supports the spec at <https://open-plugins.com/supported-agents>. If it doesn't, the marketplace files in this repo will not be discovered — even if the plugin contents themselves would work standalone.

Every agent uses its own command surface to add a marketplace and install a plugin. Pick the section for your agent below.

## Install per agent

### Claude Code

```sh
claude plugin marketplace add robotcodedev/robotframework-agent-plugins
claude plugin install robotcode@robotframework-agent-plugins
```

Update with `claude plugin marketplace update` once the marketplace is registered. See [Claude Code plugin docs](https://code.claude.com/docs/en/plugin-marketplaces) for version pinning (`@<ref>`) and uninstall.

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

### Other Open-Plugins-compliant agents

If your agent implements the Open Plugin spec but isn't listed above, the install pattern is usually the same shape:

1. Register the marketplace by repository — `<tool> plugin marketplace add robotcodedev/robotframework-agent-plugins` (or via the agent's settings / UI).
2. Install an individual plugin — `<tool> plugin install <plugin>@robotframework-agent-plugins`.

Consult your agent's documentation for the exact command name and any required preview/beta flags.

## Repository layout

```
.plugin/marketplace.json          ← Open Plugins spec marketplace manifest
.claude-plugin/marketplace.json   ← Claude Code copy (same schema, tool-specific path)
.agents/plugins/marketplace.json  ← Codex copy (different schema, tool-specific path)
plugins/
└── robotcode/
    ├── .plugin/plugin.json       ← Open Plugins manifest
    ├── .codex-plugin/plugin.json ← Codex copy (same data, tool-specific path)
    └── skills/robotcode/
        ├── SKILL.md
        └── references/
```

Each plugin is its own directory under `plugins/`. The marketplace manifest and per-plugin manifest are duplicated at tool-specific paths because each agent reads only its own location:

| Tool | Marketplace path | Plugin manifest path | Schema |
| --- | --- | --- | --- |
| Open Plugins (Copilot CLI, …) | `.plugin/marketplace.json` | `<plugin>/.plugin/plugin.json` | Open Plugins spec |
| Claude Code | `.claude-plugin/marketplace.json` | `<plugin>/.claude-plugin/plugin.json` (if present, else `.plugin/`) | same as Open Plugins |
| Codex | `.agents/plugins/marketplace.json` | `<plugin>/.codex-plugin/plugin.json` | Codex-specific (`source` object, `policy`, `category`, `interface`) |

## Contributing

Contributions are welcome — new plugins, improvements to existing ones, bug reports, and docs. In short, to submit a plugin: add it under `plugins/<your-plugin>/` (with `.plugin/plugin.json`, a `README.md`, and a `LICENSE`), register it in the source catalog [`.plugin/marketplace.json`](.plugin/marketplace.json), run `python scripts/sync_manifests.py` to generate the tool-specific copies, and open a PR.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide — plugin requirements, manifest generation, evals, commit conventions, and signed-commit setup. By participating you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Apache-2.0
