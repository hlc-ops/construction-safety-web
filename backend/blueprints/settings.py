"""系统设置蓝图：报警推送、品牌、告警声音、灵敏度（按需仅管理员）。

  GET  /api/settings/alert            读取报警配置（管理员）
  PUT  /api/settings/alert            保存报警配置
  POST /api/settings/alert/test       测试发送
  GET  /api/settings/brand            读取品牌信息（公开，登录页用）
  PUT  /api/settings/brand            保存品牌（管理员）
  POST /api/settings/brand/logo       上传 logo（管理员）
  GET  /api/settings/alert_sound      读取自定义告警音 URL（登录后）
  POST /api/settings/alert_sound      上传 mp3/wav（管理员）
  DEL  /api/settings/alert_sound      清除自定义音
  GET  /api/settings/class_confs      读取按类别灵敏度（管理员）
  PUT  /api/settings/class_confs      保存按类别灵敏度
"""
import json
import os
import time
import uuid
from functools import wraps

from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt

from ..extensions import db
from ..models import Setting
from .. import alert

bp_settings = Blueprint("settings", __name__)


CLASS_NAMES = ["反光衣", "跌倒", "未戴安全帽", "安全帽", "打电话", "吸烟"]
DEFAULT_CLASS_CONF = 0.5

ALLOWED_LOGO_EXT = {"png", "jpg", "jpeg", "svg", "webp"}
ALLOWED_AUDIO_EXT = {"mp3", "wav", "ogg", "m4a"}


def _uploads_dir() -> str:
    d = os.path.join(current_app.config["DATA_DIR"], "uploads")
    os.makedirs(d, exist_ok=True)
    return d


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if get_jwt().get("role") != "admin":
            return jsonify({"code": 403, "msg": "仅管理员可操作"}), 403
        return fn(*args, **kwargs)
    return wrapper


@bp_settings.get("/alert")
@admin_required
def get_alert():
    cfg = alert.get_config()
    return jsonify({"code": 200, "config": cfg})


@bp_settings.put("/alert")
@admin_required
def put_alert():
    data = request.get_json(silent=True) or {}
    Setting.put("alert_enabled", "1" if data.get("enabled") else "0")
    Setting.put("alert_channel", data.get("channel", "dingtalk"))
    Setting.put("alert_webhook", (data.get("webhook") or "").strip())
    Setting.put("alert_cooldown", int(data.get("cooldown") or 30))
    db.session.commit()
    from .. import audit
    audit.log("setting.alert", "setting", "alert",
              f"enabled={bool(data.get('enabled'))} channel={data.get('channel')}")
    return jsonify({"code": 200, "msg": "已保存", "config": alert.get_config()})


@bp_settings.post("/alert/test")
@admin_required
def test_alert():
    data = request.get_json(silent=True) or {}
    channel = data.get("channel", "dingtalk")
    webhook = (data.get("webhook") or "").strip()
    if not webhook:
        return jsonify({"code": 400, "msg": "请先填写 Webhook 地址"}), 400
    ok, msg = alert.send_test(channel, webhook)
    if ok:
        return jsonify({"code": 200, "msg": "测试消息已发送，请查看群消息"})
    return jsonify({"code": 502, "msg": f"发送失败：{msg}"}), 502


# ======================== 品牌定制 ========================

def _brand_config() -> dict:
    return {
        "name": Setting.get("brand_name", "工地安防预警系统"),
        "subtitle": Setting.get("brand_subtitle", "基于深度学习的智能工地安防违规识别平台"),
        "logoUrl": Setting.get("brand_logo_url", ""),
    }


@bp_settings.get("/brand")
def get_brand():
    """登录页要用，无需鉴权。"""
    return jsonify({"code": 200, "config": _brand_config()})


@bp_settings.put("/brand")
@admin_required
def put_brand():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()[:64]
    sub = (data.get("subtitle") or "").strip()[:128]
    if name:
        Setting.put("brand_name", name)
    if "subtitle" in data:
        Setting.put("brand_subtitle", sub)
    if "logoUrl" in data:
        Setting.put("brand_logo_url", (data.get("logoUrl") or "").strip())
    db.session.commit()
    from .. import audit
    audit.log("setting.brand", "setting", "brand", f"name={name}")
    return jsonify({"code": 200, "msg": "已保存", "config": _brand_config()})


@bp_settings.post("/brand/logo")
@admin_required
def upload_logo():
    file = request.files.get("logo")
    if not file:
        return jsonify({"code": 400, "msg": "未上传文件"}), 400
    ext = (file.filename.rsplit(".", 1)[-1] if "." in file.filename else "").lower()
    if ext not in ALLOWED_LOGO_EXT:
        return jsonify({"code": 400, "msg": f"仅支持 {', '.join(ALLOWED_LOGO_EXT)}"}), 400
    fname = f"logo_{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
    path = os.path.join(_uploads_dir(), fname)
    file.save(path)
    if os.path.getsize(path) > 2 * 1024 * 1024:
        os.remove(path)
        return jsonify({"code": 400, "msg": "Logo 需 < 2MB"}), 400
    url = f"/api/uploads/{fname}"
    Setting.put("brand_logo_url", url)
    db.session.commit()
    return jsonify({"code": 200, "logoUrl": url})


