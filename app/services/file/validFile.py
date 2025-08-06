import re


# function to validate file names
def is_valid_file_name(file_name: str) -> bool:
    """
    Validate the file name.
    File names can only contain letters, numbers, underscores, and dashes,
    and must be under 255 characters.
    """
    if len(file_name) > 255:
        return False
    if not re.match(r"^[\w\-. ]+$", file_name):
        return False
    return True
