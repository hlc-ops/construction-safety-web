"""大模型复核蓝图。

  GET  /api/llm/status          查询是否已配置大模型
  POST /api/llm/review          对某条记录做视觉大模型二次复核，结果写回记录
       body: { "recordId": 123 }
"""
import os

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import DetectionRecord
from .. import llm

bp_llm = Blueprint("llm", __name__)


@bp_llm.get("/status")
@jwt_required()
def status():
    return jsonify({
        "code": 200,
        "configured": llm.is_configured(),
        "provider": current_app.config.get("LLM_PROVIDER"),
    })


@bp_llm.post("/review")
@jwt_required()
def review():
    data = request.get_json(silent=True) or {}
    rid = data.get("recordId")
    rec = db.session.get(DetectionRecord, rid) if rid else None
    if not rec:
        return jsonify({"code": 404, "msg": "记录不存在"}), 404
    if not rec.image_path:
        return jsonify({"code": 400, "msg": "该记录没有截图，无法复核"}), 400

    img_file = os.path.join(current_app.config["SNAPSHOT_DIR"], rec.image_path)
    if not os.path.exists(img_file):
        return jsonify({"code": 400, "msg": "截图文件丢失"}), 400

    with open(img_file, "rb") as f:
        image_bytes = f.read()

    result = llm.review(image_bytes, rec.cls_list)
    if not result.get("ok"):
        return jsonify({"code": 503, "msg": result.get("msg", "大模型复核失败")}), 503

    # 写回记录
    rec.llm_reviewed = True
    rec.llm_confirmed = result.get("confirmed")
    rec.llm_description = result.get("description", "")
    rec.llm_advice = result.get("advice", "")
    db.session.commit()

    return jsonify({"code": 200, "msg": "复核完成", "result": result, "record": rec.to_dict()})
