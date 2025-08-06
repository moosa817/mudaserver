import os
from app.core.config import config


def RenameMyFile(old_file_path: str, new_file_name: str, user) -> str:
    """
    Rename a file on the server.
    """
    # Construct the full old file path
    old_file_full_path = os.path.join(
        f"{config.DIR_LOCATION}/data", user.root_foldername, old_file_path
    )

    # Check if the old file exists
    if not os.path.exists(old_file_full_path):
        raise FileNotFoundError(f"The file {old_file_full_path} does not exist.")

    # Construct the new file path
    new_file_full_path = os.path.join(
        os.path.dirname(old_file_full_path), new_file_name
    )

    # Rename the file
    os.rename(old_file_full_path, new_file_full_path)

    return new_file_full_path
