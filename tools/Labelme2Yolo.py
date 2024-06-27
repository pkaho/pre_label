# -*- encoding: utf-8 -*-
import json
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


def xyxy2xywh(img_w, img_h, box):
    dw = 1.0 / img_w
    dh = 1.0 / img_h

    x_c = (box[0] + box[2]) / 2.0
    y_c = (box[1] + box[3]) / 2.0

    box_w = abs(box[2] - box[0])
    box_h = abs(box[3] - box[1])

    x_center = x_c * dw
    width = box_w * dw
    y_center = y_c * dh
    height = box_h * dh

    return (x_center, y_center, width, height)


def labelme_to_yolo(img_path, cls_path, label_path=None, output_path=None):
    # 使用绝对路径避免路径错误, 在 label_path 是相对路径并为单层路径时 e.g: label_path = ./test 时, parent_dir = ./test
    parent_dir = Path(img_path).resolve().parent
    output_path = create_directory(output_path, parent_dir, "A_json2txt")
    label_path = label_path or img_path
    ck_value = check_path(label_path, img_path, cls_path, output_path)
    if isinstance(ck_value, list):
        return ck_value

    with open(cls_path, "r") as f:
        classes = f.read().splitlines()

    not_found_file = parent_dir / "JSON_NotFoundLabel.txt"

    image_list = [
        file
        for file in Path(img_path).iterdir()
        if file.name.endswith(tuple(IMAGE_FORMATS))
    ]
    for jpg_file in track(image_list, description="JsonToYolo..."):
        filename = jpg_file.stem
        label_file = Path(label_path) / f"{filename}.json"

        # 如果没找到标签文件则写入JSON_NotFoundLabel.txt中
        if not label_file.exists():
            with open(not_found_file, "a") as ef:
                ef.write(str(filename) + "\n")
            continue

        with open(label_file, "r") as rf:
            data = json.load(rf)

        im_width, im_height = data["imageWidth"], data["imageHeight"]

        txt_path = Path(output_path) / f"{filename}.txt"
        with open(txt_path, "w") as f:
            for shape in data["shapes"]:
                label = shape["label"]
                class_id = classes.index(label)
                xyxy_box = shape["points"]
                xyxy_box = [
                    xyxy_box[0][0],
                    xyxy_box[0][1],
                    xyxy_box[1][0],
                    xyxy_box[1][1],
                ]
                xywh_box = xyxy2xywh(im_width, im_height, xyxy_box)
                f.write(
                    f"{str(class_id)} " + " ".join([str(i) for i in xywh_box]) + "\n"
                )
        shutil.copy(jpg_file, output_path)

    prompt = f"Completed! files saved to {output_path}"
    if not_found_file.exists():
        prompt += f"\nSome data failed to be converted! pls check {not_found_file}"
    return prompt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""JSON格式标签 --> YOLO的txt格式""",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("--img_path", type=str, help="image path")
    parser.add_argument("--cls_path", type=str, help="classes.txt path")
    parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="output path")
    opt = parser.parse_args()

    stat = labelme_to_yolo(**vars(opt))
    print(stat)
