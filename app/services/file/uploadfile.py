from app.core.config import config
from fastapi import HTTPException, UploadFile
import os


def UploadMyFile(file: UploadFile, folder_location: str) -> str:
    """
    Uploads a file to the server.
    :param file: The file to be uploaded.
    :return: The path of the uploaded file.
    """
    # Check if the file is empty
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")

    # Check if the file is too large
    # TODO

    # Check if the folder exists, if not raise an error
    if not os.path.exists(folder_location):
        raise HTTPException(status_code=400, detail="Folder does not exist")

    # check if the filename is too long
    if len(file.filename) > 255:
        raise HTTPException(
            status_code=400,
            detail="Filename is too long, maximum length is 255 characters",
        )

    # Check if the file name is already in use, add (1) to the end of the file name if it is
    if os.path.exists(os.path.join(folder_location, file.filename)):
        file_name, file_extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(
            os.path.join(folder_location, f"{file_name}({i}){file_extension}")
        ):
            i += 1
        file.filename = f"{file_name}({i}){file_extension}"

    # finally upload the file
    file_location = os.path.join(folder_location, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    return file_location
