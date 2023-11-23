# -*- encoding: utf-8 -*-
import re
import json
import argparse
from pathlib import Path
from rich.progress import track
from argparse import RawDescriptionHelpFormatter

LABEL_FORMATS = [".txt", ".json"]  # include image suffixes


def modify_txt(file, old_str, new_str, cls_path):
    with open(cls_path, "r") as af:
        all_cls = [i.strip() for i in af if i.strip()]
    with open(file, "r") as bf:
        lines = [i.strip() for i in bf if i.strip()]

    old_str_id =  int(old_str) if old_str.isdigit() else all_cls.index(old_str)
    new_lines = []
    for line in lines:
        label = int(line.split(" ")[0])
        if label != old_str_id:
            new_lines.append(line)
            continue
        if new_str is None:
            continue
        elif new_str.isdigit():
            new_str_id = str(new_str)
        else:
            new_str_id = str(all_cls.index(new_str))
        new_line = re.sub(f"^{old_str_id}", new_str_id, line, flags=re.MULTILINE)
        new_lines.append(new_line)

    with open(file, 'w') as f:
        f.write('\n'.join(new_lines))
    return "Modification completed!"


def modify_json(file, old_str, new_str):
    with open(file, "r") as f:
        data = json.load(f)

    if new_str is None:
        data["shapes"] = [
            shape for shape in data["shapes"] if shape["label"] != old_str
        ]

    if new_str is not None:
        for shape in data["shapes"]:
            if shape["label"] == old_str:
                shape["label"] = new_str

    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def modify_label(label_path, old_str, new_str, cls_path):
    label_path = Path(label_path)
    if not label_path.exists():
        return f"{label_path} not found!"

    label_list = [i for i in label_path.iterdir() if i.suffix in LABEL_FORMATS]
    for label_file in track(label_list, description="Modify..."):
        if label_file.suffix == LABEL_FORMATS[0]:       # .txt
            modify_txt(label_file, old_str, new_str, cls_path)
        elif label_file.suffix == LABEL_FORMATS[1]:     # .json
            modify_json(label_file, old_str, new_str)

    return "Modification completed!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""修改标签类别""", formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("--label_path", type=str, help="label path")
    parser.add_argument("--old_str", type=str, help="label that need to be modified")
    parser.add_argument("--new_str", type=str, default=None, help="new label")
    parser.add_argument("--cls_path", type=str, default=None, help="classes.txt path")
    opt = parser.parse_args()

    stat = modify_label(**vars(opt))
    print(stat)
