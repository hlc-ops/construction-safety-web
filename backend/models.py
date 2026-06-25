"""数据库模型：用户 与 检测记录。"""
import json
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(64), default="")
    # 角色：admin（管理员）/ operator（操作员）
    role = db.Column(db.String(16), default="operator", nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)  # 停用后不能登录
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    records = db.relationship(
        "DetectionRecord",
        backref="user",
        lazy=True,
        foreign_keys="DetectionRecord.user_id",
    )

    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "realName": self.real_name,
            "role": self.role,
            "enabled": bool(self.enabled),
            "createdAt": self.created_at.isoformat() + "Z" if self.created_at else None,
            "lastLogin": self.last_login.isoformat() + "Z" if self.last_login else None,
        }


class AuditLog(db.Model):
    """审计日志：登录、配置改动、关键操作留痕。"""
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(64), default="")
    action = db.Column(db.String(64), nullable=False, index=True)   # 如 login.success
    target_type = db.Column(db.String(32), default="")              # user / camera / record / setting
    target_id = db.Column(db.String(32), default="")
    ip = db.Column(db.String(64), default="")
    detail = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    ACTION_ZH = {
        "login.success": "登录成功",
        "login.fail": "登录失败",
        "logout": "退出登录",
        "user.create": "新建用户",
        "user.update": "修改用户",
        "user.delete": "删除用户",
        "user.set_status": "启停用户",
        "user.reset_password": "重置密码",
        "camera.create": "新建摄像头",
        "camera.update": "修改摄像头",
        "camera.delete": "删除摄像头",
        "camera.start": "启动摄像头",
        "camera.stop": "停止摄像头",
        "setting.alert": "修改报警配置",
        "record.delete": "删除记录",
        "record.batch": "批量处理记录",
    }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "userId": self.user_id,
            "username": self.username,
            "action": self.action,
            "actionZh": self.ACTION_ZH.get(self.action, self.action),
            "targetType": self.target_type,
            "targetId": self.target_id,
            "ip": self.ip,
            "detail": self.detail,
            "createdAt": self.created_at.isoformat() + "Z" if self.created_at else None,
        }


class Camera(db.Model):
    """摄像头档案：多路 RTSP/IP/USB 设备的统一登记。"""
    __tablename__ = "cameras"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    url = db.Column(db.String(255), nullable=False)        # rtsp://... 或文件路径
    location = db.Column(db.String(128), default="")        # 安装位置
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    conf = db.Column(db.Float, default=0.5)                 # 默认置信度
    snap_interval = db.Column(db.Integer, default=10)
    # 检测时段：开启后仅在 [start, end] 内做 YOLO 检测，时段外只拉流不识别
    schedule_enabled = db.Column(db.Boolean, default=False, nullable=False)
    schedule_start = db.Column(db.String(5), default="07:00")  # HH:MM
    schedule_end = db.Column(db.String(5), default="19:00")
    last_online_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, online=False, error="") -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "location": self.location or "",
            "enabled": bool(self.enabled),
            "conf": self.conf,
            "snapInterval": self.snap_interval,
            "scheduleEnabled": bool(self.schedule_enabled),
            "scheduleStart": self.schedule_start or "07:00",
            "scheduleEnd": self.schedule_end or "19:00",
            "lastOnlineAt": self.last_online_at.isoformat() + "Z" if self.last_online_at else None,
            "createdAt": self.created_at.isoformat() + "Z" if self.created_at else None,
            "online": online,           # 当前是否拉流中
            "error": error,             # 拉流错误（如有）
        }


class Setting(db.Model):
    """键值配置表：存放可在线修改、无需重启的配置（如报警 webhook）。"""
    __tablename__ = "settings"

    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text, default="")

    @staticmethod
    def get(key: str, default=None):
        row = db.session.get(Setting, key)
        return row.value if row else default

    @staticmethod
    def put(key: str, value):
        row = db.session.get(Setting, key)
        if row:
            row.value = "" if value is None else str(value)
        else:
            db.session.add(Setting(key=key, value="" if value is None else str(value)))


