# -*- encoding: utf-8 -*-
import shutil
import argparse
import glob
from pathlib import Path
from rich.progress import track
from argparse import RawDescriptionHelpFormatter

def move_or_copy(file_list, output_path):
    for file in file_list:
        shutil.move(file, output_path)

def create_directory(output_dir, parent_path, dir_path):
    if output_dir is None:
        output_dir = parent_path / dir_path
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def match_same_name(src_path, dst_path, output_path):
    src_path, dst_path = Path(src_path).resolve(), Path(dst_path).resolve()
    parent_dir = src_path.parent
    output_path = create_directory(output_path, parent_dir, "A_SameName")
    src_set = set([Path(file.name).stem for file in src_path.iterdir()])
    dst_set = set([Path(file.name).stem for file in dst_path.iterdir()])

    same_set = src_set & dst_set
    for file in same_set:
        file_list = glob.glob(str(src_path / file) + "*")
        move_or_copy(file_list, output_path)

    return f"Completed! file saved in {output_path}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""从src_path中取出dst_path中同名的文件""", formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("--src_path", type=str, default="../data/a/", help="src path")
    parser.add_argument("--dst_path", type=str, default="../data/b/", help="dst path")
    parser.add_argument("--output_path", type=str, default=None, help="dst path")
    opt = parser.parse_args()

    stat = match_same_name(**vars(opt))
    print(stat)