# ======================== 自定义告警声音 ========================

@bp_settings.get("/alert_sound")
@jwt_required()
def get_alert_sound():
    return jsonify({"code": 200, "url": Setting.get("alert_sound_url", "")})


@bp_settings.post("/alert_sound")
@admin_required
def upload_alert_sound():
    file = request.files.get("audio")
    if not file:
        return jsonify({"code": 400, "msg": "未上传文件"}), 400
    ext = (file.filename.rsplit(".", 1)[-1] if "." in file.filename else "").lower()
    if ext not in ALLOWED_AUDIO_EXT:
        return jsonify({"code": 400, "msg": f"仅支持 {', '.join(ALLOWED_AUDIO_EXT)}"}), 400
    fname = f"alert_{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
    path = os.path.join(_uploads_dir(), fname)
    file.save(path)
    if os.path.getsize(path) > 1 * 1024 * 1024:
        os.remove(path)
        return jsonify({"code": 400, "msg": "音频需 < 1MB"}), 400
    url = f"/api/uploads/{fname}"
    Setting.put("alert_sound_url", url)
    db.session.commit()
    return jsonify({"code": 200, "url": url})


@bp_settings.delete("/alert_sound")
@admin_required
def clear_alert_sound():
    Setting.put("alert_sound_url", "")
    db.session.commit()
    return jsonify({"code": 200, "msg": "已恢复内置蜂鸣声"})


# ======================== 按类别灵敏度 ========================

def _read_class_confs() -> dict:
    raw = Setting.get("class_confs", "")
    if not raw:
        return {n: DEFAULT_CLASS_CONF for n in CLASS_NAMES}
    try:
        d = json.loads(raw)
        return {n: float(d.get(n, DEFAULT_CLASS_CONF)) for n in CLASS_NAMES}
    except Exception:
        return {n: DEFAULT_CLASS_CONF for n in CLASS_NAMES}


@bp_settings.get("/class_confs")
@admin_required
def get_class_confs():
    return jsonify({"code": 200, "config": _read_class_confs()})


# ======================== 数据保留 + 系统健康 ========================

@bp_settings.get("/retention")
@admin_required
def get_retention():
    from .. import maintenance
    return jsonify({"code": 200, "config": maintenance.get_config()})


@bp_settings.put("/retention")
@admin_required
def put_retention():
    from .. import maintenance
    data = (request.get_json(silent=True) or {}).get("config") or {}
    maintenance.save_config(data)
    from .. import audit
    audit.log("setting.retention", "setting", "retention", str(data))
    return jsonify({"code": 200, "msg": "已保存", "config": maintenance.get_config()})


@bp_settings.post("/retention/run")
@admin_required
def run_cleanup_now():
    """立即跑一次清理。"""
    from flask import current_app
    from .. import maintenance
    stats = maintenance.cleanup_once(current_app._get_current_object())
    from .. import audit
    audit.log("setting.retention.run", "setting", "retention", str(stats))
    return jsonify({"code": 200, "msg": "清理完成", "stats": stats})


@bp_settings.get("/triage")
@admin_required
def get_triage():
    """AI 告警分级开关。"""
    return jsonify({"code": 200, "enabled": Setting.get("triage_enabled", "0") == "1"})


@bp_settings.put("/triage")
@admin_required
def put_triage():
    data = request.get_json(silent=True) or {}
    Setting.put("triage_enabled", "1" if data.get("enabled") else "0")
    db.session.commit()
    from .. import audit
    audit.log("setting.triage", "setting", "triage", f"enabled={bool(data.get('enabled'))}")
    return jsonify({"code": 200, "msg": "已保存", "enabled": data.get("enabled")})


@bp_settings.get("/health")
@admin_required
def health_detail():
    from flask import current_app
    from .. import maintenance
    return jsonify({"code": 200, "metrics": maintenance.health_metrics(
        current_app._get_current_object())})


@bp_settings.put("/class_confs")
@admin_required
def put_class_confs():
    data = (request.get_json(silent=True) or {}).get("config") or {}
    cleaned = {}
    for n in CLASS_NAMES:
        v = data.get(n, DEFAULT_CLASS_CONF)
        try:
            v = float(v)
        except (TypeError, ValueError):
            v = DEFAULT_CLASS_CONF
        cleaned[n] = max(0.05, min(0.95, v))
    Setting.put("class_confs", json.dumps(cleaned, ensure_ascii=False))
    db.session.commit()
    from .. import audit
    audit.log("setting.class_confs", "setting", "class_confs", "")
    return jsonify({"code": 200, "msg": "已保存", "config": cleaned})
