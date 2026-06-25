# 工地安防 · 智能违规检测系统

> 基于 **YOLO + 大语言模型双保险** 的工地安全监管平台,从前端可视化、实时检测、告警推送到 AI 日报全栈实现。

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)
![Vue](https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vue.js&logoColor=white)
![Element Plus](https://img.shields.io/badge/Element--Plus-2.7-409EFF)
![YOLO](https://img.shields.io/badge/YOLO-v8-00FFFF)
![OpenVINO](https://img.shields.io/badge/OpenVINO-2024-005CED)
![LLM](https://img.shields.io/badge/LLM-Qwen--VL%20%2F%20GLM--4V-FF6F00)

---

## 📌 项目亮点

- **YOLO + LLM 双保险检测**:YOLO 第一道(快速、低成本),视觉大模型第二道复核(降低误报、生成整改建议)
- **AI 智能日报**:LLM 自动总结时段告警、生成关键发现 / 执行建议 / 下阶段重点
- **AI 告警智能分级**:每条高危告警由视觉大模型判断真实紧急度,只有 `immediate / high` 才推送钉钉/企微,过滤误报
- **多源检测**:图片、视频文件、本地摄像头、RTSP 网络摄像头四种输入
- **实时告警推送**:Server-Sent Events 实时下发,浏览器内通知 + 蜂鸣 + 自定义提示音
- **商业化功能**:品牌定制(白标 Logo/名称)、电子围栏、安全分数、告警热力图、告警视频片段回放
- **企业级基建**:JWT 鉴权、RBAC 权限、操作审计、登录限频、密码强度校验、数据保留策略、数据库备份、日志轮转
- **单进程部署**:Flask 同时承载 API 与构建好的前端 SPA,一条命令上线

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     浏览器 (SPA)                          │
│   Vue 3 + Pinia + Vue Router + Element Plus + ECharts    │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP / SSE / WebSocket
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  Flask 应用工厂模式                       │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │ 鉴权 JWT │  审计    │  告警    │  SSE 流  │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
│  ┌──────────────────────────────────────────┐           │
│  │       Blueprints: 检测 / 记录 / 摄像头     │           │
│  │       报表 / 设置 / 用户 / LLM 复核        │           │
│  └──────────────────────────────────────────┘           │
└──────┬──────────────────────────────────────┬───────────┘
       │                                       │
       ▼                                       ▼
┌──────────────┐                      ┌──────────────────┐
│ YOLOv8 +     │                      │ 视觉/文本大模型    │
│ OpenVINO 推理 │                      │ Qwen-VL / GLM-4V │
└──────────────┘                      └──────────────────┘
       │                                       │
       ▼                                       ▼
   ┌────────────────────────────────────────────┐
   │     SQLAlchemy ORM  ·  SQLite 持久层        │
   │  用户 · 记录 · 摄像头 · 告警 · 审计 · 设置   │
   └────────────────────────────────────────────┘
```

## ✨ 功能矩阵

| 模块 | 功能 |
|------|------|
| **检测中心** | 图片检测、视频检测、本地摄像头、RTSP 网络摄像头 |
| **记录管理** | 列表筛选、详情对话框、LLM 二次复核、处理状态流转 |
| **摄像头管理** | RTSP 添加 / 删除、健康监测、离线告警、电子围栏配置 |
| **报表中心** | 时段统计、违规类别分布、来源分布、PDF 日报导出、**AI 智能日报** |
| **驾驶舱** | 实时态势、安全分数、告警热力图、告警视频片段回放 |
| **系统设置** | 报警推送、品牌定制、检测灵敏度、告警声音、**AI 告警分级**、数据保留、健康指标 |
| **权限审计** | JWT 登录、RBAC(管理员/普通用户)、操作审计、登录限频、密码强度 |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- (可选)NVIDIA GPU 或 Intel CPU 支持 OpenVINO 加速

### 一、克隆 & 安装

```bash
git clone https://github.com/YOUR_USERNAME/construction-safety-web.git
cd construction-safety-web

# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
cd ..
```

### 二、模型文件

将训练好的 YOLO 模型放到 `model/` 目录(路径可在 `backend/config.py` 调整):

```
model/
├── best_openvino_model/      # OpenVINO 量化后的 INT8 模型(推荐)
└── best.pt                    # 原始 PyTorch 权重(备用)
```

> 自训练步骤见下方《模型训练》章节。

### 三、配置环境变量

```bash
cp .env.example .env
# 编辑 .env,至少填入 LLM_API_KEY
```

### 四、启动

```bash
# 开发模式:前后端分离
# Terminal 1
python run.py                  # 后端 http://localhost:5000

# Terminal 2
cd frontend && npm run dev     # 前端 http://localhost:5173

# 生产模式:单进程
cd frontend && npm run build   # 构建前端到 frontend/dist
cd .. && python run.py          # Flask 同时服务 API 和前端
# 访问 http://localhost:5000
```

默认管理员:`admin / admin123`(首次启动自动创建,登录后请修改密码)

## 📁 项目结构

```
construction-safety-web/
├── backend/                      # Flask 后端 (3226 行)
│   ├── __init__.py               # 应用工厂
│   ├── config.py                 # 配置
│   ├── models.py                 # SQLAlchemy 模型
│   ├── migrate.py                # 自动迁移
│   ├── detector.py               # YOLO + OpenVINO 推理
│   ├── stream.py                 # RTSP 实时流处理
│   ├── llm.py                    # 大模型客户端
│   ├── triage.py                 # AI 告警分级
│   ├── alert.py                  # 告警推送(钉钉/企微)
│   ├── report.py                 # PDF 报表生成
│   ├── maintenance.py            # 数据保留 / 备份 / 日志轮转
│   ├── health.py                 # 摄像头健康监测
│   └── blueprints/               # API 路由
│       ├── auth.py               # 登录 / 注册 / 改密
│       ├── detect.py             # 图片 / 视频 / 摄像头检测
│       ├── records.py            # 告警记录
│       ├── cameras.py            # 摄像头管理
│       ├── reports.py            # 报表 + AI 日报
│       ├── settings.py           # 系统设置
│       └── ...
├── frontend/                     # Vue 3 前端 (6096 行)
│   └── src/
│       ├── views/                # 13 个页面
│       ├── components/           # 公共组件
│       ├── api/                  # HTTP 客户端
│       ├── store/                # Pinia 状态
│       ├── styles/               # 设计令牌系统
│       └── utils/                # SSE / 实时告警 / 时间工具
├── model/                        # YOLO 模型 (gitignored)
├── data/                         # 运行数据 (gitignored)
│   ├── app.db                    # SQLite 数据库
│   ├── snapshots/                # 告警截图
│   ├── clips/                    # 告警视频片段
│   ├── backups/                  # 数据库备份
│   └── logs/                     # 应用日志
├── requirements.txt
├── run.py                        # 启动入口
└── .env.example
```

## 🧠 模型训练

本项目使用 [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) 训练,推荐流程:

```bash
# 1. 训练(以 yolov8s 为例)
yolo detect train data=construction.yaml model=yolov8s.pt epochs=100 imgsz=640

# 2. 导出 OpenVINO INT8 量化模型(CPU 推理提速 3-5 倍)
yolo export model=runs/detect/train/weights/best.pt format=openvino int8=True data=construction.yaml
```

类别可在 `backend/detector.py` 中调整。当前支持:`未戴安全帽 / 未穿反光衣 / 抽烟 / 打架 / 跌倒 / 高空作业未挂安全带 / 烟雾 / 火焰` 等(以训练数据集为准)。

## 📊 数据规模

- **代码量**:9322 行(后端 3226 + 前端 Vue 5361 + JS 471 + CSS 264)
- **后端模块**:28 个
- **前端页面**:13 个 + 5 个公共组件
- **API 路由**:64 条
- **数据库表**:8 张(用户 / 角色 / 记录 / 摄像头 / 设置 / 审计 / 通知去重 / 围栏)

## 🛣️ 路线图

- [x] YOLO + LLM 双保险检测
- [x] 实时 SSE 告警推送
- [x] 钉钉 / 企微 Webhook 推送
- [x] 电子围栏 + 安全分数 + 热力图
- [x] AI 智能日报 + 告警分级
- [x] 数据保留 / 备份 / 日志轮转
- [ ] 多租户 SaaS 化改造
- [ ] PostgreSQL + Redis + Celery 生产架构
- [ ] PyInstaller 打包 / Docker 部署
- [ ] OpenAPI / Swagger 文档
- [ ] 海康 / 大华 SDK 适配

## 🛠️ 技术栈一览

**后端**:Flask 3 · Flask-SQLAlchemy · Flask-JWT-Extended · SQLAlchemy 2 · Ultralytics YOLOv8 · OpenVINO · OpenCV · ReportLab · Requests

**前端**:Vue 3 · Vite 5 · Pinia · Vue Router 4 · Element Plus · ECharts · Axios

**AI**:YOLOv8 (INT8 量化) · Qwen-VL-Plus / GLM-4V (视觉) · Qwen-Plus (文本)

**部署**:单进程 Flask + 内置 SPA 路由回退

## 📝 License

MIT License — 详见 [LICENSE](LICENSE)

## 🙏 致谢

- [Ultralytics](https://github.com/ultralytics/ultralytics) — YOLO 框架
- [OpenVINO](https://github.com/openvinotoolkit/openvino) — Intel 推理引擎
- [Element Plus](https://element-plus.org/) — Vue 3 UI 组件库
- [通义千问](https://tongyi.aliyun.com/) / [智谱 GLM](https://chatglm.cn/) — 视觉大模型

---

如果这个项目对你有启发,欢迎 ⭐ Star 支持。
