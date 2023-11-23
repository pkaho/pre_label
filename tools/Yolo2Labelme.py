# -*- encoding: utf-8 -*-
import json
import shutil
import argparse
from PIL import Image
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
JSON_FORMAT = {
    "version": "5.3.1",
    "flags": {},
    "shapes": [],
    "imagePath": None,
    "imageData": None,
    "imageHeight": None,
    "imageWidth": None,
}


def check_path(*args):
    if err_list := [
        f"Error: The specified {path} path does not exist."
        for path in args
        if path is not None and not Path(path).exists()
    ]:
        return err_list
    return 1

def create_directory(output_dir, parent_path, dir_path):
    if output_dir is None:
        output_dir = parent_path / dir_path
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def yolo_to_labelme(img_path, cls_path, label_path=None, output_path=None):
    # 使用绝对路径避免路径错误, 在 label_path 是相对路径并为单层路径时 e.g: label_path = ./test 时, parent_dir = ./test
    parent_dir = Path(img_path).resolve().parent
    label_path = label_path or img_path
    output_path = create_directory(output_path, parent_dir, "A_txt2json")
    ck_value = check_path(label_path, img_path, cls_path, output_path)
    if isinstance(ck_value, list):
        return ck_value

    with open(cls_path, "r") as f:
        all_cls = f.read().splitlines()

    not_found_file = parent_dir / "TXT_NotFoundLabel.txt"

    image_list = [
        file
        for file in Path(img_path).iterdir()
        if file.name.endswith(tuple(IMAGE_FORMATS))
    ]
    for jpg_file in track(image_list, description="YoloToJson..."):
        filename = jpg_file.stem
        label_file = Path(label_path) / f"{filename}.txt"

        # 如果没找到标签文件则写入TXT_NotFoundLabel.txt中
        if not label_file.exists():
            with open(not_found_file, "a") as ef:
                ef.write(str(filename) + "\n")
            continue

        with open(label_file, "r") as rf:
            lines = [i.strip() for i in rf if i.strip()]

        im_width, im_height = Image.open(jpg_file).size
        JSON_FORMAT["shapes"] = []
        JSON_FORMAT["imagePath"] = jpg_file.name
        JSON_FORMAT["imageHeight"] = im_height
        JSON_FORMAT["imageWidth"] = im_width

        json_path = Path(output_path) / f"{filename}.json"
        for line in lines:
            clsid, x_c, y_c, w, h = map(float, line.split())

            x_min = (x_c - w / 2) * im_width
            y_min = (y_c - h / 2) * im_height
            x_max = (x_c + w / 2) * im_width
            y_max = (y_c + h / 2) * im_height

            JSON_FORMAT["shapes"].append(
                {
                    "label": str(all_cls[int(clsid)]),
                    "points": [[x_min, y_min], [x_max, y_max]],
                    "group_id": None,
                    "shape_type": "rectangle",
                    "flags": {},
                }
            )
        shutil.copy(jpg_file, output_path)
        with json_path.open("w") as f:
            json.dump(JSON_FORMAT, f)

    prompt = f"Completed! files saved to {output_path}"
    if not_found_file.exists():
        prompt += f"\nSome data failed to be converted! pls check {not_found_file}"
    return prompt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""YOLO格式标签 --> JSON的txt格式""",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("--img_path", type=str, help="image path")
    parser.add_argument("--cls_path", type=str, help="classes.txt path")
    parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="output path")
    opt = parser.parse_args()

    stat = yolo_to_labelme(**vars(opt))
    print(stat)
