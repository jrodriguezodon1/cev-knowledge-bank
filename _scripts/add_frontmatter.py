#!/usr/bin/env python3
"""
Add Jekyll frontmatter to all existing knowledge-bank markdown files.
Parses Source/Added/Tags/Category from the existing body text.
"""

import os
import re
import sys

REPO_ROOT = os.path.expanduser("~/knowledge-bank")

# Folders that contain content files (exclude Jekyll dirs)
CONTENT_FOLDERS = [
    "paid-ads",
    "influencer-marketing",
    "dev-engineering",
    "dev-technical",
    "product-gtm",
    "ai-agents",
    "founder-business",
    "life-personal",
    "attribution-mmm",
    "business-strategy",
    "content-marketing",
]

# Map folders to nav categories (the 7 in the sidebar)
FOLDER_TO_CATEGORY = {
    "paid-ads": "paid-ads",
    "influencer-marketing": "influencer-marketing",
    "dev-engineering": "dev-engineering",
    "dev-technical": "dev-engineering",
    "product-gtm": "product-gtm",
    "ai-agents": "ai-agents",
    "founder-business": "founder-business",
    "life-personal": "life-personal",
    "attribution-mmm": "founder-business",
    "business-strategy": "founder-business",
    "content-marketing": "paid-ads",
}


def extract_frontmatter_data(content, folder):
    """Parse Source/Added/Tags from body text."""
    lines = content.split("\n")
    
    # Extract title from first H1
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        title = "Untitled Entry"
    
    # Extract source URL
    source = ""
    source_patterns = [
        r'\*\*Source:\*\*\s*\[.*?\]\((https?://[^\)]+)\)',  # **Source:** [text](url)
        r'\*\*Source:\*\*\s*(https?://\S+)',                 # **Source:** url
        r'>\s*\*\*Source:\*\*\s*(https?://\S+)',             # > **Source:** url
        r'>\s*\*\*Source:\*\*\s*\[.*?\]\((https?://[^\)]+)\)', # > **Source:** [text](url)
    ]
    for pattern in source_patterns:
        m = re.search(pattern, content)
        if m:
            source = m.group(1).rstrip(")")
            break
    if not source:
        # Try plain text source
        m = re.search(r'\*\*Source:\*\*\s*(.+)', content)
        if m:
            source = m.group(1).strip()
    
    # Extract date
    date = ""
    date_patterns = [
        r'\*\*Added:\*\*\s*([\d]{4}-[\d]{2}-[\d]{2})',
        r'\*\*Date logged:\*\*\s*([\d]{4}-[\d]{2}-[\d]{2})',
        r'\*\*Date:\*\*\s*([\d]{4}-[\d]{2}-[\d]{2})',
        r'date:\s*([\d]{4}-[\d]{2}-[\d]{2})',
    ]
    for pattern in date_patterns:
        m = re.search(pattern, content, re.IGNORECASE)
        if m:
            date = m.group(1)
            break
    if not date:
        date = "2026-09-01"  # fallback
    
    # Extract tags
    tags = []
    tags_patterns = [
        r'\*\*Tags:\*\*\s*(.+)',
        r'\*\*Keywords:\*\*\s*(.+)',
    ]
    for pattern in tags_patterns:
        m = re.search(pattern, content)
        if m:
            raw_tags = m.group(1).strip()
            tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
            break
    
    # Category from folder
    category = FOLDER_TO_CATEGORY.get(folder, folder)
    
    return title, date, tags, source, category


def file_has_frontmatter(content):
    return content.startswith("---\n")


def build_frontmatter(title, date, tags, source, category):
    tags_yaml = "[" + ", ".join(f'"{t}"' for t in tags) + "]" if tags else "[]"
    fm = f"""---
title: "{title.replace('"', "'")}"
date: {date}
tags: {tags_yaml}
category: {category}
source: "{source.replace('"', "'")}"
layout: entry
---
"""
    return fm


def process_file(filepath, folder):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if file_has_frontmatter(content):
        print(f"  SKIP (already has frontmatter): {filepath}")
        return False
    
    title, date, tags, source, category = extract_frontmatter_data(content, folder)
    fm = build_frontmatter(title, date, tags, source, category)
    
    new_content = fm + content
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"  OK: {filepath}")
    print(f"      title={title[:60]!r}, date={date}, tags={tags[:3]}")
    return True


def main():
    processed = 0
    skipped = 0
    
    for folder in CONTENT_FOLDERS:
        folder_path = os.path.join(REPO_ROOT, folder)
        if not os.path.isdir(folder_path):
            continue
        
        for fname in os.listdir(folder_path):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(folder_path, fname)
            result = process_file(fpath, folder)
            if result:
                processed += 1
            else:
                skipped += 1
    
    print(f"\nDone: {processed} files updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
