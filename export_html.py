#!/usr/bin/env python3
"""
HTML Export for changelog-gen
Converts generated CHANGELOG.md to styled HTML using the template.
"""

import re
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "templates" / "html_template.html"

def markdown_to_html(md_content: str, project_name: str, repo_url: str) -> str:
    """Convert markdown changelog to HTML using template."""
    
    # Read template
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    
    # Parse markdown sections
    # Split by version headers: ## [tag] - date
    version_pattern = re.compile(r'^## \[(.+?)\](?:\s*-\s*(.+?))?$', re.MULTILINE)
    
    html_parts = []
    last_end = 0
    
    for match in version_pattern.finditer(md_content):
        # Add content before this version (should be header/unreleased)
        if match.start() > last_end:
            before = md_content[last_end:match.start()].strip()
            if before:
                html_parts.append(parse_section(before, is_unreleased=True))
        
        tag = match.group(1)
        date = match.group(2) or ""
        version_title = f"[{tag}]" + (f" - {date}" if date else "")
        
        # Find next version or end
        next_match = version_pattern.search(md_content, match.end())
        section_end = next_match.start() if next_match else len(md_content)
        section_content = md_content[match.end():section_end].strip()
        
        html_parts.append(parse_version_section(version_title, section_content))
        last_end = section_end
    
    # Any remaining content
    if last_end < len(md_content):
        remaining = md_content[last_end:].strip()
        if remaining:
            html_parts.append(parse_section(remaining, is_unreleased=False))
    
    changelog_html = "\n".join(html_parts)
    
    # Fill template
    return template.replace("{{PROJECT_NAME}}", project_name) \
                   .replace("{{REPO_URL}}", repo_url) \
                   .replace("{{CHANGELOG_CONTENT}}", changelog_html)

def parse_section(content: str, is_unreleased: bool) -> str:
    """Parse a section (unreleased or footer)."""
    lines = content.split('\n')
    html = []
    
    if is_unreleased:
        html.append('<section class="version">')
        html.append('<h2>[Unreleased]</h2>')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('### '):
            html.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('- '):
            html.append(parse_commit_line(line[2:]))
    
    if is_unreleased:
        html.append('</section>')
    
    return "\n".join(html)

def parse_version_section(title: str, content: str) -> str:
    """Parse a version section."""
    html = ['<section class="version">']
    html.append(f'<h2>{title}</h2>')
    
    # Extract date if in format " - YYYY-MM-DD"
    date_match = re.search(r' - (\d{4}-\d{2}-\d{2})', title)
    if date_match:
        html.append(f'<div class="version-date">{date_match.group(1)}</div>')
    
    lines = content.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('### '):
            if current_section:
                html.append('</ul>')
            current_section = line[4:]
            html.append(f'<h3>{current_section}</h3>')
            html.append('<ul class="section">')
        elif line.startswith('- '):
            if not current_section:
                current_section = "Changes"
                html.append(f'<h3>{current_section}</h3>')
                html.append('<ul class="section">')
            html.append(f'<li>{parse_commit_line(line[2:])}</li>')
    
    if current_section:
        html.append('</ul>')
    
    html.append('</section>')
    return "\n".join(html)

def parse_commit_line(line: str) -> str:
    """Parse a single commit line into HTML."""
    # Format: - message (scope) (hash) or - message (hash)
    # Also handles: - message — **BREAKING:** desc (hash)
    
    # Extract hash link at end: ([hash](url)) or (hash)
    hash_match = re.search(r'\(([^)]+)\)\s*$', line)
    hash_html = ""
    if hash_match:
        hash_part = hash_match.group(1)
        line = line[:hash_match.start()].rstrip()
        # Check if it's a link: [hash](url)
        link_match = re.match(r'\[(.+?)\]\((.+?)\)', hash_part)
        if link_match:
            hash_html = f'<a href="{link_match.group(2)}" class="commit-hash" target="_blank">{link_match.group(1)}</a>'
        else:
            hash_html = f'<span class="commit-hash">{hash_part}</span>'
    
    # Check for breaking badge
    breaking = ""
    if '— **BREAKING:**' in line:
        breaking = '<span class="breaking-badge">breaking</span> '
        line = line.replace('— **BREAKING:**', '').replace('**BREAKING:**', '').strip()
    
    # Extract scope: (scope) at end before hash
    scope = ""
    scope_match = re.search(r'\(([^)]+)\)\s*$', line)
    if scope_match and not hash_match:  # Only if not the hash
        scope_text = scope_match.group(1)
        if ':' not in scope_text and '/' not in scope_text:  # Likely a scope
            scope = f'<span class="commit-scope">{scope_text}</span> '
            line = line[:scope_match.start()].rstrip()
    
    return f'<div class="commit">{hash_html}{breaking}{scope}<span class="commit-msg">{line}</span></div>'

def main():
    if len(sys.argv) < 3:
        print("Usage: python export_html.py <changelog.md> <output.html> [project_name] [repo_url]")
        sys.exit(1)
    
    md_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    project_name = sys.argv[3] if len(sys.argv) > 3 else "Changelog"
    repo_url = sys.argv[4] if len(sys.argv) > 4 else "https://github.com/Kiendas25/changelog-generator"
    
    if not md_path.exists():
        print(f"Error: {md_path} not found")
        sys.exit(1)
    
    md_content = md_path.read_text(encoding="utf-8")
    html = markdown_to_html(md_content, project_name, repo_url)
    out_path.write_text(html, encoding="utf-8")
    print(f"✅ HTML exported to {out_path}")

if __name__ == "__main__":
    main()