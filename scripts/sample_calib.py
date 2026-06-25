"""INT8 校准图采样脚本。

用法：python scripts/sample_calib.py

输入：D:/Python/PyCharm/PythonProject/construction_safety/dataset (YOLO 格式)
输出：D:/INT8tupian/ （200 张代表性图，按风险优先级分层采样）

思路：
  1. 扫描 train + val 全部图，读对应 txt 标签
  2. 给每张图打"主类"——取所在的"风险最高"类别（让违规场景优先被选中）
  3. 按 6 类 + 合规 + 背景 的目标比例抽样
  4. 用固定 random seed，结果可复现
"""
import os
import random
import shutil
from collections import defaultdict

DATASET = r"D:/Python/PyCharm/PythonProject/construction_safety/dataset"
OUT_DIR = r"D:/INT8tupian"
TOTAL = 300
SEED = 20260613

# 类别 ID → 中文名（来自模型 metadata）
CLS_NAME = {0: "反光衣", 1: "跌倒", 2: "未戴安全帽", 3: "安全帽", 4: "打电话", 5: "吸烟"}

# 优先级：值越大优先级越高（决定一张图的"主类"标签）
PRIORITY = {1: 6, 5: 5, 2: 4, 4: 3, 3: 2, 0: 1}

# 目标采样配额（按主类分桶），总和会再补齐到 TOTAL
TARGETS = {
    1: 30,   # 跌倒
    5: 40,   # 吸烟
    2: 55,   # 未戴安全帽
    4: 30,   # 打电话
    3: 75,   # 安全帽（合规）
    0: 40,   # 反光衣（合规）
    -1: 30,  # 背景（空标签图）
}


def scan_image(image_dir: str, label_dir: str, buckets: dict, all_imgs: list):
    if not os.path.isdir(image_dir):
        return
    for name in os.listdir(image_dir):
        if not name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
            continue
        img_path = os.path.join(image_dir, name)
        stem = os.path.splitext(name)[0]
        txt_path = os.path.join(label_dir, stem + ".txt")
        cls_ids = set()
        if os.path.isfile(txt_path):
            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        cls_ids.add(int(line.split()[0]))
            except Exception:
                pass
        primary = -1
        if cls_ids:
            primary = max(cls_ids, key=lambda c: PRIORITY.get(c, 0))
        buckets[primary].append(img_path)
        all_imgs.append(img_path)


def main():
    print(f"扫描数据集：{DATASET}")
    buckets = defaultdict(list)
    all_imgs = []
    for split in ("train", "val"):
        scan_image(
            os.path.join(DATASET, "images", split),
            os.path.join(DATASET, "labels", split),
            buckets,
            all_imgs,
        )
    print(f"共扫描 {len(all_imgs)} 张图")
    print("\n各主类分布（按优先级落桶）：")
    for cid in sorted(buckets.keys(), key=lambda c: -PRIORITY.get(c, 0)):
        zh = CLS_NAME.get(cid, "背景（空标签）") if cid >= 0 else "背景（空标签）"
        print(f"  {zh:10s}  {len(buckets[cid]):6d} 张")

    rng = random.Random(SEED)
    picked = []
    picked_set = set()
    # 1) 按桶配额抽
    for cid, n in TARGETS.items():
        pool = list(buckets.get(cid, []))
        rng.shuffle(pool)
        take = pool[:n]
        for p in take:
            if p not in picked_set:
                picked.append(p)
                picked_set.add(p)

    # 2) 补齐到 TOTAL（从所有图随机补，避免某桶不足导致总量偏少）
    rest = [p for p in all_imgs if p not in picked_set]
    rng.shuffle(rest)
    while len(picked) < TOTAL and rest:
        picked.append(rest.pop())

    # 3) 复制
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"\n复制到：{OUT_DIR}")
    final_dist = defaultdict(int)
    for src in picked:
        dst = os.path.join(OUT_DIR, os.path.basename(src))
        shutil.copy2(src, dst)
        # 重新算这张图的主类用于报告
        stem = os.path.splitext(os.path.basename(src))[0]
        txt = None
        for split in ("train", "val"):
            cand = os.path.join(DATASET, "labels", split, stem + ".txt")
            if os.path.isfile(cand):
                txt = cand
                break
        cls_ids = set()
        if txt:
            try:
                for line in open(txt, "r", encoding="utf-8"):
                    line = line.strip()
                    if line:
                        cls_ids.add(int(line.split()[0]))
            except Exception:
                pass
        primary = max(cls_ids, key=lambda c: PRIORITY.get(c, 0)) if cls_ids else -1
        final_dist[primary] += 1

    print(f"\n实际复制 {len(picked)} 张，最终分布：")
    for cid in sorted(final_dist.keys(), key=lambda c: -PRIORITY.get(c, 0)):
        zh = CLS_NAME.get(cid, "背景") if cid >= 0 else "背景（空标签）"
        print(f"  {zh:10s}  {final_dist[cid]:3d} 张")
    print("\n完成。")


if __name__ == "__main__":
    main()
