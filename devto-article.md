---
title: "Stop Writing Changelogs by Hand. Your Git History Already Has Them."
description: "A zero-dependency Python CLI that generates Keep a Changelog compliant CHANGELOG.md from conventional commits. No Node, no config, single file."
tags: ["python", "cli", "git", "changelog", "conventional-commits", "devops", "opensource"]
series: "DevTools Worth Stealing"
---

You tag `v1.3.0`. CI passes. You open the release draft.

Now you need the changelog.

**Option A:** Scroll through 47 commits. Copy subjects. Group by type. Format Markdown. Link each commit. Find breaking changes. Spend 20 minutes. Ship.

**Option B:**
```bash
changelog-gen
```

Done. Professional `CHANGELOG.md` appears. Categorized (Features, Fixes, Performance, Breaking, Docs...). Linked to GitHub commits. Keep a Changelog compliant. SemVer grouped.

---

## Why This Exists

Every tool in this space requires Node.js:

| Tool | Config | Dependencies |
|------|--------|--------------|
| `auto-changelog` | Medium | 15+ (Node) |
| `standard-version` | High | 20+ (Node) |
| `release-it` | High | 30+ (Node) |
| **changelog-gen** | **Zero** | **0 (Python stdlib)** |

`changelog-gen` is:
- **Zero config** — runs on any git repo with conventional commits
- **Zero dependencies** — Python stdlib only, single ~200 line file
- **CI-native** — one step in GitHub Actions, GitLab CI, anything
- **Standard output** — Keep a Changelog format, SemVer grouping

---

## Quick Start

```bash
# No install needed
curl -sSL https://raw.githubusercontent.com/Kiendas25/changelog-generator/main/changelog_gen.py | python -

# Or install
pip install changelog-gen

# Generate
changelog-gen
```

Output: `CHANGELOG.md` with sections like:

```markdown
## [Unreleased]

### Features
- **feat(auth):** add Google OAuth provider [[a1b2c3d]](https://github.com/you/repo/commit/a1b2c3d)

### Bug Fixes
- **fix(api):** handle 429 rate limit on /search [[d4e5f6g]](https://github.com/you/repo/commit/d4e5f6g)

### Code Refactoring
- **refactor(core)!:** drop Python 3.7 support [[k1l2m3n]](https://github.com/you/repo/commit/k1l2m3n)
  ⚠️ **BREAKING CHANGE:** Python 3.7 is no longer supported

## [1.2.0] - 2024-03-15
...
```

---

## Conventional Commits → Changelog

The tool parses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): subject          → Features
fix(scope): subject           → Bug Fixes
perf(scope): subject          → Performance
refactor(scope)!: subject     → Refactoring + ⚠️ BREAKING
docs(scope): subject          → Documentation
```

Breaking changes detected two ways:
```bash
# 1. Bang prefix
feat(api)!: change response format

# 2. Body/footer
feat(api): change response format

BREAKING CHANGE: response is now {data: {...}}
```

Both render as ⚠️ **BREAKING CHANGE** in the changelog.

---

## CI/CD Integration

### GitHub Actions (auto on tag)

```yaml
# .github/workflows/changelog.yml
on:
  push:
    tags: ['v*']

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: pip install changelog-gen
      - run: changelog-gen -o CHANGELOG.md
      - uses: softprops/action-gh-release@v1
        with:
          body_path: CHANGELOG.md
```

Tag `v1.3.0` → Release drafted with full changelog. Automatic.

### GitLab CI

```yaml
# .gitlab-ci.yml
changelog:
  stage: release
  script:
    - pip install changelog-gen
    - changelog-gen -o CHANGELOG.md
  only:
    - tags
```

---

## Advanced Usage

**Release notes for stakeholders:**
```bash
changelog-gen --since v2.0.0 --until v2.1.0 -o release-notes.md
```
Clean, categorized, linked. Paste into Notion/Confluence/email.

**Monorepo — per-package changelogs:**
```bash
cd packages/api && changelog-gen -o ../../docs/api-changelog.md
cd packages/web && changelog-gen -o ../../docs/web-changelog.md
```

**Drafting next release — unreleased only:**
```bash
changelog-gen --unreleased-only
```
Perfect for "what's shipping next week?" standups.

**Custom tag prefix (`release/1.0.0` instead of `v1.0.0`):**
```bash
changelog-gen --version-prefix release/
```

**Auto-detected commit links:**
- `git@github.com:user/repo.git` → `https://github.com/user/repo/commit/<sha>`
- `https://gitlab.com/user/repo.git` → `https://gitlab.com/user/repo/-/commit/<sha>`

Click through from changelog to exact commit. 🔗

---

## Free vs Supported

**Free (MIT, forever):**
- `changelog_gen.py` — the complete CLI
- All features above
- Copy, vendor, fork, audit

**Supported Pack ($12, one-time):**
- Priority email support (24h SLA)
- 3 example repos with conventional commits + generated output
- GitHub Actions workflow (auto-changelog on tag → release)
- GitLab CI config
- Pre-commit hook (enforce conventional commits)
- VS Code task (Ctrl+Shift+P → Generate Changelog)
- HTML export CSS template
- Lifetime updates

[**Get the Supported Pack →**](https://contentwave2.gumroad.com/l/changelog-gen)

---

## Why Not Other Tools?

> "I just want a changelog. I don't want a Node project for a text file."

`changelog-gen` is ~200 lines of Python stdlib. Read it in 30 seconds. Vendor it. Run it in a distroless container. No `package.json`, no `node_modules`, no config files.

Built because I got tired of:
- "Bug fixes and improvements" release notes
- Manually curating `CHANGELOG.md`
- Node-heavy toolchains for a text file

Now every repo I touch has a real changelog. Yours can too.

---

## Try It Now

```bash
curl -sSL https://raw.githubusercontent.com/Kiendas25/changelog-generator/main/changelog_gen.py | python -
```

Drop a ⭐ if it saves you time: **https://github.com/Kiendas25/changelog-generator**

---

**Tip jar (USDC on Solana):** `49NHJ5aUPpVwjMrHzgJt7pcYPCi7cxHUXVoEhgBPrAgE`  
**Free version:** `github.com/Kiendas25/changelog-generator`  
**Supported pack ($12):** `contentwave2.gumroad.com/l/changelog-gen`  
**Support:** `support@contentwave.dev`