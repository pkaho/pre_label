# -*- encoding: utf-8 -*-
import os
import sys

import hydra
import torch
import shutil
from pathlib import Path
from rich.progress import track

from myUtils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from myUtils.checks import check_img_size, check_file, check_imshow
from myUtils.general import mkdir_output, Profile, detector, non_max_suppression
from myUtils.torch_utils import select_device, init_model
from myUtils.bbox_utils import scale_boxes
from myUtils.save_results import process_results

import warnings
os.chdir(sys.path[0]) # vscode debug 需要加上这一句
warnings.filterwarnings('ignore')

@hydra.main(version_base=None, config_path="./config", config_name="config")
def run(cfg):
    weights      = cfg.db.weights         # 模型
    source       = cfg.db.source          # 数据路径
    conf_thres   = cfg.db.conf_thres      # conf阈值
    iou_thres    = cfg.db.iou_thres       # iou阈值
    device       = cfg.db.device          # 设备
    classes      = cfg.db.classes         # 指定要识别的类别
    all_cls      = cfg.db.all_cls         # 所有类别
    save_dir     = cfg.db.save_dir        # 输出结果保存路径
    totxt        = cfg.db.totxt           # 保存标签到save_dir/txt文件夹
    tojson       = cfg.db.tojson          # 保存标签到save_dir/json文件夹
    imgsz        = cfg.db.imgsz           # 图片尺寸
    stride       = cfg.db.stride          # 步长
    vid_stride   = cfg.db.vid_stride      # 视频帧率步长
    agnostic_nms = cfg.db.agnostic_nms    # 设置是否无视类别进行nms
    max_det      = cfg.db.max_det         # 用于限制nms后保留的检测框的数量
    append_mode  = cfg.db.append_mode     # 标签路径


    # Judge source
    source = str(source)
    is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.streams') or (is_url and not is_file)
    if is_url and is_file:
        source = check_file(source)

    # Load classes
    if isinstance(all_cls, str) and Path(all_cls).is_file():
        all_cls = Path(all_cls).read_text().rsplit()
    elif isinstance(all_cls, str):
        all_cls = all_cls.replace(' ', '').split(',')
    if isinstance(classes, str):
        classes = classes.replace(' ', '').split(',')
    cls_num = classes if classes is None else [all_cls.index(i) for i in classes]

    # Save dir
    save_dir = mkdir_output(save_dir, tojson, totxt)
    if totxt:
        with open(save_dir['txt'] / 'classes.txt', 'a') as f:
            f.writelines(f'{c}\n' for c in all_cls)

    # Load model
    device = select_device(device)
    models = init_model(weights, device)
    imgsz = check_img_size(imgsz, s=stride)

    # Dataloader
    bs = 1  # batch_size
    if webcam:
        view_img = check_imshow(warn=True)
        dataset = LoadStreams(source, imgsz, stride, vid_stride=vid_stride)
        bs = len(dataset)
    else:
        dataset = LoadImages(source, imgsz, stride, vid_stride=vid_stride)
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Run inference
    seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
    for path, im, im0s, vid_cap, s in track(dataset, description="work..."):
        path = Path(path)
        if append_mode:
            save_dir['txt'] = path.parent if save_dir.get('txt') else None
            save_dir['json'] = path.parent if save_dir.get('json') else None
        with dt[0]:
            im = torch.from_numpy(im).to(device)
            im = im.half() if device != 'cpu' else im.float()    # uint8 to fp16/32
            im /= 255   # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]   # expand for batch dim

        with dt[1] and torch.jit.optimized_execution(False):
            pred = detector(models, im)

        with dt[2]:
            pred = non_max_suppression(pred, conf_thres, iou_thres, cls_num, agnostic_nms, max_det=max_det)

        for det in pred:
            if not len(det):
                shutil.copy(path, save_dir['empty'])
                continue
            det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0s.shape).round()
            process_results(det, save_dir, im0s, path, all_cls)

if __name__ == '__main__':
    run()
