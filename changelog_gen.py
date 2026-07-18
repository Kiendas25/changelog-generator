#!/usr/bin/env python3
"""
changelog_gen.py — Generate CHANGELOG.md from conventional commit git history.

Zero dependencies. Stdlib only. Single file.

Usage:
    changelog-gen                          # Full changelog
    changelog-gen -o docs/CHANGELOG.md     # Custom output
    changelog-gen --since v1.0.0           # Since last release
    changelog-gen --unreleased-only        # Draft next release notes
    changelog-gen --version-prefix release/  # Custom tags
    changelog-gen --format json            # JSON output
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


# ─── Conventional Commit Types ───
CONVENTIONAL_TYPES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "style": "Styles",
    "refactor": "Code Refactoring",
    "perf": "Performance Improvements",
    "test": "Tests",
    "chore": "Chores",
    "build": "Build System",
    "ci": "Continuous Integration",
    "revert": "Reverts",
}

BREAKING_CHANGE_TYPE = "BREAKING CHANGES"


@dataclass
class Commit:
    hash: str
    short_hash: str
    message: str
    body: str
    author: str
    date: str
    type: str
    scope: Optional[str]
    breaking: bool
    breaking_desc: Optional[str]
    footer: Dict[str, str]
    raw: str


@dataclass
class Version:
    tag: str
    name: str
    date: str
    commits: List[Commit]


def run_git(*args: str) -> str:
    """Run git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_remote_url() -> Optional[str]:
    """Get the origin remote URL."""
    try:
        url = run_git("remote", "get-url", "origin")
        return url
    except SystemExit:
        return None


def parse_remote_url(url: str) -> Optional[Dict[str, str]]:
    """Parse GitHub/GitLab remote URL to extract host, owner, repo."""
    # GitHub SSH: git@github.com:owner/repo.git
    # GitHub HTTPS: https://github.com/owner/repo.git
    # GitLab SSH: git@gitlab.com:owner/repo.git
    # GitLab HTTPS: https://gitlab.com/owner/repo.git
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)",
        r"gitlab\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            host = "github.com" if "github" in pattern else "gitlab.com"
            return {"host": host, "owner": match.group("owner"), "repo": match.group("repo")}
    return None


def get_tags() -> List[str]:
    """Get all tags sorted by version (semver-aware)."""
    try:
        output = run_git("tag", "--sort=-v:refname")
        return [t for t in output.split("\n") if t]
    except SystemExit:
        return []


def get_commits_between(since: str, until: str = "HEAD") -> List[str]:
    """Get commit hashes between two refs."""
    if since == "HEAD":
        return []
    try:
        # Handle --root case: get all commits up to "until"
        if since == "--root":
            output = run_git("log", "--pretty=format:%H", until)
        else:
            output = run_git("log", "--pretty=format:%H", f"{since}..{until}")
        return [h for h in output.split("\n") if h]
    except SystemExit:
        return []


