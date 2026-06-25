"""执行 INT8 量化导出。

输入：model/best.pt（原始 PyTorch 权重）
输出：model/best_int8_openvino_model/  （ultralytics 默认命名）
校准：D:/INT8tupian/dataset.yaml
"""
import time

from ultralytics import YOLO

PT = "model/best.pt"
YAML = "D:/INT8tupian/dataset.yaml"
IMGSZ = 416

print(f"加载模型：{PT}")
model = YOLO(PT)

print(f"开始 INT8 量化导出（校准集 300 张，imgsz={IMGSZ}）...")
t0 = time.time()
out = model.export(format="openvino", int8=True, data=YAML, imgsz=IMGSZ)
print(f"\n完成，用时 {time.time() - t0:.1f}s")
print(f"输出：{out}")
