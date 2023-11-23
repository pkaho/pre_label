# -*- encoding: utf-8 -*-
import json
import shutil
import argparse
from pathlib import Path
from rich.progress import track
from collections import Counter, defaultdict
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


def move_or_copy(label_file, jpg_file, output_path, nomove):
    if nomove is False:
        shutil.move(label_file, output_path)
        shutil.move(jpg_file, output_path)
    else:
        shutil.copy(label_file, output_path)
        shutil.copy(jpg_file, output_path)


def search_rule(label_file, search_cls, rule, all_cls=None, count_num=None):
    with label_file.open("r") as f:
        if label_file.suffix == ".txt":
            lines = [i.strip() for i in f if i.strip()]
            file_cls = [all_cls[int(i.strip().split()[0])] for i in lines]
        elif label_file.suffix == ".json":
            data = json.load(f)
            file_cls = [shape["label"] for shape in data["shapes"]]

    # cls_dic = dict(Counter(file_cls))     # 统计每个类别出现的次数
    cls_dic = defaultdict(int)
    for cls in file_cls:
        cls_dic[cls] += 1

    unique_labels = set(cls_dic.keys())
    search_cls = set(search_cls)
    result = [
        # 0) 无判断条件
        None,
        # 1) 标注类别包含任意搜索类别
        bool(unique_labels.intersection(search_cls)),
        # 2) 标注类别中不包含搜索类别
        bool(not unique_labels.intersection(search_cls)),
        # 3) 标注类别有且仅有搜索类别中的类
        bool(unique_labels.issubset(search_cls)),
        # 4) 标注类别完全匹配搜索类别(不可以有其他类)
        bool(unique_labels == search_cls),
        # 5) 标注类别包含所有搜索类别(允许存在其他类)
        bool(search_cls.issubset(unique_labels)),
        # 6) 搜索的类别出现次数大于count_num
        any([cls_dic[_key] > count_num for _key in search_cls if count_num > 0]),
        # 7) 搜索的类别出现次数小于count_num
        any([cls_dic[_key] < count_num for _key in search_cls if count_num > 0]),
    ]

    # 判断是否满足. 关于all([])返回True的问题, 可以参考下面的回答
    # ref: https://stackoverflow.com/questions/3275058/reason-for-all-and-any-result-on-empty-lists

    return result[rule], label_file


def search_img_by_labels(
    img_path,
    classes,
    cls_path=None,
    label_path=None,
    output_path=None,
    rule=1,
    nomove=False,
    count=0,
):
    parent_dir = Path(img_path).resolve().parent
    output_path = create_directory(output_path, parent_dir, "A_search")
    label_path = label_path or img_path
    ck_value = check_path(label_path, cls_path, img_path, output_path)
    if isinstance(ck_value, list):
        return ck_value

    if cls_path is not None:
        with open(cls_path, "r") as f:
                all_cls = [i.strip() for i in f if i.strip()]

    search_cls = [c.strip() for c in classes.split(",")]

    image_list = [file for file in Path(img_path).iterdir() if file.suffix in IMAGE_FORMATS]
    for jpg_file in track(image_list, description="Searching..."):
        file_prefix = jpg_file.stem

        label_txt_file = Path(label_path) / f"{file_prefix}.txt"
        label_json_file = Path(label_path) / f"{file_prefix}.json"

        verify = False
        if label_txt_file.exists():
            verify, label_file = search_rule(label_txt_file, search_cls, rule, all_cls, count_num=count)
        elif label_json_file.exists():
            verify, label_file = search_rule(label_json_file, search_cls, rule, count_num=count)

        if verify:
            move_or_copy(label_file, jpg_file, output_path, nomove)

    return f"Finished! file saved to {output_path}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""通过labels找图片""", formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("--img_path", type=str, help="image path")
    parser.add_argument("--classes", type=str, help="search cls, e.g: cat,dog")
    parser.add_argument("--cls_path", type=str, default=None, help="classes path")
    parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="save path")
    parser.add_argument("--rule", type=int, default=1, help="search rule")
    parser.add_argument("--nomove", nargs="?", const=True, default=False, help="True: copy; False: move")
    parser.add_argument("--count", type=int, default=0, help="search result > count_num retutn 1")
    opt = parser.parse_args()

    stat = search_img_by_labels(**vars(opt))
    print(stat)
