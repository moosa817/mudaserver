from app.core.config import config
import os
import shutil


def DeleteFolder(rootfolder: str, folder_name: str):
    """
    Delete a folder with the given name.
    """
    rootloc = os.path.join(f"{config.DIR_LOCATION}/data", rootfolder)

    folderlocation = os.path.join(rootloc, folder_name)

    if os.path.exists(folderlocation):
        shutil.rmtree(folderlocation)
        return True
    else:
        return False
