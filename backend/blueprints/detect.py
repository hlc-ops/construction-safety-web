"""检测推理蓝图：图片 / 视频帧 / 摄像头帧。

接口（均需登录）返回标注图（base64）+ 中文类别 + 风险标记。是否落库由前端
在合适时机调用 /api/records 决定（沿用原有"前端节流抓拍"逻辑）。
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ..detector import get_detector, decode_data_url, encode_jpg_data_url, risk_level

bp_detect = Blueprint("detect", __name__)


def _valid_zone(zone):
    """校验归一化矩形 {x1,y1,x2,y2}，非法返回 None。"""
    if not isinstance(zone, dict):
        return None
    try:
        x1, y1, x2, y2 = (float(zone[k]) for k in ("x1", "y1", "x2", "y2"))
    except (KeyError, TypeError, ValueError):
        return None
    x1, x2 = sorted((max(0.0, x1), min(1.0, x2)))
    y1, y2 = sorted((max(0.0, y1), min(1.0, y2)))
    if x2 - x1 < 0.02 or y2 - y1 < 0.02:  # 太小视为无效
        return None
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def _get_class_confs():
    """从 Setting 读取按类别灵敏度，若未配置返回 None。"""
    from ..models import Setting
    raw = Setting.get("class_confs", "")
    if not raw:
        return None
    try:
        import json
        return json.loads(raw)
    except Exception:
        return None


def _detect_dataurl(image_data_url: str, conf: float, quality: int = 70, zone=None):
    frame = decode_data_url(image_data_url)
    if frame is None:
        raise ValueError("图像解码失败")
    drawn, cls_list, high, mid, boxes = get_detector().detect(frame, conf, zone, _get_class_confs())
    return {
        "code": 200,
        "img": encode_jpg_data_url(drawn, quality),
        "high_risk": high,
        "mid_risk": mid,
        "risk": risk_level(high, mid),
        "cls_list": cls_list,
        "boxes": boxes,
    }


@bp_detect.post("/image")
@jwt_required()
def detect_image():
    """multipart 上传图片检测。"""
    try:
        import cv2
        import numpy as np

        import json as _json
        img_file = request.files["image"]
        conf = float(request.form.get("conf", 0.5))
        zone = _valid_zone(_json.loads(request.form.get("zone", "null") or "null"))
        nparr = np.frombuffer(img_file.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"code": 400, "msg": "图片无效"}), 400
        drawn, cls_list, high, mid, boxes = get_detector().detect(img, conf, zone, _get_class_confs())
        return jsonify({
            "code": 200,
            "img": encode_jpg_data_url(drawn, 70),
            "high_risk": high,
            "mid_risk": mid,
            "risk": risk_level(high, mid),
            "cls_list": cls_list,
            "boxes": boxes,
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)}), 500


@bp_detect.post("/frame")
@jwt_required()
def detect_frame():
    """摄像头实时帧（base64 dataURL）。"""
    try:
        data = request.get_json() or {}
        conf = float(data.get("conf", 0.5))
        zone = _valid_zone(data.get("zone"))
        return jsonify(_detect_dataurl(data["image"], conf, quality=60, zone=zone))
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)}), 500


@bp_detect.post("/video_frame")
@jwt_required()
def detect_video_frame():
    """视频逐帧（base64 dataURL）。"""
    try:
        data = request.get_json() or {}
        conf = float(data.get("conf", 0.5))
        zone = _valid_zone(data.get("zone"))
        return jsonify(_detect_dataurl(data["image"], conf, quality=60, zone=zone))
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)}), 500
