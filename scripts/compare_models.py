"""对比 FP32 vs INT8 模型：检测结果一致性 + 推理速度。"""
import time

import cv2
from ultralytics import YOLO

TEST_IMG = "static/background.png"
WARMUP = 5
ITERS = 30
CONF = 0.3
IMGSZ = 416


def bench(model_dir: str, label: str):
    print(f"\n--- {label} : {model_dir} ---")
    model = YOLO(model_dir, task="detect")
    img = cv2.imread(TEST_IMG)
    # 预热
    for _ in range(WARMUP):
        model.predict(img, conf=CONF, verbose=False, imgsz=IMGSZ)
    # 计时
    t0 = time.time()
    last_boxes = None
    for _ in range(ITERS):
        r = model.predict(img, conf=CONF, verbose=False, imgsz=IMGSZ)[0]
        last_boxes = r.boxes
    elapsed = time.time() - t0
    ms = elapsed / ITERS * 1000
    fps = 1000 / ms
    # 收集类别+置信度
    names = model.names
    dets = []
    if last_boxes is not None and len(last_boxes):
        for b in last_boxes:
            cid = int(b.cls[0])
            cf = float(b.conf[0])
            dets.append((names[cid], round(cf, 3)))
    print(f"平均推理: {ms:.1f} ms / 帧   ≈ {fps:.1f} fps")
    print(f"检测目标: {dets}")
    return ms, dets


print(f"测试图: {TEST_IMG} | conf={CONF} | imgsz={IMGSZ} | warmup={WARMUP} | iters={ITERS}")
fp32_ms, fp32_dets = bench("model/best_openvino_model_fp32", "FP32")
int8_ms, int8_dets = bench("model/best_int8_openvino_model", "INT8")
print(f"\n=== 总结 ===")
print(f"速度: FP32={fp32_ms:.1f}ms  INT8={int8_ms:.1f}ms  提速 {fp32_ms/int8_ms:.2f}x")
print(f"FP32 检测: {fp32_dets}")
print(f"INT8 检测: {int8_dets}")
same_cls = sorted([d[0] for d in fp32_dets]) == sorted([d[0] for d in int8_dets])
print(f"类别一致: {same_cls}")
