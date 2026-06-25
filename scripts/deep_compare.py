"""更彻底地对比 FP32 vs INT8：
1. 在 background.png 上多档置信度看 INT8 是否只是分数低
2. 在 30 张校准集图上对比检测一致性
"""
import os
import random

import cv2
from ultralytics import YOLO


def detect(model, img, conf, imgsz=416):
    r = model.predict(img, conf=conf, verbose=False, imgsz=imgsz)[0]
    if r.boxes is None or len(r.boxes) == 0:
        return []
    out = []
    for b in r.boxes:
        out.append((model.names[int(b.cls[0])], round(float(b.conf[0]), 3)))
    return sorted(out)


fp32 = YOLO("model/best_openvino_model_fp32", task="detect")
int8 = YOLO("model/best_int8_openvino_model", task="detect")

# 1) background.png 多档 conf
print("=== background.png 不同置信度对比 ===")
img = cv2.imread("static/background.png")
for c in [0.05, 0.1, 0.2, 0.3, 0.4]:
    print(f"  conf={c:.2f}  FP32={detect(fp32, img, c)}  INT8={detect(int8, img, c)}")

# 2) 校准集 30 张图对比（conf=0.3）
print("\n=== 校准集 30 张图（conf=0.3）一致性 ===")
cal_dir = "D:/INT8tupian/images/val"
files = [f for f in os.listdir(cal_dir) if f.lower().endswith((".jpg", ".png"))]
random.Random(42).shuffle(files)
sample = files[:30]

ok = 0
diff = 0
both_empty = 0
fp_more = 0
int_more = 0
for name in sample:
    p = os.path.join(cal_dir, name)
    im = cv2.imread(p)
    f = detect(fp32, im, 0.3)
    i = detect(int8, im, 0.3)
    fc = [x[0] for x in f]
    ic = [x[0] for x in i]
    if not fc and not ic:
        both_empty += 1
        ok += 1
    elif sorted(fc) == sorted(ic):
        ok += 1
    else:
        diff += 1
        if len(fc) > len(ic):
            fp_more += 1
        elif len(ic) > len(fc):
            int_more += 1
        # 只打印前 5 个差异
        if diff <= 5:
            print(f"  {name}  FP32类别={fc}  INT8类别={ic}")
print(f"\n类别完全一致 {ok}/30  (含两边都空 {both_empty})  不一致 {diff}")
print(f"FP32 多检 {fp_more} 次（INT8 漏检）   INT8 多检 {int_more} 次（INT8 误报）")
