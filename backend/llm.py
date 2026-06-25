"""视觉大模型复核客户端（YOLO 的第二重保险）。

把违规截图 + YOLO 命中的类别交给视觉大模型，让它：
  1) 二次确认是否真的存在该安全隐患（降低 YOLO 误报）；
  2) 用自然语言描述画面；
  3) 给出整改建议。

走 OpenAI 兼容的 chat/completions 接口，通义千问 Qwen-VL 与智谱 GLM-4V 都支持。
未配置 API Key 时返回 ok=False + 友好提示，不抛异常。
"""
import base64
import json
import re

import requests
from flask import current_app


def is_configured() -> bool:
    return bool(current_app.config.get("LLM_API_KEY"))


def _resolve():
    cfg = current_app.config
    provider = cfg.get("LLM_PROVIDER", "qwen")
    defaults = cfg.get("LLM_DEFAULTS", {}).get(provider, {})
    base_url = cfg.get("LLM_BASE_URL") or defaults.get("base_url")
    model = cfg.get("LLM_MODEL") or defaults.get("model")
    return provider, base_url, model, cfg.get("LLM_API_KEY"), cfg.get("LLM_TIMEOUT", 60)


def _image_to_data_url(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64," + base64.b64encode(image_bytes).decode()


PROMPT = (
    "你是工地安全监督专家。这是一张工地监控画面，目标检测模型已初步识别出疑似："
    "{classes}。请你结合画面二次研判，并严格以 JSON 返回，键固定为："
    '{{"confirmed": true/false, "description": "一句话描述画面", "advice": "整改建议"}}。'
    "confirmed 表示是否确实存在安全隐患/违规；若画面正常或检测有误则为 false。只返回 JSON，不要多余文字。"
)


def _parse_json(text: str) -> dict:
    """从模型输出里抽出 JSON。"""
    if not text:
        return {}
    # 去掉可能的 ```json 包裹
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {"description": text.strip()}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {"description": text.strip()}


def review(image_bytes: bytes, cls_list: list) -> dict:
    """对一张截图做大模型复核。返回 dict：

    成功： {ok, confirmed, description, advice, model}
    失败/未配置： {ok: False, msg}
    """
    if not is_configured():
        return {"ok": False, "msg": "未配置大模型 API Key，请在后端环境变量 LLM_API_KEY 中填写后重启"}

    provider, base_url, model, api_key, timeout = _resolve()
    classes = "、".join(cls_list) if cls_list else "未提供具体类别"
    data_url = _image_to_data_url(image_bytes)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT.format(classes=classes)},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        if resp.status_code != 200:
            return {"ok": False, "msg": f"大模型接口返回 {resp.status_code}：{resp.text[:200]}"}
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):  # 个别实现返回分段
            content = "".join(seg.get("text", "") for seg in content if isinstance(seg, dict))
        parsed = _parse_json(content)
        return {
            "ok": True,
            "confirmed": bool(parsed.get("confirmed", True)),
            "description": parsed.get("description", "").strip(),
            "advice": parsed.get("advice", "").strip(),
            "model": model,
        }
    except requests.Timeout:
        return {"ok": False, "msg": "大模型接口超时，请稍后重试"}
    except Exception as e:
        return {"ok": False, "msg": f"大模型调用失败：{e}"}


# ==================== 文本摘要（写日报）====================

REPORT_PROMPT = """你是一名工地安全主管助手。请根据下面这份工地安防{period_zh}数据，写一份**专业、克制、有可执行建议**的工地安全报告。

【数据摘要】
- 时段：{start} 至 {end}
- 总告警：{total} 起（高危 {high} · 中危 {mid} · 低危 {low}）
- 处理情况：已处理 {processed} 起，未处理 {pending} 起
- 工地安全指数：{score}/100（{grade}）
- 高发违规类别（按次数）：{top_classes}
- 高发时段：{peak_hours}

【输出要求】
严格以 JSON 返回，键固定为：
{{
  "summary": "1-2 句总体评价",
  "highlights": ["关键发现 1", "关键发现 2", "关键发现 3"],
  "recommendations": ["可执行建议 1", "可执行建议 2", "可执行建议 3"],
  "outlook": "下阶段重点关注事项"
}}

要求：语气专业克制；不要堆砌数字（数字已在数据里）；建议要具体可执行，不要空话套话。只返回 JSON，不要任何额外说明。"""


