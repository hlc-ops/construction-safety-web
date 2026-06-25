"""把 D:/INT8tupian/ 的 300 张平铺图重排成 YOLO 格式 + 写 dataset.yaml。

输出结构：
  D:/INT8tupian/
    images/val/  <- 300 张图
    labels/val/  <- 对应的 300 个 txt（从原数据集复制过来）
    dataset.yaml <- 给 ultralytics 导出做校准用
"""
import os
import shutil

CALIB = r"D:/INT8tupian"
SOURCE = r"D:/Python/PyCharm/PythonProject/construction_safety/dataset"

# 1) 把平铺的 jpg 移进 images/val
img_dir = os.path.join(CALIB, "images", "val")
lbl_dir = os.path.join(CALIB, "labels", "val")
os.makedirs(img_dir, exist_ok=True)
os.makedirs(lbl_dir, exist_ok=True)

moved = 0
for name in list(os.listdir(CALIB)):
    src = os.path.join(CALIB, name)
    if os.path.isfile(src) and name.lower().endswith((".jpg", ".jpeg", ".png")):
        shutil.move(src, os.path.join(img_dir, name))
        moved += 1
print(f"已移动图片 {moved} 张到 images/val/")

# 2) 拷贝对应标签
labeled = 0
missing = []
for name in os.listdir(img_dir):
    stem = os.path.splitext(name)[0]
    txt = stem + ".txt"
    found = False
    for split in ("train", "val"):
        src = os.path.join(SOURCE, "labels", split, txt)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(lbl_dir, txt))
            labeled += 1
            found = True
            break
    if not found:
        missing.append(name)
print(f"已复制标签 {labeled} 个；缺标签 {len(missing)} 张（这些图也行，量化只用图片）")

# 3) 写 dataset.yaml
yaml = f"""# INT8 量化校准用数据集（仅 val 即可）
path: {CALIB.replace(chr(92), '/')}
train: images/val
val: images/val
nc: 6
names:
  0: Safety_vest
  1: fall
  2: head
  3: helmet
  4: phone
  5: smoking
"""
yaml_path = os.path.join(CALIB, "dataset.yaml")
with open(yaml_path, "w", encoding="utf-8") as f:
    f.write(yaml)
print(f"已写 {yaml_path}")
