# -*- encoding: utf-8 -*-
import os
import shutil
import argparse
from pathlib import Path
from rich.progress import track
from argparse import RawDescriptionHelpFormatter

IMAGE_FORMATS = [
    ".bmp",
    ".dng",
    ".jpeg",
    ".jpg",
    ".mpo",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
    ".pfm",
]  # include image suffixes


def create_directory(output_dir, parent_path, dir_path):
    if output_dir is None:
        output_dir = parent_path / dir_path
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def single_move_or_copy(file, output_path, nomove):
    if nomove is False:
        shutil.move(file, output_path)
    else:
        shutil.copy(file, output_path)


def move_single_data(img_path, label_path=None, output_path=None, nomove=1):
    parent_dir = Path(img_path).resolve().parent
    output_path = create_directory(output_path, parent_dir, "A_single")
    label_path = label_path or img_path

    all_files = set(os.listdir(label_path)) | set(os.listdir(img_path))

    print("Checking...")
    file_cnt = {}
    for file in all_files:
        file = Path(file)
        name, suffix = file.stem, file.suffix
        file_cnt[name] = file_cnt.get(name, [])
        file_cnt[name].append(suffix)

    result = [Path(key + value[0]) for key, value in file_cnt.items() if len(value) < 2]

    for mv_file in track(result, description="MoveSingle..."):
        suffix = mv_file.suffix
        if suffix.lower() in IMAGE_FORMATS:
            jpg_file = Path(img_path) / mv_file
            single_move_or_copy(jpg_file, output_path, nomove)
        else:
            label_file = Path(label_path) / mv_file
            single_move_or_copy(label_file, output_path, nomove)
    return f"Completed! file saved in {output_path}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""移动图片和标签不成对的数据""", formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("--img_path", type=str, help="image path")
    parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="output path")
    parser.add_argument("--nomove", nargs="?", const=True, default=False, help="True: copy; False: move")
    opt = parser.parse_args()

    stat = move_single_data(**vars(opt))
    print(stat)
