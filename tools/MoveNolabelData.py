# -*- encoding: utf-8 -*-
import shutil
import json
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


def move_or_copy(label_file, jpg_file, output_path, nomove):
    if nomove is False:
        shutil.move(label_file, output_path)
        shutil.move(jpg_file, output_path)
    else:
        shutil.copy(label_file, output_path)
        shutil.copy(jpg_file, output_path)


def judge_nolabel(label_file):
    if label_file.stat().st_size == 0:
        return 1

    with open(label_file, "r", encoding="utf-8") as f:
        if label_file.suffix == ".txt":
            lines = [i.strip() for i in f if i.strip()]
            if not lines or any(len(i.split(" ")) != 5 for i in lines):
                return 1
        elif label_file.suffix == ".json":
            data = json.load(f)
            return not data.get("shapes", 0)
    return 0


def move_nolabel_data(img_path, label_path=None, output_path=None, nomove=False):
    parent_dir = Path(img_path).resolve().parent
    output_path = create_directory(output_path, parent_dir, "A_nolabel")
    label_path = label_path or img_path

    image_list = [
        file for file in Path(img_path).iterdir() if file.suffix in IMAGE_FORMATS
    ]
    for jpg_file in track(image_list, description="MoveNolabel..."):
        file_prefix = jpg_file.stem

        label_txt_file = Path(label_path) / f"{file_prefix}.txt"
        label_json_file = Path(label_path) / f"{file_prefix}.json"

        if label_txt_file.exists():
            verify = judge_nolabel(label_txt_file)
            if not verify:
                continue
            move_or_copy(label_txt_file, jpg_file, output_path, nomove)
        elif label_json_file.exists():
            verify = judge_nolabel(label_json_file)
            if not verify:
                continue
            move_or_copy(label_json_file, jpg_file, output_path, nomove)

    return f"Completed! file saved in {output_path}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""移动空标签的数据""", formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("--img_path", type=str, help="image path")
    parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="output path")
    parser.add_argument("--nomove", nargs="?", const=True, default=False, help="True: copy; False: move")
    opt = parser.parse_args()

    stat = move_nolabel_data(**vars(opt))
    print(stat)