def summarize_report(data: dict) -> dict:
    """根据汇总数据让 LLM 写一份自然语言报告。

    data 字段：period_zh / start / end / total / high / mid / low /
               processed / pending / score / grade / top_classes / peak_hours
    返回：{ok, summary, highlights, recommendations, outlook} 或 {ok:False, msg}
    """
    if not is_configured():
        return {"ok": False, "msg": "未配置大模型 API Key"}

    provider, base_url, model, api_key, timeout = _resolve()
    text_model = current_app.config.get("LLM_TEXT_MODEL") or _text_model_for(provider)

    prompt = REPORT_PROMPT.format(**data)
    payload = {
        "model": text_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        resp = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            json=payload, headers=headers, timeout=timeout,
        )
        if resp.status_code != 200:
            return {"ok": False, "msg": f"大模型返回 {resp.status_code}：{resp.text[:200]}"}
        content = resp.json()["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(seg.get("text", "") for seg in content if isinstance(seg, dict))
        parsed = _parse_json(content)
        return {
            "ok": True,
            "summary": parsed.get("summary", ""),
            "highlights": parsed.get("highlights", []),
            "recommendations": parsed.get("recommendations", []),
            "outlook": parsed.get("outlook", ""),
            "model": text_model,
        }
    except requests.Timeout:
        return {"ok": False, "msg": "大模型接口超时"}
    except Exception as e:
        return {"ok": False, "msg": f"大模型调用失败：{e}"}


# ==================== 告警紧急度分级 ====================

TRIAGE_PROMPT = (
    "你是工地安全紧急响应分析师。这张工地监控截图里，YOLO 初步检出：{classes}。"
    "请综合考虑：是否高空作业 / 边缘临边 / 多人聚集 / 危险机械附近，"
    "判断**该告警的紧急程度**。"
    '严格以 JSON 返回：{{"urgency": "immediate|high|normal|low", "reason": "30字内中文原因"}}'
    "规则：immediate=可能立即造成伤亡；high=多人违规或危险区；normal=一般违规；low=远处或轻微。"
    "只返回 JSON。"
)


def triage_alert(image_bytes: bytes, cls_list: list) -> dict:
    """对一张违规截图做紧急度分级。返回 {ok, urgency, reason} 或 {ok:False, msg}。"""
    if not is_configured():
        return {"ok": False, "msg": "未配置大模型"}

    provider, base_url, model, api_key, timeout = _resolve()
    classes = "、".join(cls_list) or "未知"
    data_url = _image_to_data_url(image_bytes)

    payload = {
        "model": model,  # 看图必须用视觉模型
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": TRIAGE_PROMPT.format(classes=classes)},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        resp = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            json=payload, headers=headers, timeout=timeout,
        )
        if resp.status_code != 200:
            return {"ok": False, "msg": f"HTTP {resp.status_code}"}
        content = resp.json()["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(seg.get("text", "") for seg in content if isinstance(seg, dict))
        parsed = _parse_json(content)
        urgency = parsed.get("urgency", "normal")
        if urgency not in ("immediate", "high", "normal", "low"):
            urgency = "normal"
        return {
            "ok": True,
            "urgency": urgency,
            "reason": (parsed.get("reason") or "").strip()[:100],
        }
    except Exception as e:
        return {"ok": False, "msg": str(e)}


def _text_model_for(provider: str) -> str:
    """各厂商的纯文本模型默认值（写日报时用，比视觉模型便宜）。"""
    return {
        "qwen": "qwen-plus",
        "zhipu": "glm-4-flash",
    }.get(provider, "qwen-plus")
