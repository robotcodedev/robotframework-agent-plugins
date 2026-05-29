# robotframework-agent-plugins

A curated [Open Plugins](https://open-plugins.com/) marketplace for Robot Framework — Skills, hooks, and tools that extend AI coding agents (Claude Code, GitHub Copilot, Codex, OpenCode, …) with Robot Framework expertise.

## Plugins in this marketplace

| Plugin | What it does |
| --- | --- |
| [`robotcode`](plugins/robotcode/) | RobotCode CLI workflows: library/keyword lookup via `libdoc`, interactive REPL, test discovery, run, result inspection, and static analysis. |

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
codex plugin install robotcode@robotframework-agent-plugins
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
.claude-plugin/marketplace.json   ← Claude-specific copy (Claude Code only reads this path)
plugins/
└── robotcode/
    ├── .plugin/plugin.json
    └── skills/robotcode/
        ├── SKILL.md
        └── references/
```

Each plugin is its own directory under `plugins/` with an Open-Plugin-shaped `.plugin/` manifest. The marketplace manifest is mirrored at two paths because Claude Code only looks at `.claude-plugin/marketplace.json` and does not fall back to the vendor-neutral `.plugin/` location that other tools (Copilot CLI, Codex) read.

## Contributing

Plugins are reviewed for quality, accurate documentation, and license compatibility with Apache-2.0. To submit a plugin:

1. Add your plugin under `plugins/<your-plugin>/` with at minimum:
   - `.plugin/plugin.json` (Open Plugins spec manifest, `"license": "Apache-2.0"`).
   - A skill, agent, hook, or MCP/LSP config — whatever the plugin provides.
   - A `README.md` describing what it does, prerequisites, and how the agent activates it.
   - A `LICENSE` file (Apache-2.0 — copy the one at the repo root) so the plugin stays self-contained when an agent caches it independently of this marketplace.
2. Register the plugin in **both** marketplace manifests — `.plugin/marketplace.json` and `.claude-plugin/marketplace.json`. The two files must stay byte-identical.
3. Open a PR.

## License

Apache-2.0
