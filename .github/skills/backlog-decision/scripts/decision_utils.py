#!/usr/bin/env python3
"""
Helper utilities for backlog-decision skill.
Handles decision ID generation, file naming, and validation.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple

# Project root and decisions directory
BACKLOG_DIR = Path(__file__).parent.parent.parent.parent / "backlog"
DECISIONS_ACTIVE = BACKLOG_DIR / "decisions"
DECISIONS_ARCHIVE = BACKLOG_DIR / "archive" / "decisions"


def get_next_decision_id() -> str:
    """
    Generate the next sequential decision ID.
    Scans both active and archive directories for existing IDs.
    Returns: 'decision-0005' if 0004 is the highest found
    """
    max_id = 0
    
    for directory in [DECISIONS_ACTIVE, DECISIONS_ARCHIVE]:
        if directory.exists():
            for file in directory.glob("decision-*.md"):
                match = re.match(r"decision-(\d+)", file.name)
                if match:
                    num = int(match.group(1))
                    max_id = max(max_id, num)
    
    return f"decision-{max_id + 1:04d}"


def slugify_title(title: str) -> str:
    """
    Convert title to slug format: lowercase, hyphens, no special chars.
    Truncates to 60 chars if needed.
    Example: "Use Confluent Enterprise" -> "use-confluent-enterprise"
    """
    # Lowercase and replace spaces with hyphens
    slug = title.lower().replace(" ", "-")
    # Remove special characters except hyphens
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    # Truncate to 60 chars if needed
    if len(slug) > 60:
        slug = slug[:60].rstrip("-")
    
    return slug


def generate_filename(title: str) -> str:
    """
    Generate decision filename: decision-000#-{slugified-title}.md
    """
    next_id = get_next_decision_id()
    slug = slugify_title(title)
    return f"{next_id}-{slug}.md"


def validate_status(status: str) -> Tuple[bool, Optional[str]]:
    """
    Validate decision status value.
    Returns: (is_valid, error_message)
    """
    valid_statuses = {"Proposed", "Accepted", "Rejected", "Superseded"}
    if status not in valid_statuses:
        return (False, f"Status must be one of: {', '.join(sorted(valid_statuses))}")
    return (True, None)


def validate_tags(tags_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate comma-separated tags (must be lowercase, hyphenated).
    Returns: (is_valid, error_message)
    """
    if not tags_str.strip():
        return (True, None)  # Optional field
    
    tags = [t.strip() for t in tags_str.split(",")]
    invalid = [t for t in tags if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", t)]
    
    if invalid:
        return (False, f"Invalid tags: {', '.join(invalid)}. Use lowercase, hyphens only.")
    return (True, None)


def task_id_exists(task_id: str) -> bool:
    """
    Check if a backlog task ID exists.
    Example: 'task-1.2' should exist in backlog/tasks/
    Returns: True if found, False otherwise
    """
    if not task_id:
        return True  # Optional field
    
    pattern = r"^task-(\d+)\.(\d+)$"
    if not re.match(pattern, task_id):
        return False
    
    tasks_dir = BACKLOG_DIR / "tasks"
    if not tasks_dir.exists():
        return False
    
    # Look for matching task file
    for file in tasks_dir.glob(f"{task_id}*.md"):
        return True
    
    return False


if __name__ == "__main__":
    # Test utilities
    print("Next Decision ID:", get_next_decision_id())
    print("Slugified Title:", slugify_title("Use Confluent Enterprise for Kafka"))
    print("Generated Filename:", generate_filename("Use Confluent Enterprise for Kafka"))
    print("Validate Status 'Accepted':", validate_status("Accepted"))
    print("Validate Tags 'infrastructure, database':", validate_tags("infrastructure, database"))
