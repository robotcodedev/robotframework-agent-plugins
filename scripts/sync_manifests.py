#!/usr/bin/env python3
"""Sync marketplace and plugin manifests across tool-specific paths.

Sources of truth (edit these):
- .plugin/marketplace.json                    Open Plugins catalog manifest.
- plugins/<name>/.plugin/plugin.json          Open Plugins per-plugin manifest.

Generated (do not edit by hand — re-run this script):
- .claude-plugin/marketplace.json             Byte-identical copy for Claude Code.
- .agents/plugins/marketplace.json            Codex catalog (different schema).
- plugins/<name>/.codex-plugin/plugin.json    Byte-identical copy for Codex.

Usage:
    python scripts/sync_manifests.py            # apply (writes generated files)
    python scripts/sync_manifests.py --check    # exit 1 on drift; do not modify files
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SOURCE_MARKETPLACE = REPO_ROOT / ".plugin" / "marketplace.json"
CLAUDE_MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"

# Codex catalog defaults. When adding a plugin, register its category here so
# the Codex listing has the right label; otherwise CODEX_DEFAULT_CATEGORY wins.
CODEX_MARKETPLACE_DISPLAY_NAME = "Robot Framework Agent Plugins"
CODEX_PLUGIN_CATEGORIES = {
    "robotcode": "Developer Tools",
}
CODEX_DEFAULT_CATEGORY = "Developer Tools"
CODEX_DEFAULT_POLICY = {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL",
}


def die(msg: str) -> None:
    print(f"sync-manifests: {msg}", file=sys.stderr)
    sys.exit(1)


def plugin_dir(source_path: str) -> Path:
    return (REPO_ROOT / source_path.lstrip("./")).resolve()


def codex_marketplace_from(src: dict) -> dict:
    return {
        "name": src["name"],
        "interface": {"displayName": CODEX_MARKETPLACE_DISPLAY_NAME},
        "plugins": [
            {
                "name": p["name"],
                "source": {
                    "source": "local",
                    "path": p["source"].rstrip("/"),
                },
                "policy": CODEX_DEFAULT_POLICY,
                "category": CODEX_PLUGIN_CATEGORIES.get(p["name"], CODEX_DEFAULT_CATEGORY),
            }
            for p in src["plugins"]
        ],
    }


def dump_json(obj: dict) -> str:
    return json.dumps(obj, indent="\t") + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 on drift; do not modify files.",
    )
    args = ap.parse_args()

    if not SOURCE_MARKETPLACE.is_file():
        die(f"missing source: {SOURCE_MARKETPLACE.relative_to(REPO_ROOT)}")

    source_text = SOURCE_MARKETPLACE.read_text()
    source_data = json.loads(source_text)

    targets: dict[Path, str] = {
        CLAUDE_MARKETPLACE: source_text,
        CODEX_MARKETPLACE: dump_json(codex_marketplace_from(source_data)),
    }

    for entry in source_data["plugins"]:
        pdir = plugin_dir(entry["source"])
        src_plugin = pdir / ".plugin" / "plugin.json"
        codex_plugin = pdir / ".codex-plugin" / "plugin.json"
        if not src_plugin.is_file():
            die(f"missing source: {src_plugin.relative_to(REPO_ROOT)}")
        targets[codex_plugin] = src_plugin.read_text()

    drift: list[Path] = []
    for path, content in targets.items():
        existing = path.read_text() if path.is_file() else None
        if existing != content:
            drift.append(path)

    if args.check:
        if drift:
            print("manifest drift detected:", file=sys.stderr)
            for p in drift:
                print(f"  {p.relative_to(REPO_ROOT)}", file=sys.stderr)
            print("run `python scripts/sync_manifests.py`", file=sys.stderr)
            return 1
        print("manifests in sync")
        return 0

    if not drift:
        print("manifests already in sync")
        return 0

    for path in drift:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(targets[path])
        print(f"wrote {path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
