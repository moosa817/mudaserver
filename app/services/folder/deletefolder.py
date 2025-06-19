from app.core.config import config
import os
import shutil


def DeleteFolder(rootfolder: str, folder_path: str):
    """
    Delete a folder with the given name.
    """
    rootloc = os.path.join(f"{config.DIR_LOCATION}/data", rootfolder)

    folderlocation = os.path.join(rootloc, folder_path)

    print(folderlocation)
    if os.path.exists(folderlocation):
        shutil.rmtree(folderlocation)
        return True
    else:
        return False
