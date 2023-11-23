import random
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


def split_dataset(img_path, label_path=None, output_path=None, ratio=0.1):
    parent_dir = Path(img_path).resolve().parent
    output_path = create_directory(output_path, parent_dir, "A_splitdata")
    label_path = label_path or img_path

    train_image_dir = Path(output_path, "images", "train")
    val_image_dir = Path(output_path, "images", "val")
    train_label_dir = Path(output_path, "labels", "train")
    val_label_dir = Path(output_path, "labels", "val")

    train_image_dir.mkdir(parents=True, exist_ok=True)
    val_image_dir.mkdir(parents=True, exist_ok=True)
    train_label_dir.mkdir(parents=True, exist_ok=True)
    val_label_dir.mkdir(parents=True, exist_ok=True)

    image_list = [
        file for file in Path(img_path).iterdir() if file.suffix in IMAGE_FORMATS
    ]
    random.shuffle(image_list)

    split_index = int(len(image_list) * ratio)

    train_files = image_list[split_index:]
    val_files = image_list[:split_index]

    for tr_image_file in track(train_files, description="SplitTrain..."):
        tr_label_file = Path(label_path) / tr_image_file.name
        shutil.copy(tr_image_file, train_image_dir)
        shutil.copy(tr_label_file, train_label_dir)

    for val_image_file in track(val_files, description="SplitVal..."):
        val_label_file = Path(label_path) / val_image_file.name
        shutil.copy(val_image_file, val_image_dir)
        shutil.copy(val_label_file, val_label_dir)

    return f"Finished! file saved in {output_path}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""切分数据集""", formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("--img_path", type=str, help="image path")
    parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="output path")
    parser.add_argument("--ratio", type=float, default=0.1, help="val ratio")
    opt = parser.parse_args()

    stat = split_dataset(**vars(opt))
    print(stat)
