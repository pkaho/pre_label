import torch
import shutil
import cv2
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from myUtils.bbox_utils import xyxy2xywh
from myUtils.colors import RGB_COLORS, HEX_COLORS
HEX_COLORS = list(HEX_COLORS.keys())

def draw_box(im, box, label, cls):
    text_color = (0, 0, 0)
    color = HEX_COLORS[cls]
    lw = max(round(sum(im.size) / 2 * 0.003), 2)

    if label:
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("./utils/arial.ttf", size=20)
        draw.rectangle(box, width=lw, outline=color)
        # ImageDraw.textsize()自Pillow-10.0.0开始被删除, 具体替换方法可到官网查看
        # refer: https://pillow.readthedocs.io/en/stable/releasenotes/9.2.0.html#font-size-and-offset-methods
        left, top, right, bottom = font.getbbox(label)
        text_width, text_height = right - left, bottom - top

        text_x = box[0]
        text_y = box[1] - text_height
        draw.rectangle(
            (text_x, text_y, text_x + text_width, text_y + text_height), fill=color
        )
        draw.text((text_x, text_y), label, fill=text_color, font=font)
    return im

def draw_box_with_cv2(im, box, label, cls):
    text_color = (0, 0, 0)
    cls = 13 if cls>7 else 12
    color = RGB_COLORS[cls][::-1]
    lw = max(round(sum(im.shape) / 2 * 2e-3), 2)
    tf = max(lw - 1, 1)
    sf = lw / 3

    p1 = tuple(map(int, box[:2]))
    p2 = tuple(map(int, box[2:]))
    cv2.rectangle(im, p1, p2, color=color, thickness=lw, lineType=cv2.LINE_AA)
    if label:
        w, h = cv2.getTextSize(label, 0, fontScale=sf, thickness=tf)[0]
        outside = p1[1] - h >= 3
        p2 = p1[0] + w, p1[1] - h -3 if outside else p1[1] + h + 3
        cv2.rectangle(im, p1, p2, color, -1, cv2.LINE_AA)
        cv2.putText(
            im,
            label,
            (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
            0,
            sf,
            text_color,
            thickness=tf,
            lineType=cv2.LINE_AA,
        )

def write_json(json_path, label_mes, shapes):
    if json_path.exists():
        with open(json_path, "r") as f:
            label_mes = json.load(f)
    label_mes['shapes'].extend(shapes)

    with open(json_path, "w") as f:
        json.dump(label_mes, f, ensure_ascii=False, indent=2)

def write_txt(txt_path, lines):
    for line in lines:
        with open(txt_path, "a+") as f:
            f.seek(0)
            all_lines = f.readlines()
            if all_lines and all_lines[-1][-1].strip() != "":
                f.write("\n")
            f.write(("%g " * len(line)).rstrip() % line + "\n")

def process_results(det, save_dir, im0, path, all_cls):
    label_mes = {
        "version": "5.2.1",
        "flags": {},
        "shapes": [],
        "imageData": None,
        "imagePath": path.name,
        "imageHeight": im0.shape[0],
        "imageWidth": im0.shape[1],
    }
    pil_img = Image.fromarray(cv2.cvtColor(im0, cv2.COLOR_BGR2RGB))     # 使用PIL.Image可以绘制非英文字符的文本
    shapes = []
    lines = []
    for *xyxy, conf, cls in det:
        cls = int(cls)
        xyxy = torch.Tensor(xyxy).tolist()
        conf = round(float(conf), 4)

        # add one xyxy box to image with label
        label = f"{all_cls[cls]} {conf:.2f}"
        pil_img = draw_box(pil_img, xyxy, label, cls)

        # write file
        if save_dir.get("txt", None):
            # normalized xywh
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]
            xywh = (xyxy2xywh(torch.Tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
            line = (cls, *xywh)
            lines.append(line)

        if save_dir.get("json", None):
            shape = {
                "label"      : all_cls[cls],
                "points"     : [[xyxy[0], xyxy[1]], [xyxy[2], xyxy[3]]],
                "shape_type" : "rectangle",
                "flags"      : {},
                "group_id"   : None,
                "other_data" : {},
            }
            shapes.append(shape)

    pil_img.save(save_dir['show'] / path.name)
    if shapes:
        json_path = save_dir['json'] / f"{path.stem}.json"
        write_json(json_path, label_mes, shapes)
        if not Path(save_dir['json'] / path.name).exists():
            shutil.copy(path, save_dir['json'])
    if lines:
        txt_path = save_dir['txt'] / f"{path.stem}.txt"
        write_txt(txt_path, lines)
        if not Path(save_dir['txt'] / path.name).exists():
            shutil.copy(path, save_dir['txt'])
