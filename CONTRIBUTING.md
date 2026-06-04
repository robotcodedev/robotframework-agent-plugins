<!-- omit in toc -->
# Contributing to Robot Framework Agent Plugins

First off, thanks for taking the time to contribute!

All types of contributions are encouraged and valued. See the [Table of Contents](#table-of-contents) for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved. The community looks forward to your contributions.

**New here? Find your path:**

- Have a question → [I Have a Question](#i-have-a-question)
- Found a bug → [Reporting Bugs](#reporting-bugs)
- Have an idea → [Suggesting Enhancements](#suggesting-enhancements)
- Want to add or change a plugin → [Contributing a Plugin](#contributing-a-plugin)

One short ground rule applies to everything — please skim our note on [payment and bounty requests](#payment-bounty-and-monetization-requests). Everything after that is about *how* to contribute.

And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support the project and show your appreciation, which we would also be very happy about:
- Star the project
- Tweet about it
- Refer this project in your project's readme
- Mention the project at local meetups and tell your friends/colleagues

<!-- omit in toc -->
## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [I Have a Question](#i-have-a-question)
- [Project-Wide Rules](#project-wide-rules)
  - [Payment, Bounty, and Monetization Requests](#payment-bounty-and-monetization-requests)
- [I Want To Contribute](#i-want-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Contributing a Plugin](#contributing-a-plugin)
    - [Development Environment Setup](#development-environment-setup)
    - [Plugin Requirements](#plugin-requirements)
    - [Registering and Generating Manifests](#registering-and-generating-manifests)
    - [Testing and Evaluating Your Plugin](#testing-and-evaluating-your-plugin)
    - [Pull Request Guidelines](#pull-request-guidelines)
  - [Improving The Documentation](#improving-the-documentation)
- [Styleguides](#styleguides)
  - [Commit Messages](#commit-messages)
  - [Signed Commits Required](#signed-commits-required)
- [Join The Project Team](#join-the-project-team)


## Code of Conduct

This project and everyone participating in it is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable behavior
to <support@robotcode.io>.


## I Have a Question

Before you ask a question, it is best to search the existing [Issues](https://github.com/robotcodedev/robotframework-agent-plugins/issues) and read the [marketplace README](README.md) and the README of the plugin you have in mind (e.g. [`plugins/robotcode/`](plugins/robotcode/)). In case you have found a suitable issue and still need clarification, you can write your question in that issue.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/robotcodedev/robotframework-agent-plugins/issues/new).
- Provide as much context as you can about what you're running into.
- Provide relevant versions: which agent and version (Claude Code, Copilot, Codex, …), the plugin, and your platform.

We will then take care of the issue as soon as possible.

You can also ask questions in the Robot Framework [Slack](https://robotframework.slack.com) or in the [Robot Framework Forum](https://forum.robotframework.org).

## Project-Wide Rules

Just one ground rule, and it applies to every interaction with this project — pull requests, issues, discussions, comments, code review replies, and anything else. It's short; please read it before opening a contribution of any kind.

### Payment, Bounty, and Monetization Requests

This is an open-source project, not a lead-generation or micro-bounty platform.

Do not include payment links, invoices, donation requests, wallet addresses, "paid fix" notes, bounty claims, sponsorship requests, or similar monetization requests in pull requests, issues, discussions, comments, or any other project interaction unless paid work or a bounty process was explicitly agreed with the maintainers before the work started.

Unsolicited monetization requests attached to contributions are not accepted. Pull requests containing such requests may be closed without review, and issues or discussions containing such requests may be declined or closed.

If a contribution is part of an agreed paid engagement, sponsored work, or bounty process, disclose that context clearly and follow the agreed process. Do not add ad-hoc payment requests to the contribution body.

Contributions are reviewed on their technical merit, usefulness to users, and compliance with the project's contribution standards — not on payment requests attached to them.

## I Want To Contribute

> [!IMPORTANT]
> **Legal Notice**
>
> When contributing to this project, you must agree that you have the right to submit the contribution under the project license ([Apache-2.0](LICENSE)).
>
> This means that the contribution was created in whole or in part by you, is based on previous work that you are allowed to submit under a compatible license, or was otherwise lawfully provided to you for contribution.
>
> This corresponds to the spirit of the [Developer Certificate of Origin](https://developercertificate.org/). You are encouraged to add a DCO sign-off to your commits with `git commit -s` — this only adds a `Signed-off-by` trailer and is separate from the cryptographic commit signature (`-S`, GPG/SSH) required by [Signed Commits Required](#signed-commits-required) below.

### Reporting Bugs

<!-- omit in toc -->
#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version of the plugin and your agent.
- Determine if your bug is really a bug and not an error on your side — for instance, whether your agent currently [supports the Open Plugin spec](https://open-plugins.com/supported-agents), or whether the underlying tool the plugin drives (e.g. `robotcode`) is installed and working.
- To see if other users have experienced (and potentially already solved) the same issue, check the [issue tracker](https://github.com/robotcodedev/robotframework-agent-plugins/issues).
- Collect information about the bug:
  - The agent and version (Claude Code, Copilot CLI, Copilot Chat, Codex, …).
  - The plugin and the marketplace ref/version you installed.
  - OS, platform, and version.
  - The prompt or action that triggered it, and what the agent did versus what you expected.
  - Can you reliably reproduce the issue?

<!-- omit in toc -->
#### How Do I Submit a Good Bug Report?

> [!WARNING]
> Never report security related issues, vulnerabilities or bugs including sensitive information to the issue tracker, or elsewhere in public. Send sensitive bugs by email to <support@robotcode.io> instead.

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an [Issue](https://github.com/robotcodedev/robotframework-agent-plugins/issues/new).
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the *reproduction steps* that someone else can follow to recreate the issue on their own — ideally the exact prompt you gave the agent and the commands it ran.
- Provide the information you collected in the previous section.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, **including completely new plugins, new behaviors for an existing skill, and minor improvements**. Following these guidelines helps maintainers and the community understand your suggestion and find related ones.

<!-- omit in toc -->
#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [marketplace README](README.md) and the relevant plugin's README and skill files to find out whether the behavior is already covered.
- Perform a [search](https://github.com/robotcodedev/robotframework-agent-plugins/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits the scope of this marketplace: plugins that teach AI coding agents to work well with Robot Framework and its ecosystem. If your idea is narrowly specific to your own setup, consider keeping it as a private plugin.

<!-- omit in toc -->
#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/robotcodedev/robotframework-agent-plugins/issues).

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
- For a skill behavior change, include the **prompt** you gave the agent and the behavior you want it to exhibit — that maps directly onto an [eval case](#testing-and-evaluating-your-plugin).
- **Explain why this enhancement would be useful** to most users of the plugin.

### Contributing a Plugin

Plugins are reviewed for quality, accurate documentation, and license compatibility with Apache-2.0. This section walks you through adding a new plugin or changing an existing one.

#### Development Environment Setup

This is a content repository — plugins, manifests, and docs — not a compiled project. You only need:

1. **Prerequisites:**
   - [Git](https://git-scm.com/).
   - [Python](https://www.python.org/) 3 — only to run the manifest generator. It uses the standard library only; there is nothing to `pip install`.
   - The target agent(s) you want to test against (e.g. [Claude Code](https://code.claude.com/docs/en/plugin-marketplaces)).

2. **Setup:**
   ```sh
   git clone https://github.com/robotcodedev/robotframework-agent-plugins.git
   cd robotframework-agent-plugins
   ```

See [Repository layout](README.md#repository-layout) in the README for how the source-of-truth manifests relate to the generated, tool-specific copies.

#### Plugin Requirements

Add your plugin under `plugins/<your-plugin>/` with at minimum:

- `.plugin/plugin.json` — [Open Plugins spec](https://open-plugins.com/plugin-builders/specification) manifest, with `"license": "Apache-2.0"`.
- A skill, agent, hook, or MCP/LSP config — whatever the plugin provides.
- A `README.md` describing what it does, prerequisites, and how the agent activates it.
- A `LICENSE` file (Apache-2.0 — copy the one at the [repo root](LICENSE)) so the plugin stays self-contained when an agent caches it independently of this marketplace.

Use the existing [`plugins/robotcode/`](plugins/robotcode/) plugin as a reference for structure.

#### Registering and Generating Manifests

The marketplace and plugin manifests are duplicated at tool-specific paths because each agent reads only its own location. You edit the **source** manifests; a script generates the rest — never hand-edit a generated file.

1. Register the plugin once in the **source** marketplace catalog [`.plugin/marketplace.json`](.plugin/marketplace.json) (Open Plugins schema).
2. If your plugin needs a Codex category other than the default, add it to `CODEX_PLUGIN_CATEGORIES` in [`scripts/sync_manifests.py`](scripts/sync_manifests.py).
3. Run the manifest generator to populate the Claude and Codex copies:
   ```sh
   python scripts/sync_manifests.py
   ```
   This writes `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, and each `plugins/<name>/.codex-plugin/plugin.json`.
4. Verify nothing drifted before you push:
   ```sh
   python scripts/sync_manifests.py --check
   ```
   This exits non-zero if a generated file is out of sync with its source — the same check CI runs.

#### Testing and Evaluating Your Plugin

For skill plugins, behavior is the thing under test: does an agent with the skill loaded reach for the right commands and avoid the habits the skill warns against? The [`evals/`](evals/) directory holds behavioral test cases and a harness for exactly this.

- Try your change manually first — open a fresh agent session with the plugin installed and run a realistic prompt.
- For the `robotcode` plugin, see [`evals/robotcode/README.md`](evals/robotcode/README.md) for the case format and the `run.py` harness, and **test across the models you ship for** (Haiku, Sonnet, Opus).
- When you change skill behavior, re-run the affected cases and **add a new case** for any behavior the skill should enforce but doesn't yet. Evals are the source of truth for skill changes.

#### Pull Request Guidelines

<!-- omit in toc -->
##### PR Checklist

Before submitting your pull request, make sure that:

- [ ] The change is **focused** on a single concern (no unrelated edits or formatting noise).
- [ ] Each plugin still has its required files — [`.plugin/plugin.json`](README.md#repository-layout), `README.md`, and a `LICENSE` (Apache-2.0).
- [ ] **Generated manifests are in sync** — you ran `python scripts/sync_manifests.py` and `python scripts/sync_manifests.py --check` passes. Generated files were regenerated by the script, not edited by hand.
- [ ] **Behavior was checked** — for skill changes, the relevant [evals](#testing-and-evaluating-your-plugin) were run (and a new case added if appropriate).
- [ ] **Documentation** was updated where relevant (plugin README, marketplace README).
- [ ] **Commits** follow [Conventional Commits](#commit-messages) and are [cryptographically signed](#signed-commits-required) (`git commit -S`, GPG/SSH).
- [ ] No payment, bounty, or monetization requests are attached (see [Payment, Bounty, and Monetization Requests](#payment-bounty-and-monetization-requests)).

<!-- omit in toc -->
##### PR Description

A good PR description:
- Explains **what** changed and **why**.
- References any related issues (e.g. `Fixes #123`).
- For a new plugin, summarizes what it does and which agents it targets.
- For a skill behavior change, notes which eval cases you ran and their outcome.

<!-- omit in toc -->
##### PR Review Process

- Automated checks must pass (including `sync_manifests.py --check`).
- At least one maintainer review is required.
- Address feedback promptly.
- Keep your PR up to date with the main branch.

### Improving The Documentation

Documentation is crucial for helping users understand and use these plugins effectively. The docs in this repository are:

- The [marketplace README](README.md) — install instructions per agent, repository layout, and the plugin list.
- Each plugin's `README.md` — what it does, prerequisites, and how the agent activates it.
- The skill content itself (e.g. `plugins/robotcode/skills/robotcode/`) — `SKILL.md` and its `references/`, which *are* the user-facing instructions the agent reads.
- The eval READMEs under [`evals/`](evals/).

Keep documentation clear, concise, and accurate. Verify that any command you document actually works, and prefer linking related concepts over repeating them. Small fixes can go straight to a pull request; for larger restructuring, open an issue first to discuss the approach.

## Styleguides
### Commit Messages

Good commit messages help maintain a clean project history and make it easier to understand changes. This repository uses [Conventional Commits](https://www.conventionalcommits.org/).

<!-- omit in toc -->
#### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

<!-- omit in toc -->
#### Types

- **feat:** A new plugin or a new capability for an existing one.
- **fix:** A bug fix.
- **docs:** Documentation only changes (READMEs, skill references).
- **refactor:** A change that neither fixes a bug nor adds a feature.
- **test:** Adding or correcting evals.
- **chore:** Tooling, manifests, and repository maintenance.

<!-- omit in toc -->
#### Scope

The scope should indicate the plugin or area affected — for example the plugin name (`robotcode`), `marketplace`, `scripts`, or `evals`.

<!-- omit in toc -->
#### Examples

```
feat(robotcode): teach the skill to use the command-line debugger

Add guidance and an eval case so the agent drives robotcode's
debugger non-interactively instead of editing the test.
```

```
fix: also publish marketplace at .claude-plugin/marketplace.json

Claude Code reads the marketplace from .claude-plugin/, which the
generator was not writing.
```

```
docs(robotcode): add per-plugin README
```

<!-- omit in toc -->
#### Guidelines

- **Subject line:** 50 characters or less, imperative mood ("add" not "added").
- **Body:** Wrap at 72 characters, explain what and why (not how).
- **Footer:** Reference issues and breaking changes.
- **Breaking changes:** Start footer with "BREAKING CHANGE:" followed by a description.

### Signed Commits Required

**All commits and pull requests must be signed** to be accepted into the project. This helps ensure the authenticity and integrity of the codebase.

This refers to the **cryptographic commit signature** (`git commit -S`, GPG/SSH/X.509) — not to be confused with the DCO `Signed-off-by` trailer (`git commit -s`) mentioned in the [Legal Notice](#i-want-to-contribute).

**Setting up commit signing:**

The simplest setup is SSH signing — reuse the SSH key you already use for GitHub (or create one), no GPG toolchain needed:

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub   # your public key
git config --global commit.gpgsign true
```

Then add that key on GitHub once more as a **Signing Key** under *Settings → SSH and GPG keys*. Every commit is now signed automatically — verify with `git log --show-signature`.

Prefer GPG (or already have a GPG key)? Follow GitHub's [Managing commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification) guide, then set `commit.gpgsign true` the same way.

**For pull requests:**
- All commits in the PR must be signed.
- You can sign previous commits using: `git rebase --exec 'git commit --amend --no-edit -S' -i HEAD~<number-of-commits>`.

## Join The Project Team

We're always looking for dedicated contributors! If you've been actively contributing and are interested in taking on more responsibility, here's how you can get involved:

### Ways to Get More Involved

**Regular Contributors:**
- Consistently submit high-quality pull requests.
- Help with reviews and testing.
- Assist in triaging and responding to issues.
- Contribute to documentation improvements.

**Maintainer Responsibilities:**
- Review and merge pull requests.
- Manage releases and versioning.
- Guide project direction and roadmap.
- Mentor new contributors.

### How to Apply

If you're interested in joining the project team:

1. **Build a track record** of meaningful contributions over time.
2. **Engage with the community** by helping other users and contributors.
3. **Reach out** to existing maintainers via email at <support@robotcode.io>.
4. **Express your interest** in specific areas where you'd like to contribute more.

### What We Look For

- **Technical expertise** in relevant areas (Robot Framework, AI coding agents, skill authoring).
- **Communication skills** for working with contributors and users.
- **Reliability** in following through on commitments.
- **Collaborative mindset** and willingness to help others.
- **Alignment** with project goals and values.

We value diversity and welcome contributors from all backgrounds. This project benefits from different perspectives and experiences.
