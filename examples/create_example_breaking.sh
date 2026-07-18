#!/bin/bash
# Example: Repository with breaking changes, custom footers, and custom tag prefix
# Run this to create the example repo and generate its changelog

set -e

REPO_DIR="example-breaking"
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

git init -q
git config user.email "demo@example.com"
git config user.name "Demo User"

echo "# Breaking Changes Example" > README.md
git add README.md
git commit -q -m "chore: init project"

# release/1.0.0 (custom prefix)
echo "module.exports = { version: '1.0.0' };" > package.js
git add package.js
git commit -q -m "feat: initial release"
git tag release/1.0.0

# release/1.1.0
echo "module.exports = { version: '1.1.0', api: 'v1' };" > package.js
git add package.js
git commit -q -m "feat(config): add api version config"
git commit -q -m "fix(build): resolve dependency conflict"
git tag release/1.1.0

# release/2.0.0 - major breaking
echo "module.exports = { version: '2.0.0', api: 'v2', breaking: true };" > package.js
git add package.js
git commit -q -m "feat!: migrate to v2 API"
git commit -q -m "BREAKING CHANGE: config schema changed, migration guide at docs/migration.md"
git commit -q -m "refactor(internal): modernize internals"
git commit -q -m "docs: add migration guide"
git tag release/2.0.0

# release/2.1.0
echo "module.exports = { version: '2.1.0', api: 'v2', features: ['a', 'b'] };" > package.js
git add package.js
git commit -q -m "feat: add feature flags"
git commit -q -m "fix(security): sanitize user input"
git tag release/2.1.0

# Unreleased
echo "module.exports = { version: '2.2.0-dev' };" > package.js
git add package.js
git commit -q -m "feat(experimental): add beta feature"

# Generate changelog with custom prefix
cd ..
python changelog_gen.py --version-prefix release/ -o "$REPO_DIR/CHANGELOG.md"

echo "✅ Created $REPO_DIR with tags: release/1.0.0, release/1.1.0, release/2.0.0, release/2.1.0"
echo "📄 Generated CHANGELOG.md with breaking change detection"