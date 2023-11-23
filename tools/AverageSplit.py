import random
import shutil
import argparse
from rich.progress import track
from pathlib import Path
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

def create_directory(output_dir, parent_path, dir_path, nums):
    output_list = []

    if output_dir is None:
        output_dir = parent_path / dir_path

    output_dir = Path(output_dir).resolve()
    for i in range(nums):
        sub_dir = output_dir / f"split_{i}"
        output_list.append(sub_dir)
        sub_dir.mkdir(parents=True, exist_ok=True)
    return output_list

def average_split(img_path, nums, label_path=None, output_path=None):
    label_path = img_path if label_path is None else label_path
    parent_dir = Path(img_path).resolve().parent
    output_list = create_directory(output_path, parent_dir, "A_avesplit", nums)

    file_list = [file for file in Path(img_path).iterdir() if file.suffix in IMAGE_FORMATS]
    random.shuffle(file_list)
    for idx, jpg_file in track(enumerate(file_list), description="AveSplit..."):
        basename = Path(file_list[idx].stem)
        label_txt_file = label_path / basename.with_suffix('.txt')
        label_json_file = label_path / basename.with_suffix('.json')

        folder_id = idx % nums
        if label_json_file.exists():
            shutil.move(label_json_file, output_list[folder_id])
        elif label_txt_file.exists():
            shutil.move(label_txt_file, output_list[folder_id])
        shutil.move(jpg_file, output_list[folder_id])

    return f"Completed! file saved in {output_list}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""数据均分指定份数""", formatter_class=RawDescriptionHelpFormatter
    )
    # parser.add_argument("--img_path", type=str, help="image path")
    # parser.add_argument("--nums", type=str, help="number of copie")
    parser.add_argument("--img_path", type=str, default="./123", help="image path")
    parser.add_argument("--nums", type=int, default=3, help="number of copie")
    parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="output path")
    opt = parser.parse_args()

    stat = average_split(**vars(opt))
    print(stat)
