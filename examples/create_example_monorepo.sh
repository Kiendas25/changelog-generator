#!/bin/bash
# Example: Monorepo with per-package changelogs
# Run this to create the example repo and generate changelogs

set -e

REPO_DIR="example-monorepo"
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

git init -q
git config user.email "demo@example.com"
git config user.name "Demo User"

# Root files
echo "# Monorepo Example" > README.md
git add README.md
git commit -q -m "chore: init monorepo"

# Package: core
mkdir -p packages/core
echo "export function core() { return 'core'; }" > packages/core/index.js
git add packages/core
git commit -q -m "feat(core): add core module"
git tag core@v1.0.0

echo "export function helper() { return 'helper'; }" >> packages/core/index.js
git add packages/core
git commit -q -m "feat(core): add helper function"
git commit -q -m "fix(core): handle edge case"
git tag core@v1.1.0

# Package: ui
mkdir -p packages/ui
echo "export function Button() { return '<button>'; }" > packages/ui/index.js
git add packages/ui
git commit -q -m "feat(ui): add button component"
git tag ui@v1.0.0

# Package: api
mkdir -p packages/api
echo "export function fetchData() { return Promise.resolve({}); }" > packages/api/index.js
git add packages/api
git commit -q -m "feat(api): add data fetching"
git commit -q -m "fix(api): retry on timeout"
git tag api@v1.0.0

# Generate per-package changelogs
cd ..
for pkg in core ui api; do
    echo "📦 Generating changelog for $pkg..."
    python changelog_gen.py --version-prefix "$pkg@" -o "$REPO_DIR/packages/$pkg/CHANGELOG.md"
done

# Also generate root changelog
python changelog_gen.py -o "$REPO_DIR/CHANGELOG.md"

echo "✅ Created $REPO_DIR with packages: core, ui, api"
echo "📄 Generated per-package CHANGELOG.md files"