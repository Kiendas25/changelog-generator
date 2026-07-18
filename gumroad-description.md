# Changelog Generator — Supported Pack ($12)

## What You Get

**Core Tool (Free, Forever)**
- `changelog_gen.py` — Single-file Python CLI, stdlib only
- Generates Keep a Changelog compliant CHANGELOG.md from conventional commits
- Auto-detects GitHub/GitLab remotes for commit links
- Breaking change detection (bang prefix + BREAKING CHANGE footer)
- Flexible tag prefixes (v1.0.0, release/1.0.0, custom)
- Zero config, zero deps, runs anywhere Python runs

**Supported Pack Extras ($12, One-Time)**
- ✅ **Priority Support** — Email support, 24h response SLA
- ✅ **3 Example Repositories** — Real projects with conventional commits + generated changelogs
  - `example-simple/` — Basic feature/fix/chore history
  - `example-monorepo/` — Per-package changelogs from shared history
  - `example-breaking/` — Breaking changes, footers, custom tag prefix
- ✅ **CI/CD Templates** — Drop-in workflows
  - `.github/workflows/changelog.yml` — Auto-changelog on tag push → GitHub Release
  - `.gitlab-ci.yml` — Same for GitLab
- ✅ **Pre-commit Hook** — `.pre-commit-config.yaml` to enforce conventional commits
- ✅ **VS Code Task** — `.vscode/tasks.json` → Ctrl+Shift+P → "Generate Changelog"
- ✅ **HTML Export Template** — `changelog.css` for styled HTML output
- ✅ **Lifetime Updates** — All future versions included

## Who This Is For

- **Open source maintainers** tired of manual CHANGELOG.md curation
- **DevOps engineers** automating release notes in CI/CD
- **Teams** enforcing conventional commits + wanting standard output
- **Anyone** who wants a changelog without Node.js, config files, or 50 dependencies

## What You Don't Get (And Don't Need)

- ❌ No `package.json`, `node_modules`, or JavaScript toolchain
- ❌ No YAML/TOML/JSON config files to maintain
- ❌ No plugin system, no hook API, no breaking API changes
- ❌ No subscription, no recurring fees

## Installation

```bash
# Free version — always
pip install changelog-gen
# OR no-install:
curl -sSL https://raw.githubusercontent.com/Kiendas25/changelog-generator/main/changelog_gen.py | python -

# Supported pack — includes all extras
# Purchase at: https://contentwave2.gumroad.com/l/changelog-gen
# Then unzip and drop the extras/ folder into your repo
```

## Usage

```bash
changelog-gen                          # Full changelog
changelog-gen -o docs/CHANGELOG.md     # Custom output
changelog-gen --since v1.0.0           # Since last release
changelog-gen --unreleased-only        # Draft next release notes
changelog-gen --version-prefix release/  # Custom tags
```

## License

Core tool: MIT (free forever)
Supported pack: Personal/commercial use, no redistribution of paid assets

---

**Tip jar (USDC on Solana):** `49NHJ5aUPpVwjMrHzgJt7pcYPCi7cxHUXVoEhgBPrAgE`  
**Free repo:** `github.com/Kiendas25/changelog-generator`  
**Supported pack:** `contentwave2.gumroad.com/l/changelog-gen`  
**Support:** `support@contentwave.dev`