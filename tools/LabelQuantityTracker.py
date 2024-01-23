import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from rich.progress import track
from argparse import RawDescriptionHelpFormatter

LABEL_FORMATS = ['.txt', '.json']

def column_charts(df, jpg_path):
    fig = plt.figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)

    colors = ["red", "blue", "green", "yellow", "purple", "orange", "black", "pink", "brown", "gray", "cyan", "lightskyblue", "gold"]
    total_count = df["Count"].sum()
    for idx, (name, count) in enumerate(df.values):
        color = colors[idx % len(colors)]  # Use modulo operator to loop back to beginning of colors
        ax.barh(name, count, label=f"{name}: {count} ({(count/total_count):.2%})", color=color)
        ax.annotate(f"{count}", xy=(count, idx), xytext=(count, idx), color='black', fontweight='normal')

    ax.legend(loc='upper right', reverse=True)
    # plt.show()
    fig.savefig(jpg_path)

def count_by_labels(label_path, output_path, cls_path=None):
    label_path = Path(label_path)
    output_path = label_path.parent if output_path is None else output_path
    xlsx_path = output_path / "label_counts.xlsx"
    jpg_path = output_path / "label_counts.jpg"

    label_list = [
        file for file in label_path.iterdir() if file.suffix in LABEL_FORMATS
    ]
    labels = []

    for label_file in track(label_list, description="Tracker..."):
        if label_file.suffix == LABEL_FORMATS[1]:    # .json
            with open(label_file, 'r') as f:
                data = json.load(f)
                labels.extend([shape['label'] for shape in data['shapes']])
        elif label_file.suffix == LABEL_FORMATS[0]:  # .txt
            with open(cls_path, "r") as f:
                classes = f.read().splitlines()
            with open(label_file, 'r') as f:
                clsid_list = [line.strip().split()[0] for line in f if line.strip()]
                labels.extend([classes[int(i)] for i in clsid_list])
        else:
            raise ValueError('Unsupported label file format')

    df = pd.Series(labels).value_counts().reset_index()
    df.columns = ['Label', 'Count']
    df.to_excel(xlsx_path, index=False)

    column_charts(df, jpg_path)

    return f"Completed! file saved in {output_path}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""统计标签数量""", formatter_class=RawDescriptionHelpFormatter
    )
    # parser.add_argument("--label_path", type=str, default=None, help="label path")
    parser.add_argument("--label_path", type=str, help="label path")
    parser.add_argument("--output_path", type=str, default=None, help="xlsx output path")
    parser.add_argument("--cls_path", type=str, default=None, help="label path")
    opt = parser.parse_args()

    stat = count_by_labels(**vars(opt))
    print(stat)
