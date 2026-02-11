import re
import os


def sanitize_folder_name(name: str) -> str:
    """
    Sanitize device name for use as folder name.
    - Remove/replace invalid filesystem characters
    - Limit length
    - Handle edge cases
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    # Strip leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    sanitized = sanitized[:100]
    # Default if empty
    if not sanitized:
        sanitized = "Device"
    return sanitized


def get_unique_folder_name(base_name: str, existing_folders: list[str]) -> str:
    """
    Ensure folder name is unique by appending number if needed.
    "Laptop" -> "Laptop", "Laptop (2)", "Laptop (3)"
    """
    if base_name not in existing_folders:
        return base_name
    
    counter = 2
    while f"{base_name} ({counter})" in existing_folders:
        counter += 1
    return f"{base_name} ({counter})"
