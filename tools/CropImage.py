# -*- encoding: utf-8 -*-
import json
import argparse
from pathlib import Path
from PIL import Image
from rich.progress import track
from datetime import datetime
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


def cutter(message, image, output_path):
    for bbox in message:
        class_id, left, top, right, bottom = bbox
        now = datetime.now()
        formatted_date = now.strftime("%Y_%m_%d_%H_%M_%S_%f")

        cropped_image = image.crop((left, top, right, bottom))
        cropped_image.save(f"{output_path}/cls_{class_id}_{formatted_date}.jpg")


def crop_image(img_path, label_path=None, output_path=None):
    parent_dir = Path(img_path).resolve().parent
    output_path = create_directory(output_path, parent_dir, "A_crop")
    label_path = label_path or img_path

    image_list = [
        file for file in Path(img_path).iterdir() if file.suffix in IMAGE_FORMATS
    ]
    for image_file in track(image_list, description="Cut..."):
        image = Image.open(image_file)
        label_mess = []
        file_prefix = image_file.stem

        label_txt_file = Path(label_path) / f"{file_prefix}.txt"
        label_json_file = Path(label_path) / f"{file_prefix}.json"
        if label_txt_file.exists():
            with label_txt_file.open("r") as f:
                lines = [i.strip() for i in f if i.strip()]
            for line in lines:
                class_id, x_center, y_center, width, height = map(
                    float, line.strip().split()
                )

                # xywh2xyxy
                left = int((x_center - width / 2) * image.width)
                top = int((y_center - height / 2) * image.height)
                right = int((x_center + width / 2) * image.width)
                bottom = int((y_center + height / 2) * image.height)
                label_mess.append([class_id, left, top, right, bottom])
        elif label_json_file.exists():
            with open(label_json_file, "r") as f:
                data = json.load(f)
            shapes = data["shapes"]
            for shape in shapes:
                class_id = shape["label"]
                left = shape["points"][0][0]
                top = shape["points"][0][1]
                right = shape["points"][1][0]
                bottom = shape["points"][1][1]
                label_mess.append([class_id, left, top, right, bottom])
        cutter(label_mess, image, output_path)

    return f"Complete! file saved to {output_path}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""从原图切割出标注的部分""", formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("--img_path", type=str, help="image path")
    parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="output path")
    opt = parser.parse_args()

    stat = crop_image(**vars(opt))
    print(stat)
