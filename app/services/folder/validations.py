import re


def to_valid_folder_name(name: str) -> str:
    """
    Converts any string to a valid folder name by:
    - Removing all non-alphanumeric and underscore characters
    - Trimming to 255 characters
    - Falling back to 'untitled' if nothing is left
    """
    # Keep only letters, numbers, and underscores
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", name)

    # Trim to 255 characters
    cleaned = cleaned[:255]

    # Fallback name if nothing valid remains
    return cleaned if cleaned else "untitled"


def validFolderName(foldername):
    """
    Check if the folder name is valid.
    """
    # Check if the folder name is valid
    if not re.match(r"^[a-zA-Z0-9_]+$", foldername):
        return False

    if len(foldername) > 255:
        return False
    return True
