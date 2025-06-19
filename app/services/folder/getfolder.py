import os
from app.core.config import config
from fastapi.responses import JSONResponse


def getfolder(root_folder: str, foldername: str):
    """
    return list of stuff inside folder
    """
    folder_path = os.path.join(f"{config.DIR_LOCATION}/data", root_folder, foldername)
    if not os.path.exists(folder_path):
        return {"error": "Folder does not exist"}

    # List all files and directories in the folder
    items = os.listdir(folder_path)

    return {"items": items}


def getallfolders(root_folder: str):
    """
    return list of all folders
    """

    if not root_folder:
        return JSONResponse({"error": "Root folder is not specified"}, status_code=400)
    folder_path = os.path.join(f"{config.DIR_LOCATION}/data", root_folder)

    if not os.path.exists(folder_path):
        return {"error": "Folder does not exist"}

    items = {}
    for folder in os.listdir(folder_path):
        all_items = os.listdir(os.path.join(folder_path, folder))
        items[folder] = all_items

    return items
