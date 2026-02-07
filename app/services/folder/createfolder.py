from app.core.config import config
import os
import re
from fastapi.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)


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
        logger.warning(f"Root folder already exists for user: {username}")
        return None
    except PermissionError as e:
        logger.error(f"Permission denied creating folder for {username}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creating root folder for {username}: {e}", exc_info=True)
        return None
    return username


def create_folder(root_folder, foldername, root_path):
    """
    Create a folder for the user.
    root_folder: The root folder of the user. (e.g "username")
    foldername: The name of the folder to be created.
    root_path: relative path where the folder should be created.
    """
    try:
        main_root = os.path.join(f"{config.DIR_LOCATION}/data", root_folder)

        if root_path == "root":
            root_folder_path = main_root
        else:
            root_folder_path = os.path.join(main_root, root_path)

        # Security check: ensure path is within user's directory
        root_folder_path = os.path.realpath(root_folder_path)
        main_root = os.path.realpath(main_root)
        if not root_folder_path.startswith(main_root + os.sep) and root_folder_path != main_root:
            raise HTTPException(
                status_code=403,
                detail="Access denied.",
            )

        if not os.path.exists(root_folder_path):
            raise HTTPException(
                status_code=400,
                detail="Root path does not exist.",
            )

        folder_path = os.path.join(root_folder_path, foldername)

        if os.path.exists(folder_path):
            raise HTTPException(
                status_code=400,
                detail="Folder already exists.",
            )

        os.makedirs(folder_path)
        return foldername
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating folder: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create folder.",
        )