def parse_commit(hash_: str) -> Commit:
    """Parse a single commit into a Commit object."""
    raw = run_git("show", "-s", "--format=%H%n%h%n%s%n%b%n%an%n%ad", "--date=iso", hash_)
    lines = raw.split("\n")
    if len(lines) < 6:
        return Commit(hash_, hash_[:7], "", "", "", "", "chore", None, False, None, {}, raw)

    full_hash, short_hash, subject, *rest = lines
    # Find body end (blank line before author/date)
    body_lines = []
    i = 0
    while i < len(rest) and rest[i]:
        body_lines.append(rest[i])
        i += 1
    body = "\n".join(body_lines)
    author = rest[i] if i < len(rest) else ""
    date = rest[i + 1] if i + 1 < len(rest) else ""

    # Parse conventional commit: type(scope): message
    type_ = "chore"
    scope = None
    message = subject
    breaking = False
    breaking_desc = None
    footer = {}

    # Check for breaking change in subject (bang prefix)
    if subject.endswith("!"):
        breaking = True
        subject = subject[:-1].strip()

    match = re.match(r"^(\w+)(?:\(([^)]+)\))?:\s*(.+)$", subject)
    if match:
        type_ = match.group(1).lower()
        scope = match.group(2) if match.group(2) else None
        message = match.group(3).strip()

    # Parse body for BREAKING CHANGE footer and other footers
    for line in body.split("\n"):
        line = line.strip()
        if line.upper().startswith("BREAKING CHANGE:"):
            breaking = True
            breaking_desc = line[len("BREAKING CHANGE:"):].strip()
        elif ":" in line and not line.startswith(" "):
            # Footer: key: value
            key, _, value = line.partition(":")
            footer[key.strip()] = value.strip()

    return Commit(
        hash=full_hash,
        short_hash=short_hash,
        message=message,
        body=body,
        author=author,
        date=date,
        type=type_,
        scope=scope,
        breaking=breaking,
        breaking_desc=breaking_desc,
        footer=footer,
        raw=raw,
    )


def get_version_info(tag: str) -> Version:
    """Get version info for a tag."""
    # Get tag date
    date = run_git("log", "-1", "--format=%ad", "--date=iso", tag)
    # Get commits since previous tag
    tags = get_tags()
    idx = tags.index(tag) if tag in tags else -1
    prev_tag = tags[idx + 1] if idx + 1 < len(tags) else None
    since = prev_tag if prev_tag else "--root"
    commit_hashes = get_commits_between(since, tag)
    commits = [parse_commit(h) for h in commit_hashes]
    return Version(tag=tag, name=tag, date=date, commits=commits)


def get_unreleased_commits(last_tag: Optional[str]) -> List[Commit]:
    """Get commits since last tag (unreleased)."""
    since = last_tag if last_tag else "--root"
    commit_hashes = get_commits_between(since, "HEAD")
    return [parse_commit(h) for h in commit_hashes]


def group_commits(commits: List[Commit]) -> Dict[str, List[Commit]]:
    """Group commits by conventional type."""
    groups = {}
    for commit in commits:
        # Breaking changes get their own section
        if commit.breaking:
            key = BREAKING_CHANGE_TYPE
        else:
            key = CONVENTIONAL_TYPES.get(commit.type, "Other")
        groups.setdefault(key, []).append(commit)
    return groups


def format_commit(commit: Commit, remote_info: Optional[Dict[str, str]]) -> str:
    """Format a single commit for markdown output."""
    link = ""
    if remote_info:
        host = remote_info["host"]
        owner = remote_info["owner"]
        repo = remote_info["repo"]
        if host == "github.com":
            link = f"([{commit.short_hash}](https://github.com/{owner}/{repo}/commit/{commit.hash}))"
        elif host == "gitlab.com":
            link = f"([{commit.short_hash}](https://gitlab.com/{owner}/{repo}/-/commit/{commit.hash}))"
    else:
        link = f"({commit.short_hash})"

    scope = f"({commit.scope})" if commit.scope else ""
    msg = commit.message
    if commit.breaking_desc:
        msg += f" — **BREAKING:** {commit.breaking_desc}"
    return f"- {msg} {scope} {link}"


