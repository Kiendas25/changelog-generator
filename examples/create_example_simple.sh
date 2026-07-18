#!/bin/bash
# Example: Simple repository with conventional commits
# Run this to create the example repo and generate its changelog

set -e

REPO_DIR="example-simple"
rm -rf "$REPO_DIR"
mkdir "$REPO_DIR"
cd "$REPO_DIR"

git init -q
git config user.email "demo@example.com"
git config user.name "Demo User"

# Initial commit
echo "# Simple Project" > README.md
git add README.md
git commit -q -m "chore: initial commit"

# v1.0.0
echo "console.log('hello');" > index.js
git add index.js
git commit -q -m "feat: add hello world feature"
git tag v1.0.0

# v1.1.0
echo "console.log('feature added');" >> index.js
git add index.js
git commit -q -m "feat(cli): add verbose flag"
git commit -q -m "fix: handle empty input gracefully"
git commit -q -m "docs: update readme with usage"
git tag v1.1.0

# v2.0.0 (breaking)
echo "// BREAKING: new API" > index.js
echo "export function hello(name) { return 'Hello, ' + name; }" >> index.js
git add index.js
git commit -q -m "feat!: migrate to ES modules"
git commit -q -m "BREAKING CHANGE: default export changed to named export"
git tag v2.0.0

# Unreleased
echo "// New feature coming" >> index.js
git add index.js
git commit -q -m "feat: add greeting customization"

# Generate changelog
cd ..
python changelog_gen.py --version-prefix v -o "$REPO_DIR/CHANGELOG.md"

echo "✅ Created $REPO_DIR with tags: v1.0.0, v1.1.0, v2.0.0"
echo "📄 Generated CHANGELOG.md"