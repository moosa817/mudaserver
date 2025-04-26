from app.core.config import config
import os
import re


# create root folder on user registration
def create_root_folder(username):
    """
    Create a root folder for the user.
    """
    # Get the root folder path from the config
    root_folder_path = os.path.join(f"{config.DIR_LOCATION}/data", username)
    try:
        os.makedirs(root_folder_path)
    except FileExistsError:
        return None
    return username


def create_folder(root_folder, foldername):
    """
    Create a folder for the user.
    """
    # Get the root folder path from the config
    root_folder_path = os.path.join(f"{config.DIR_LOCATION}/data", root_folder)
    # Create the folder path
    folder_path = os.path.join(root_folder_path, foldername)

    if os.path.exists(folder_path):
        return False

    try:
        os.makedirs(folder_path)
    except:
        return False

    return foldername


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