class DetectionRecord(db.Model):
    __tablename__ = "detection_records"

    id = db.Column(db.Integer, primary_key=True)
    # 来源类型：img（图片）/ video（视频）/ camera（实时）
    record_type = db.Column(db.String(16), nullable=False, index=True)
    # 风险等级：high / mid / low
    risk_level = db.Column(db.String(8), nullable=False, index=True)
    # 处理状态：pending（未处理）/ processed（已处理）
    status = db.Column(db.String(16), default="pending", nullable=False, index=True)

    image_path = db.Column(db.String(255), nullable=True)  # 相对快照文件名
    clip_path = db.Column(db.String(255), nullable=True)   # 告警视频片段文件名(mp4)
    cls_list_json = db.Column(db.Text, default="[]")        # 命中的中文类别列表
    remark = db.Column(db.Text, default="")                 # 处理意见

    duration_seconds = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # ---- 视觉大模型二次复核结果 ----
    llm_reviewed = db.Column(db.Boolean, default=False)
    llm_confirmed = db.Column(db.Boolean, nullable=True)   # 大模型是否确认存在隐患
    llm_description = db.Column(db.Text, default="")        # 画面描述
    llm_advice = db.Column(db.Text, default="")            # 整改建议

    # ---- AI 告警分级（LLM 看图后给出真实紧急度，替补单纯的 risk_level）----
    urgency = db.Column(db.String(16), nullable=True)        # immediate/high/normal/low
    urgency_reason = db.Column(db.String(255), default="")
    urgency_at = db.Column(db.DateTime, nullable=True)

    # ---- 工单流（pending/processing/processed/closed） + 分配 + 升级 ----
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    escalated = db.Column(db.Boolean, default=False)
    escalated_at = db.Column(db.DateTime, nullable=True)
    processed_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

    # 风险等级 → 中文显示
    RISK_ZH = {"high": "高危", "mid": "中危", "low": "低危"}
    TYPE_ZH = {"img": "图片检测", "video": "视频检测", "camera": "实时检测"}
    STATUS_ZH = {
        "pending": "待处理", "processing": "处理中",
        "processed": "已处理", "closed": "已关闭",
    }
    URGENCY_ZH = {
        "immediate": "立即处置", "high": "紧急", "normal": "一般", "low": "可缓",
    }

    @property
    def cls_list(self) -> list:
        try:
            return json.loads(self.cls_list_json or "[]")
        except Exception:
            return []

    @cls_list.setter
    def cls_list(self, value):
        self.cls_list_json = json.dumps(value or [], ensure_ascii=False)

    def to_dict(self) -> dict:
        img_url = f"/api/snapshots/{self.image_path}" if self.image_path else None
        clip_url = f"/api/clips/{self.clip_path}" if self.clip_path else None
        return {
            "id": self.id,
            "type": self.record_type,
            "clipUrl": clip_url,
            "typeZh": self.TYPE_ZH.get(self.record_type, self.record_type),
            "risk": self.risk_level,
            "riskZh": self.RISK_ZH.get(self.risk_level, self.risk_level),
            "status": self.status,
            "statusZh": self.STATUS_ZH.get(self.status, self.status),
            "imgUrl": img_url,
            "clsList": self.cls_list,
            "remark": self.remark or "",
            "duration": f"{self.duration_seconds:.1f}s",
            "durationSeconds": self.duration_seconds,
            "startedAt": self.started_at.isoformat() + "Z" if self.started_at else None,
            "endedAt": self.ended_at.isoformat() + "Z" if self.ended_at else None,
            "createdAt": self.created_at.isoformat() + "Z" if self.created_at else None,
            "llmReviewed": bool(self.llm_reviewed),
            "llmConfirmed": self.llm_confirmed,
            "llmDescription": self.llm_description or "",
            "llmAdvice": self.llm_advice or "",
            "urgency": self.urgency,
            "urgencyZh": self.URGENCY_ZH.get(self.urgency, "") if self.urgency else "",
            "urgencyReason": self.urgency_reason or "",
            "urgencyAt": self.urgency_at.isoformat() + "Z" if self.urgency_at else None,
            "assigneeId": self.assignee_id,
            "escalated": bool(self.escalated),
            "escalatedAt": self.escalated_at.isoformat() + "Z" if self.escalated_at else None,
            "processedAt": self.processed_at.isoformat() + "Z" if self.processed_at else None,
            "closedAt": self.closed_at.isoformat() + "Z" if self.closed_at else None,
        }