def generate_changelog(
    versions: List[Version],
    unreleased: List[Commit],
    remote_info: Optional[Dict[str, str]],
    include_unreleased: bool = True,
) -> str:
    """Generate markdown changelog."""
    lines = ["# Changelog", "", "All notable changes to this project will be documented in this file.", ""]

    # Unreleased section
    if include_unreleased and unreleased:
        groups = group_commits(unreleased)
        lines.append("## [Unreleased]")
        lines.append("")
        for section, commits in groups.items():
            lines.append(f"### {section}")
            lines.append("")
            for commit in commits:
                lines.append(format_commit(commit, remote_info))
            lines.append("")

    # Version sections
    for v in versions:
        if not v.commits:
            continue
        groups = group_commits(v.commits)
        lines.append(f"## [{v.tag}] - {v.date.split(' ')[0]}")
        lines.append("")
        for section, commits in groups.items():
            lines.append(f"### {section}")
            lines.append("")
            for commit in commits:
                lines.append(format_commit(commit, remote_info))
            lines.append("")

    # Footer with links
    if remote_info:
        host = remote_info["host"]
        owner = remote_info["owner"]
        repo = remote_info["repo"]
        if host == "github.com":
            base = f"https://github.com/{owner}/{repo}"
            lines.append(f"[{repo}]: {base}")
            for v in versions:
                lines.append(f"[{v.tag}]: {base}/releases/tag/{v.tag}")
            lines.append(f"[Unreleased]: {base}/compare/{versions[0].tag}...HEAD" if versions else f"[Unreleased]: {base}/commits/main")

    return "\n".join(lines).rstrip() + "\n"


def generate_json(
    versions: List[Version],
    unreleased: List[Commit],
    remote_info: Optional[Dict[str, str]],
    include_unreleased: bool = True,
) -> str:
    """Generate JSON output."""
    data = {
        "remote": remote_info,
        "versions": [],
    }
    if include_unreleased and unreleased:
        data["unreleased"] = [asdict(c) for c in unreleased]
    for v in versions:
        data["versions"].append({
            "tag": v.tag,
            "name": v.name,
            "date": v.date,
            "commits": [asdict(c) for c in v.commits],
        })
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate CHANGELOG.md from conventional commit git history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  changelog-gen                          # Full changelog
  changelog-gen -o docs/CHANGELOG.md     # Custom output path
  changelog-gen --since v1.0.0           # Since last release
  changelog-gen --unreleased-only        # Draft next release notes
  changelog-gen --version-prefix release/  # Custom tag prefix
  changelog-gen --format json            # JSON output
""",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("--since", help="Generate changelog since this tag (exclusive)")
    parser.add_argument("--until", default="HEAD", help="Generate changelog until this ref (default: HEAD)")
    parser.add_argument("--unreleased-only", action="store_true", help="Only show unreleased changes")
    parser.add_argument("--version-prefix", default="v", help="Tag prefix for version detection (default: v)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--no-unreleased", action="store_true", help="Exclude unreleased section")
    args = parser.parse_args()

    # Get remote info for commit links
    remote_url = get_remote_url()
    remote_info = parse_remote_url(remote_url) if remote_url else None

    # Get all tags matching prefix
    all_tags = get_tags()
    version_tags = [t for t in all_tags if t.startswith(args.version_prefix)]

    # Sort by version (semver)
    def semver_key(tag):
        v = tag[len(args.version_prefix):]
        parts = v.split(".")
        nums = []
        for p in parts:
            try:
                nums.append(int(p))
            except ValueError:
                nums.append(0)
        return tuple(nums)

    version_tags.sort(key=semver_key, reverse=True)

    # Filter by --since
    if args.since:
        try:
            idx = version_tags.index(args.since)
            version_tags = version_tags[:idx]
        except ValueError:
            print(f"Tag '{args.since}' not found", file=sys.stderr)
            sys.exit(1)

    # Get version info
    versions = [get_version_info(tag) for tag in version_tags]

    # Get unreleased commits
    last_tag = version_tags[0] if version_tags else None
    unreleased = get_unreleased_commits(last_tag)

    # Generate output
    if args.unreleased_only:
        output = generate_changelog([], unreleased, remote_info, include_unreleased=True) if args.format == "markdown" else generate_json([], unreleased, remote_info, include_unreleased=True)
    else:
        output = generate_changelog(versions, unreleased, remote_info, include_unreleased=not args.no_unreleased) if args.format == "markdown" else generate_json(versions, unreleased, remote_info, include_unreleased=not args.no_unreleased)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()