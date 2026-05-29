# robotframework-agent-plugins

Curated [Open Plugins](https://open-plugins.com/) marketplace for Robot Framework — Skills, hooks, and tools that extend AI coding agents (Claude Code, VS Code Copilot Chat, Cursor, Codex, OpenCode, …) with Robot Framework expertise.

## Plugins

| Plugin | What it does |
| --- | --- |
| [`robotcode`](plugins/robotcode/) | RobotCode CLI workflows: library/keyword lookup, REPL, test discovery, run, result inspection, static analysis. |

More plugins are planned — Browser Library, RequestsLibrary, and general Robot Framework patterns.

## Install

### Claude Code

```
/plugin marketplace add robotcodedev/robotframework-agent-plugins
/plugin install robotcode@robotframework-agent-plugins
```

### VS Code Copilot Chat

Add to your User Settings:

```json
"chat.plugins.marketplaces": [
	"robotcodedev/robotframework-agent-plugins"
]
```

Then install plugins from the Extensions view (Chat Plugins section).

> **Note:** The RobotCode VS Code extension already ships the `robotcode` plugin built-in (via `contributes.chatPlugins`). You only need this marketplace if you want the plugin in a different agent (Cursor, Claude Code, Codex, OpenCode), or want to mix in future plugins from this marketplace.

### Other Agents

Any tool that implements the [Open Plugin Specification](https://open-plugins.com/plugin-builders/specification) can consume this marketplace. Add the repository as a marketplace source per the tool's instructions.

## Repository layout

```
.plugin/marketplace.json   ← marketplace manifest (this catalogue)
plugins/
└── robotcode/             ← one directory per plugin
    ├── .plugin/plugin.json
    └── skills/robotcode/SKILL.md  + references/
```

The marketplace file lives in `.plugin/` per the Open Plugins spec. Each plugin's `source` in `marketplace.json` is a relative path to its directory.

## License

Apache-2.0
