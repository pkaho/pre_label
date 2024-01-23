## 关于【tools】文件夹说明

### 2024/01/23
| 文件名                  | 功能说明                                     |
| ----------------------- | -------------------------------------------- |
| AverageSplit.py         | 将数据集均分（并不常用）                     |
| BatchRename.py          | 批量命名，后续要优化一下位置插入的功能       |
| CropImage.py            | 将识别内容从原图剪切出来                     |
| Labelme2Yolo.py         | Json格式的标签文件转换成Txt格式              |
| LabelQuantityTracker.py | 统计数据集各类别的标签数量                   |
| MathchingFileNames.py   | 从src_path目录中取出dst_path目录中同名的文件 |
| ModifyLabel.py          | 修改标签类别                                 |
| MoveNolabelData.py      | 将标注文件为空/格式错误的数据移动/复制出来   |
| MoveSingleData.py       | 移动/复制图片和标签文件不成对的数据          |
| SearchDataByLabel.py    | 按照一定规则在数据集中搜索匹配的标注数据     |
| SplitData.py            | 分割数据集                                   |
| Yolo2Labelme.py         | Txt格式的标签文件转换成Json格式              |
