#!/usr/bin/env python3
"""
Pre-commit hook to enforce Conventional Commits format.
Install: cp pre-commit-hook.py .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
Or use with pre-commit framework: add to .pre-commit-hooks.yaml
"""

import re
import sys

CONVENTIONAL_TYPES = {
    "feat", "fix", "docs", "style", "refactor", "perf",
    "test", "chore", "build", "ci", "revert"
}

# Regex for conventional commit message
# type(scope): subject
# type(scope)!: subject  (breaking change with bang)
COMMIT_REGEX = re.compile(
    r"^(" + "|".join(CONVENTIONAL_TYPES) + r")"
    r"(\([^)]+\))?"        # optional scope
    r"(!)?"                # optional breaking bang
    r":\s"                 # colon + space
    r".+"                  # subject (at least one char)
    r"$"
)

# Allowed merge commit patterns
MERGE_REGEX = re.compile(
    r"^(Merge (branch|pull request)|Revert\s+\").*"
)

def is_conventional_commit(msg: str) -> bool:
    """Check if commit message follows conventional commits."""
    first_line = msg.split('\n')[0].strip()
    
    # Allow merge commits
    if MERGE_REGEX.match(first_line):
        return True
    
    # Allow fixup/squash commits
    if first_line.startswith(("fixup! ", "squash! ")):
        return True
    
    return bool(COMMIT_REGEX.match(first_line))

def main():
    if len(sys.argv) < 2:
        print("Usage: commit-msg.py <commit-message-file>", file=sys.stderr)
        return 1
    
    msg_file = sys.argv[1]
    
    try:
        with open(msg_file, 'r') as f:
            message = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {msg_file}", file=sys.stderr)
        return 1
    
    if not is_conventional_commit(message):
        print("❌ Commit message does not follow Conventional Commits format.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Expected format:", file=sys.stderr)
        print("  <type>(<scope>): <subject>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Types:", ", ".join(sorted(CONVENTIONAL_TYPES)), file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  feat(api): add user authentication", file=sys.stderr)
        print("  fix: resolve login timeout", file=sys.stderr)
        print("  docs: update README with examples", file=sys.stderr)
        print("  refactor!(core): migrate to new API", file=sys.stderr)
        print("", file=sys.stderr)
        print("Breaking changes: add '!' after type/scope or include 'BREAKING CHANGE:' in body", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())