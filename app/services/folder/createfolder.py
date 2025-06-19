from app.core.config import config
import os
import re
from fastapi.exceptions import HTTPException


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


def create_folder(root_folder, foldername, root_path):
    """
    Create a folder for the user.
    root_folder: The root folder of the user. (e.g "username")
    foldername: The name of the folder to be created.
    root_path: relative path where the folder should be created.
    """

    main_root = os.path.join(f"{config.DIR_LOCATION}/data", root_folder)

    if root_path == "root":
        root_folder_path = main_root
    else:
        root_folder_path = os.path.join(main_root, root_path)

    folder_path = os.path.join(root_folder_path, foldername)

    if os.path.exists(folder_path):
        raise HTTPException(
            status_code=400,
            detail="Folder already exists.",
        )

    try:
        os.makedirs(folder_path)
    except Exception as e:
        print(f"Error creating folder: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create folder.",
        )

    return foldername
