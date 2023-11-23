# -*- encoding: utf-8 -*-
import argparse
from pathlib import Path, PurePath
from argparse import RawDescriptionHelpFormatter
from rich.progress import track

def rename_files(path, add_str=None, position="0", old_str=None, new_str=""):
    """
    Renames files in the specified path by adding a string, changing a string, or both.

    Args:
        path (str): The path to the directory containing the files.
        add_str (str, optional): The string to be added to the filenames. Defaults to None.
        position (str, optional): The position at which the add_str should be inserted.
            Can be 'end' or a number. Defaults to "0".
        old_str (str, optional): The string to be replaced in the filenames. Defaults to None.
        new_str (str, optional): The replacement string. Defaults to "".

    Returns:
        str: A message indicating the status of the operation. If successful, returns "Complete!".
            Otherwise, returns an error message.
    """

    path = Path(path)
    if not Path.exists(path):
        return f"Error: {path} does not exist."

    for file in track(path.iterdir(), description="Rename..."):
        if Path.is_dir(file) or file.name.startswith('.'):
            continue

        old_filename, ext = file.stem, file.suffix
        new_filename = old_filename
        if add_str:
            if position == 'end':
                new_filename = old_filename + add_str
            elif position.isdigit():
                pos = int(position)
                new_filename = old_filename[:pos] + add_str + old_filename[pos:]
            else:
                new_filename = old_filename
                add_str = None
                print("Format Error! The <position> should be 'end' or a number")
        elif old_str:
            new_filename = old_filename.replace(old_str, new_str)

        if new_filename != old_filename:
            dir_path = file.parent
            # new_path = PurePath(dir_path, new_filename + ext)
            new_path = dir_path / (new_filename + ext)
            file.rename(new_path)
    return "Complete!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""批量重命名""", formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--path', type=str, help="directory path")
    parser.add_argument('--add_str', type=str, default=None, help="The string to be added")
    parser.add_argument('--position', type=str, default="0", help="string position")
    parser.add_argument('--old_str', type=str, default=None, help="old string")
    parser.add_argument('--new_str', type=str, default="", help="new string")
    opt = parser.parse_args()

    stat = rename_files(**vars(opt))
    print(stat)
