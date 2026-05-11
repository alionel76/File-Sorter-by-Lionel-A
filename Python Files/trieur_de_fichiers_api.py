import re
from pathlib import Path

my_dico = {}

def existing_folders(source_folder):
    return [folder.name for folder in Path(source_folder).iterdir() if folder.is_dir()]


def _check_folder_name(folder_name):

    EMPTY_FOLDER_NAME_ERROR = "Le nom du dossier ne peut pas être vide."
    INVALID_FOLDER_NAME_ERROR = "Le nom du dossier ne peut pas contenir les caractères suivants : \\ / : * ? \" < > |"

    if folder_name == "":
        return EMPTY_FOLDER_NAME_ERROR
    elif re.search(r"[\\/:*?\"<>|]", folder_name):
        return INVALID_FOLDER_NAME_ERROR
    return True


def create_folders(source_folder, folder_name):
    folder_path = Path(source_folder) / folder_name

    check_folder = _check_folder_name(folder_name)
    
    if check_folder is not True:
        return check_folder
    
    if not folder_path.exists():
        folder_path.mkdir()
        return True
   

def organise_files(current_directory, dico):
    count = 0
    for my_file in current_directory.iterdir():
        if my_file.is_file():
            for folder_name, file_types in dico.items():
                if my_file.suffix[1:] in file_types:
                    current_directory.joinpath(my_file.name).rename(current_directory.joinpath(folder_name, my_file.name))
                    count += 1
    return count