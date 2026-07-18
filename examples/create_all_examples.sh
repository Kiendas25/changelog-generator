#!/bin/bash
# Create all example repositories and generate their changelogs

set -e

echo "📦 Creating example repositories..."

# Create all three examples
bash examples/create_example_simple.sh
echo ""
bash examples/create_example_monorepo.sh
echo ""
bash examples/create_example_breaking.sh

echo ""
echo "✅ All examples created!"
echo ""
echo "📁 Structure:"
echo "  example-simple/       - Basic feature/fix/chore history"
echo "  example-monorepo/     - Per-package changelogs (core, ui, api)"
echo "  example-breaking/     - Breaking changes, custom prefix (release/)"
echo ""
echo "📄 Each includes generated CHANGELOG.md"