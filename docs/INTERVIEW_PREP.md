# 工地安防系统 · 面试深度准备文档

> 本文档用于面试讲述这个项目时的**技术深度准备**。目标:让面试官从"听你讲完"到"想录用你"。
> 阅读顺序建议:第一章背熟 → 第二、三、四章理解 → 第五、六章重点理解原理 → 第九章模拟问答。

---

## 📑 目录

0. [新手友好:术语字典](#零新手友好术语字典)
1. [项目电梯介绍(必背)](#一项目电梯介绍必背)
2. [项目背景与选题](#二项目背景与选题)
3. [整体架构设计](#三整体架构设计)
4. [技术栈选型与理由](#四技术栈选型与理由)
5. [核心算法详解](#五核心算法详解)
6. [工程难点与解决方案](#六工程难点与解决方案)
7. [性能数据与优化](#七性能数据与优化)
8. [工程化细节](#八工程化细节)
9. [高频面试问题与标准答案](#九高频面试问题与标准答案)
10. [反问面试官的高质量问题](#十反问面试官的高质量问题)
11. [演示视频操作步骤(逐键说明)](#十一演示视频操作步骤逐键说明)

---

## 零、新手友好:术语字典

> **这一章帮你快速理解后面的"黑话"**。看不懂就回来查,看懂了就忽略。

### 后端/Web 相关

| 术语 | 大白话解释 |
|---|---|
| **Flask** | Python 的轻量 Web 框架,写后端 API 用的。"路由 = 哪个 URL 触发哪个函数" |
| **Blueprint** | Flask 的"模块",把路由分文件,避免一个文件几千行 |
| **应用工厂模式** | 用 `create_app()` 函数生成 Flask 实例,而不是写全局 `app = Flask(...)`。方便测试 |
| **ORM** | Object-Relational Mapping。让你用 Python 类操作数据库,不用写 SQL |
| **SQLAlchemy** | Python 最流行的 ORM 库 |
| **JWT** | JSON Web Token,登录后服务器发的"身份令牌",前端每次请求带上它 |
| **JWT 的 jti** | 每个 token 的唯一 ID,用来"拉黑"已登出的 token |
| **RBAC** | Role-Based Access Control,基于角色的权限。管理员能干啥、普通用户能干啥 |
| **CORS** | 跨域资源共享。前端 localhost:5173 调后端 localhost:5000,默认浏览器禁止,要后端允许 |
| **SSE** | Server-Sent Events,服务器主动推消息给浏览器(单向),适合实时通知 |
| **WebSocket** | 双向实时通信,比 SSE 重 |
| **SPA** | Single Page Application,单页应用,刷新页面不重载,路由前端控制 |
| **RTSP** | Real Time Streaming Protocol,网络摄像头常用协议(`rtsp://...`) |
| **Webhook** | 一个 HTTP 接口地址,你发消息过去,它帮你转给钉钉/企微群 |
| **PRAGMA** | SQLite 的元命令,查表结构用 `PRAGMA table_info(表名)` |

### 算法 / AI 相关

| 术语 | 大白话解释 |
|---|---|
| **YOLO** | You Only Look Once,主流目标检测算法。"一眼看完整张图,直接框出所有目标" |
| **YOLOv8** | YOLO 的第 8 代,2023 年 Ultralytics 出的,目前工业界最稳定 |
| **目标检测** | 给一张图,找出物体在哪(框)+ 是什么(类别) |
| **mAP** | mean Average Precision,平均精度。目标检测的核心指标,**0.82 算还不错** |
| **mAP@0.5** | IoU 阈值取 0.5 时算的 mAP(框重叠 ≥ 50% 算检对) |
| **IoU** | Intersection over Union,两个框的"交集面积/并集面积",衡量重叠度 |
| **CIoU** | Complete IoU,IoU 的改进版,考虑中心距离 + 长宽比,优化更稳 |
| **NMS** | Non-Maximum Suppression,非极大值抑制。同一目标可能被检出多个重叠框,NMS 留最优 |
| **Anchor** | 预设的候选框,老版 YOLO 用,新版 anchor-free(不需要预设) |
| **Backbone** | "骨干网络",负责提特征。比如 CSPDarknet |
| **Neck** | "脖子",做多尺度特征融合,比如 FPN/PAN |
| **Head** | "头",最终出预测结果(类别+框) |
| **FPN** | Feature Pyramid Network,特征金字塔,多尺度融合 |
| **PAN** | Path Aggregation Network,FPN 的升级版,双向融合 |
| **DFL** | Distribution Focal Loss,把"框的位置"建模成概率分布,定位更准 |
| **BCE** | Binary Cross Entropy,二分类交叉熵,分类常用损失函数 |
| **量化** | 把模型从 FP32(4字节)压到 INT8(1字节),小 4 倍快 2-5 倍 |
| **PTQ** | Post-Training Quantization,训练完再量化,简单 |
| **QAT** | Quantization-Aware Training,边训边量化,精度更高但慢 |
| **OpenVINO** | Intel 的推理加速框架,在 Intel CPU 上比 PyTorch 快 3-5 倍 |
| **NNCF** | Neural Network Compression Framework,Intel 的量化工具 |
| **LATENCY 模式** | 单流低延迟,实时摄像头用 |
| **THROUGHPUT 模式** | 多流高吞吐,批处理用 |
| **LLM** | Large Language Model,大语言模型(如 GPT、通义千问) |
| **VLM** | Vision Language Model,视觉大模型(能看图+回答),如 Qwen-VL、GPT-4V |
| **Qwen-VL** | 阿里通义千问的视觉版本 |
| **GLM-4V** | 智谱 AI 的视觉大模型 |
| **prompt** | 给 LLM 的输入指令 |
| **temperature** | LLM 的"随机度",0 = 完全确定,1 = 创意发挥 |
| **token** | LLM 处理的最小单位,大约 1 个中文字符 = 1-2 token |

### 前端 / Vue 相关

| 术语 | 大白话解释 |
|---|---|
| **Vue 3** | 前端框架,写组件化界面 |
| **Composition API** | Vue 3 推荐的写法,用 `setup()` 函数 + `ref/reactive`,比 Options API 灵活 |
| **`<script setup>`** | Composition API 的语法糖,更简洁 |
| **Pinia** | Vue 3 的状态管理库(全局数据共享),替代 Vuex |
| **Element Plus** | Vue 3 的 UI 组件库(按钮、表格、对话框等) |
| **Vite** | 前端构建工具,比 Webpack 快很多 |
| **Axios** | HTTP 客户端,前端调后端 API 用 |
| **路由守卫** | 进入页面前的检查,比如"未登录就跳登录页" |
| **响应拦截器** | Axios 的全局处理,所有响应统一过一遍(比如 401 跳登录) |

### 部署 / 工程相关

| 术语 | 大白话解释 |
|---|---|
| **Gunicorn** | Python 的生产级 WSGI 服务器,替代 Flask 自带的 dev server |
| **Nginx** | 反向代理服务器,做 SSL、负载均衡、静态文件加速 |
| **Docker** | 容器化部署,把应用打包成镜像 |
| **CI/CD** | 持续集成/持续部署,代码提交后自动测试、构建、上线 |
| **Sentry** | 错误监控平台,前端/后端崩溃自动上报 |
| **Prometheus + Grafana** | 监控指标采集 + 可视化 |
| **ELK** | Elasticsearch + Logstash + Kibana,日志聚合三件套 |
| **Celery** | Python 的异步任务队列,处理耗时任务(发邮件、跑算法) |
| **Redis** | 内存数据库,做缓存、队列、分布式锁 |
| **Alembic** | SQLAlchemy 的数据库迁移工具,正式项目用 |

### 设计模式 / 架构

| 术语 | 大白话解释 |
|---|---|
| **单进程部署** | 整个应用一个 Python 进程跑完,SQLite + Flask + 前端静态文件全在一起 |
| **微服务** | 把应用拆成多个独立服务,各自部署。规模大才需要 |
| **多租户** | 一套系统服务多个客户,数据隔离。SaaS 必备 |
| **降级** | 某个依赖挂了,主功能仍能用(比如 LLM 挂了,YOLO 仍工作) |
| **熔断** | 某依赖失败率高,直接不调用,避免雪崩 |
| **幂等** | 同一操作执行 N 次结果一样(比如订单 ID 防重复提交) |
| **STAR 法** | Situation-Task-Action-Result,讲故事的结构 |

> ✅ **看不懂的术语**:百度/Google "XX 是什么 通俗解释",或者问 ChatGPT/Claude "用大白话解释 XX"。**不要装懂**,搞清楚比硬背强 10 倍。

---

## 一、项目电梯介绍(必背)

### 30 秒版(自我介绍后被问"讲一下你的项目")

> "我做了一个工地安防违规检测系统,9000 多行代码,单人独立全栈开发。
> 核心特色是 **YOLO 加大模型的双保险架构**:YOLO 第一道做快速目标检测,视觉大模型第二道做语义复核和整改建议生成,显著降低了纯 YOLO 的误报率。
> 技术栈是 Vue 3 加 Flask,集成 YOLOv8 加 OpenVINO INT8 量化,CPU 单路 RTSP 推理能跑到 15+ FPS。
> 系统涵盖图片、视频、本地摄像头、RTSP 四种检测、SSE 实时告警、电子围栏、AI 智能日报、白标定制、数据保留备份等商业级功能,共 13 个页面、64 条 API。"

### 60 秒版(被问"详细说说")

加上这一段:
> "工程亮点上,我用 Flask 应用工厂 + Blueprint 做了模块化,SQLAlchemy ORM + 自动 PRAGMA 迁移、JWT 鉴权 + RBAC 权限、操作审计、登录限频、SSE 实时推送、钉钉企微 Webhook、PDF 报表生成。
> 算法侧除了 YOLO 主链路,还做了大模型异步分级——视觉大模型判断每条高危告警的真实紧急度,只有'立即处置'级别才推送钉钉,实测过滤了 60-70% 的无效推送。
> 整个系统能单进程部署:Flask 同时托管 API 和构建好的 Vue SPA,SQLite 持久化,一条命令就能上线,目标客户是工地工控机这种 CPU 单机环境。"

---

## 二、项目背景与选题

### 行业痛点(讲故事用)

1. **传统人工巡检效率低**:工地面积大、违规行为分散,安全员一人盯 N 个区域,漏检率高
2. **传统 AI 系统误报多**:纯 YOLO 检测在工地复杂场景下,光照/遮挡/反光导致误报率 30%+
3. **报警没有可执行性**:传统系统只告诉你"违规了",不告诉你"整改怎么做"
4. **海康/广联达等商业系统贵且封闭**:几十万一个项目,二次开发空间小

### 我的设计哲学(讲价值观)

- **降低误报优先于提升召回**:工地宁可漏报 5% 也不能误报 30% 刷屏
- **AI 可解释 > AI 黑盒**:每条告警必须能讲清"为什么是违规"
- **轻量级部署 > 重型云架构**:工地网络差,边缘部署是刚需

### 为什么是个有价值的项目(讲商业)

- 工地安全是**强监管行业**,有刚性需求(应急管理部要求)
- 双保险架构是当前少数能真正降低误报的方案
- 单人能做出商业级 MVP,验证全栈 + 算法工程能力

---

## 三、整体架构设计

### 架构图(口述时画在纸上)

```
┌─────────────────────────────────────────────┐
│  浏览器 SPA (Vue 3 + Element Plus)           │
│  ├─ 13 个业务页面                            │
│  ├─ Pinia 状态管理                           │
│  └─ Axios 拦截器 + Vue Router 路由守卫        │
└──────────────┬──────────────────────────────┘
               │ HTTP/SSE/multipart
               ▼
┌─────────────────────────────────────────────┐
│  Flask 应用工厂(单进程)                      │
│  ├─ JWT 鉴权中间件                           │
│  ├─ CORS / 错误统一处理                       │
│  ├─ 8 个 Blueprint(模块化路由)               │
│  └─ SPA 路由回退(404 → index.html)          │
└────┬──────────────┬──────────────┬──────────┘
     │              │              │
     ▼              ▼              ▼
 检测引擎层      数据持久层      集成服务层
 ┌────────┐    ┌──────────┐  ┌────────────┐
 │ YOLOv8 │    │SQLAlchemy│  │ Qwen-VL    │
 │ +Open  │    │+ SQLite  │  │ 钉钉Webhook│
 │ VINO   │    │  + 自迁移 │  │ 企微Webhook│
 └────────┘    └──────────┘  └────────────┘
     ↑
 ┌────────────────────────────────┐
 │ 后台异步任务(threading)         │
 │ ├─ StreamWorker:RTSP 拉流推理   │
 │ ├─ HealthWatcher:摄像头心跳     │
 │ ├─ AlertNotifier:告警推送       │
 │ ├─ TriageWorker:LLM 异步分级    │
 │ └─ Maintainer:数据保留/备份/日志│
 └────────────────────────────────┘
```

### 分层职责

| 层 | 职责 | 文件 |
|---|---|---|
| **接入层** | HTTP 路由、鉴权、参数校验、CORS | `backend/blueprints/*.py` |
| **业务层** | 业务规则、数据组装、状态机 | `backend/{records,reports,...}.py` |
| **算法层** | YOLO 推理、LLM 调用、双保险编排 | `backend/{detector,llm,triage}.py` |
| **持久层** | ORM、自动迁移、设置 KV | `backend/{models,migrate}.py` |
| **任务层** | 异步后台、流处理、告警 | `backend/{stream,alert,maintenance}.py` |

### 设计原则(讲工程素养)

1. **单一职责**:每个 Blueprint 一种业务能力,文件 < 300 行
2. **应用工厂模式**:`create_app()` 接受 config,便于测试 + 多环境
3. **配置外部化**:`.env` 管理敏感配置,代码不含硬编码
4. **失败优雅降级**:LLM 不可用时,YOLO 仍能独立工作
5. **可观测**:每条关键路径都有审计日志

---

## 四、技术栈选型与理由

> **面试核心信号:你不是"会用",你是"为什么用这个不用那个"**。每个选型都要有 trade-off。

### 后端框架:Flask vs FastAPI vs Django

| 候选 | 选 Flask 的理由 |
|---|---|
| Flask ✅ | 轻量、生态成熟、可控性高、适合中型项目;Blueprint 模块化够用 |
| FastAPI | 异步性能更好,但对我的场景(CPU 密集型 YOLO 推理)没差别;学习成本略高 |
| Django | 太重,自带 admin/auth 一堆我不需要的;ORM 迁移走 migrations 流程比我用的自动 PRAGMA 重 |

**结论**:Flask 在"轻 + 模块化 + 控制力"三角上最优。

### 前端框架:Vue 3 vs React vs Angular

| 候选 | 选 Vue 3 的理由 |
|---|---|
| Vue 3 ✅ | Composition API + `<script setup>` 心智模型简单;Element Plus 是当前最成熟的 B 端组件库,工地后台界面直接复用 |
| React | 生态更大,但 B 端组件 Antd 设计偏小程序风格,商业感不如 Element Plus;hooks 心智成本对个人项目偏高 |
| Angular | 学习曲线陡,对个人项目过重 |

**结论**:B 端管理系统选型,Vue 3 + Element Plus 是性价比最高的组合。

### 数据库:SQLite vs PostgreSQL vs MySQL

| 候选 | 当前选 SQLite 的理由 |
|---|---|
| SQLite ✅ | **嵌入式无需独立进程**,一个文件部署;读多写少场景性能够用;工控机环境装 PG 反而麻烦 |
| PostgreSQL | 真正商业化必须换;SQLite 单文件锁在并发写多于几路摄像头时会成瓶颈 |
| MySQL | 同 PG;但 PG 的 JSONB 和数组类型对扩展性更好 |

**坦诚承认局限**:"如果上线工地多于 5 路摄像头,我会换到 PostgreSQL 并引入 Redis 缓存"——这种"我知道边界"的回答比硬撑更打动面试官。

### 推理引擎:OpenVINO vs TensorRT vs ONNX Runtime

| 候选 | 选 OpenVINO 的理由 |
|---|---|
| OpenVINO ✅ | 目标部署环境是 Intel CPU 工控机;OpenVINO 在 Intel CPU 上比 ONNX Runtime 快 3-5 倍 |
| TensorRT | NVIDIA 专用;工地很少有 GPU |
| ONNX Runtime | 通用但 CPU 优化不如 OpenVINO |

### 检测模型:YOLOv8 vs v9/v10/v11

| 候选 | 选 YOLOv8 的理由 |
|---|---|
| YOLOv8 ✅ | 最成熟的工程生态;Ultralytics 文档完善;v8s 精度速度平衡好;社区量化方案多 |
| v9 / v10 | mAP 提升 1-2%,但工程支持弱;v10 端到端 NMS-free 是亮点但部署链路不成熟 |
| v11 | 2024 新版,但还在快速迭代,不稳定 |

**回答口径**:"我选稳定够用的,不追新"——这是工程师的态度。

### 实时通信:SSE vs WebSocket vs 长轮询

| 候选 | 选 SSE 的理由 |
|---|---|
| SSE ✅ | 单向(服务器→客户端)正好匹配告警场景;基于 HTTP,穿透防火墙好;浏览器自动重连;实现简单 |
| WebSocket | 双向,但告警不需要客户端推消息;握手协议复杂;鉴权要单独处理 |
| 长轮询 | 服务器压力大,延迟高 |

### 状态管理:Pinia vs Vuex

- Pinia ✅:Vue 3 官方推荐,TypeScript 友好,API 更直观;Vuex 4 仍可用但被 Pinia 取代

---

## 五、核心算法详解

### 5.1 YOLOv8 原理(必须能讲)

**整体结构**:Backbone → Neck → Head

```
输入 (640×640×3)
    ↓
Backbone (CSPDarknet 改进版)
  ├─ 多次卷积下采样 + C2f 模块
  └─ 输出 P3/P4/P5 三层特征 (80×80, 40×40, 20×20)
    ↓
Neck (PAN-FPN 路径聚合)
  ├─ 自底向上 + 自顶向下双向融合
  └─ 三尺度特征图聚合
    ↓
Head (Decoupled + Anchor-Free)
  ├─ 分类分支 (BCE Loss)
  ├─ 回归分支 (CIoU + DFL Loss)
  └─ 直接输出 (cx, cy, w, h) 而非偏移
    ↓
NMS 后处理 → 最终框
```

**关键改进点(对比 YOLOv5)**:
1. **Anchor-Free**:不再需要预设 anchor,直接回归;减少超参,适应性强
2. **Decoupled Head**:分类和回归分开两个分支,避免互相干扰
3. **C2f 模块替换 C3**:更多跨层连接,梯度流更顺
4. **DFL(Distribution Focal Loss)**:把框坐标建模为分布,而非单点回归;提升定位精度
5. **TaskAlignedAssigner**:动态匹配正负样本,改善小目标

**损失函数**:
- 分类:**BCE Loss**(二分类交叉熵)
- 回归:**CIoU Loss**(考虑中心距离、长宽比)+ **DFL**(分布回归)
- 总损失:`Loss = λ_cls·L_cls + λ_box·L_box + λ_dfl·L_dfl`

### 5.2 INT8 量化原理(讲清能加分)

**为什么量化**:FP32(4 字节)→ INT8(1 字节),模型大小压缩 4 倍,推理速度提升 2-5 倍(取决于硬件)。

**两种方式**:

| 方法 | 全称 | 流程 | 精度损失 |
|---|---|---|---|
| **PTQ** ✅ 我用的 | Post-Training Quantization 训练后量化 | 准备 100-500 张校准集 → 统计激活分布 → 计算 scale/zero_point → 量化权重和激活 | 0.5-2% mAP |
| QAT | Quantization-Aware Training 量化感知训练 | 训练时插入伪量化算子,反向传播感知量化误差 | 0-0.5% mAP 但需重新训练 |

**量化数学**:
```
量化:  q = round(x / scale) + zero_point
反量化: x = (q - zero_point) × scale
```

`scale` 和 `zero_point` 是按 tensor(per-tensor)或按通道(per-channel)统计得到。

**我用的工具**:NNCF(Neural Network Compression Framework,Intel 出品),通过 `yolo export format=openvino int8=True data=xxx.yaml` 一行命令完成。

### 5.3 OpenVINO 推理引擎

**OpenVINO 是什么**:Intel 的 Open Visual Inference and Neural network Optimization,专门优化 Intel CPU/GPU/VPU 的推理。

**核心概念**:
- **IR(Intermediate Representation)**:`.xml`(结构)+ `.bin`(权重),从 ONNX 转换而来
- **Plugin**:CPU/GPU/MYRIAD 等不同硬件的执行后端
- **Inference Engine API**:统一接口

**推理模式**(我项目里用的 LATENCY):

| 模式 | 适用场景 | 我的选择 |
|---|---|---|
| **LATENCY** ✅ | 单流低延迟(实时摄像头) | 工地告警必须实时,选这个 |
| THROUGHPUT | 批量处理(离线分析) | 不适用 |
| CUMULATIVE_THROUGHPUT | 多流并发 | 多摄像头场景值得评估 |

**性能数据**(我项目实测):
- YOLOv8s FP32 PyTorch CPU 推理:**~ 5 FPS**
- YOLOv8s INT8 OpenVINO CPU 推理:**~ 18 FPS**(提升 3.6 倍)

### 5.4 双保险架构(项目核心创新点)

**核心思想**:用便宜的快算法(YOLO)做粗筛,用贵的慢算法(LLM)做精审,在准确率和成本间平衡。

**架构流程**:
```
摄像头帧 ─┐
         ├─→ YOLO 推理 (50ms) ─→ 命中违规? ─┐
         │                                 │
         │                                 ▼
         │                            写入数据库
         │                                 │
         │                                 ▼
         │                            是否高危?
         │                                 │
         │                       ┌─────────┴─────────┐
         │                       │ 否                │ 是
         │                       │                   ▼
         │                       │              触发 LLM 分级
         │                       ▼              (异步线程,不阻塞)
         │                  仅记录,不推送            │
         │                                          ▼
         │                                  LLM 返回 urgency
         │                                          │
         │                                 ┌────────┴────────┐
         │                                 │ immediate/high  │ normal/low
         │                                 │                 │
         │                                 ▼                 ▼
         │                              推送钉钉            只入库
         │                                 │
         └─────────────────────────────────┴───→ SSE 推前端浮窗
```

**为什么这样设计**:
1. **解耦延迟**:YOLO 同步保证视频流不卡顿,LLM 异步保证告警质量不阻塞主链路
2. **成本可控**:LLM 调用 ¥0.01-0.02/次,只对高危走 LLM,**全开 vs 仅高危,成本差 5-10 倍**
3. **降级安全**:LLM 不可用时,系统自动 fallback 到"全推"模式,不会丢告警
4. **线程隔离**:LLM 调用在独立线程,Flask 主请求线程不阻塞

**关键代码模式(异步分级)**:
```python
def schedule(app, record_id: int):
    if not is_enabled(): return
    threading.Thread(
        target=_run, args=(app, record_id),
        daemon=True, name=f"triage-{record_id}"
    ).start()

def _run(app, record_id):
    with app.app_context():
        rec = DetectionRecord.query.get(record_id)
        result = llm.triage_alert(image_bytes, rec.cls_list)
        rec.urgency = result["urgency"]
        rec.urgency_reason = result["reason"]
        db.session.commit()
        if result["urgency"] in ("immediate", "high"):
            alert.notify(rec)
        events.publish("record_updated", rec.id)
```

### 5.5 SSE 实时通信

**SSE(Server-Sent Events)工作原理**:
1. 客户端发起 HTTP GET,带 `Accept: text/event-stream`
2. 服务器保持长连接,数据格式:`data: {json}\n\n`
3. 浏览器原生 `EventSource` API 自动接收 + 重连

**我的实现要点**:
- Token 走 query 参数(EventSource 不支持自定义 header)
- 每个连接独立 Queue,事件广播到所有在线客户端
- 心跳包(每 30s 一次)防代理超时

**示例代码**(后端):
```python
@bp_events.get("/stream")
def stream():
    def gen():
        q = events.subscribe()
        try:
            while True:
                try:
                    evt = q.get(timeout=30)
                    yield f"data: {json.dumps(evt)}\n\n"
                except Empty:
                    yield ": heartbeat\n\n"  # 心跳
        finally:
            events.unsubscribe(q)
    return Response(gen(), mimetype="text/event-stream")
```

### 5.6 JWT 鉴权

**JWT 结构**:`Header.Payload.Signature`(Base64Url 编码)
- **Header**: `{"alg":"HS256","typ":"JWT"}`
- **Payload**: `{"sub":"user_id","exp":1700000000,"role":"admin"}`
- **Signature**: `HMACSHA256(base64(header)+"."+base64(payload), SECRET_KEY)`

**为什么用 JWT 不用 Session**:
- 无状态,服务端不存:适合分布式 / 多实例
- 自带过期时间,无需额外清理

**安全要点(讲这些显得严谨)**:
1. SECRET_KEY 至少 32 字节(我项目最初只 24 字节,JWT 库会警告)
2. Access Token 短(1-2h),Refresh Token 长(7-30 天)
3. Refresh Token 应该一次性(用过即失效,防重放)
4. 敏感操作(改密、删数据)再要求二次验证
5. 不要在 JWT 里存敏感数据(任何人都能 base64 解码 payload)

---

## 六、工程难点与解决方案

> **面试金句**:每个难点都按"问题描述 → 失败的方案 → 最终方案 → 效果"四段式讲。

### 难点 1:视频检测拉流卡顿

**问题**:视频按 30fps 解码,但 YOLO 推理 50ms/帧只能 20fps,导致画面卡顿。

**失败方案**:降低视频播放帧率到 10fps —— 用户体验差。

**最终方案**:**分层渲染**
- 原视频用 `<video>` 标签原生 30fps 流畅播放
- AI 检测框用独立 `<canvas>` 叠加,10fps 异步刷新
- 两层用 CSS `z-index` 重叠,position absolute 对齐

**效果**:视频丝滑,框可能滞后 50ms 但用户感知不到。

### 难点 2:全屏模式下检测框错位

**问题**:进入全屏(F11)后,视频会有 letterbox(黑边),但检测框仍按 video 元素的尺寸渲染,出现在黑边里。

**根因**:CSS object-fit 让视频保持比例,实际显示区 ≠ 元素区。

**方案**:封装 `_getDisplayRect()` 工具函数,根据视频原始宽高比和容器宽高比计算实际显示矩形,所有框坐标按这个 rect 偏移。

### 难点 3:RTSP 拉流断流

**问题**:RTSP 网络流随时可能断(网络抖动、摄像头重启),导致 cv2.VideoCapture 卡死。

**方案**:**StreamWorker 自愈机制**
```python
while not self.stopped:
    if not self.cap or not self.cap.isOpened():
        self._reconnect()  # 指数退避:1s, 2s, 4s, 8s, max 60s
    ret, frame = self.cap.read()
    if not ret:
        self.cap.release()
        self.cap = None
        continue
    self._process(frame)
```

加上 `health.py` 30 秒无心跳则标记摄像头离线,自动 SSE 推送给前端。

### 难点 4:告警风暴

**问题**:同一违规连续 100 帧检出,会推送 100 次钉钉。

**方案**:**三层防护**
1. **检测层**:同一类别 N 秒内只入库一次(`AlertDedup` 表记录最后命中时间)
2. **推送层**:同一摄像头的推送 cooldown(默认 60s)
3. **AI 层**(可选):LLM 分级过滤,仅 `immediate/high` 推送

实测三层叠加后,推送量降到原始的 ~5%。

### 难点 5:LLM 调用延迟

**问题**:LLM 复核单次 2-5 秒,如果同步会卡死前端请求。

**方案**:
- 后端在收到检测结果时**异步触发**(线程池)
- LLM 返回后写库 + SSE 推前端
- 前端用 SSE 监听 `record_updated` 事件,自动刷新该记录

### 难点 6:数据库自动迁移

**问题**:每次加新字段(如 `urgency`),让用户手动改 DB 不现实。

**方案**:启动时检查 `PRAGMA table_info(table)`,缺哪个字段就 `ALTER TABLE ADD COLUMN`。

**取舍**:轻量,但只能加字段不能改字段。**正式项目应换 Alembic**(SQLAlchemy 官方迁移工具)。

### 难点 7:多 Tab 并发登录冲突

**问题**:同一用户开 3 个 Tab,登出一个其他还在用旧 token。

**方案**:
- 后端实现 `TokenBlocklist` 表,登出时把当前 token 的 `jti` 加入黑名单
- 每次请求验 JWT 后再查一次黑名单
- 改密时清空该用户所有 token

### 难点 8:OpenVINO 模型双加载

**问题**:终端启动时模型 loading 输出了两次,占双倍内存。

**根因**:模块导入时 detector 初始化一次,app 工厂创建时又初始化一次。

**方案**:延迟初始化(lazy),首次推理请求时才实例化 `_detector_instance`。

### 难点 9:中文路径 / GBK 编码

**问题**:Windows 中文用户名导致 `.env.example` 显示乱码;PowerShell 输出中文乱码。

**方案**:
- 所有文件强制 UTF-8 with BOM
- PowerShell 启动时 `$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()`

### 难点 10:前端构建产物嵌入 Flask

**问题**:开发是前后端分离(5173 + 5000),生产想单进程。

**方案**:
- `npm run build` 输出到 `frontend/dist`
- Flask 注册 SPA 回退路由:`@app.errorhandler(404)` 返回 `dist/index.html`
- API 路由优先匹配,SPA 兜底

---

## 七、性能数据与优化

### 关键性能指标(背下来,面试必问)

| 指标 | 数值 | 备注 |
|---|---|---|
| YOLOv8s FP32 PyTorch (CPU) | ~5 FPS | 基线 |
| YOLOv8s INT8 OpenVINO (CPU) | ~18 FPS | **3.6x 加速** |
| YOLOv8s INT8 OpenVINO (GPU) | ~60 FPS | 工地一般没 GPU |
| 单帧 YOLO 推理延迟 | 55ms | i5-12400 |
| 单次 LLM 复核延迟 | 2-5s | Qwen-VL-Plus |
| API P99 延迟 | < 200ms | 不含 LLM |
| SSE 推送延迟 | < 100ms | 本机 LAN |
| SQLite QPS | ~200 写 / ~3000 读 | 单文件锁瓶颈 |

### 性能优化做了什么

1. **算法层**:INT8 量化,3.6x 加速
2. **推理层**:OpenVINO LATENCY 模式,单流低延迟
3. **架构层**:LLM 异步,主链路不阻塞
4. **数据库层**:常查字段加索引(`created_at`, `risk_level`, `camera_id`)
5. **前端层**:路由级懒加载,首屏 JS 从 1.2MB 降到 400KB
6. **网络层**:SSE 心跳 30s,避免代理超时

### 如果要进一步优化(讲未来规划)

- 引入 Redis 缓存常查接口(摄像头列表、设置)
- 用 Celery + Redis 队列做 LLM 调用
- PostgreSQL + 读写分离
- 边缘节点(Jetson Nano)做近端推理,云端做聚合
- WebRTC 替代 RTSP 转发,降低带宽

---

## 八、工程化细节

### 8.1 错误处理

- **统一异常**:`@app.errorhandler(Exception)` 兜底,返回 `{code, msg}` 而非堆栈
- **分层捕获**:Blueprint 内捕获业务异常,中间件兜底未知异常
- **审计追踪**:所有 500 错误写 `data/logs/error.log`
- **前端拦截**:Axios 响应拦截器统一弹 ElMessage,401 跳登录

### 8.2 日志体系

- 三类日志分离:`access.log` / `error.log` / `audit.log`
- 按天轮转(`TimedRotatingFileHandler`),保留 30 天
- 关键操作(登录、改设置、删数据)写审计日志,带操作人 + IP + UA

### 8.3 配置管理

- `.env` 存敏感配置(API_KEY, SECRET),`.gitignore` 排除
- `.env.example` 占位模板,提交到 git
- `backend/config.py` 类继承(BaseConfig / DevConfig / ProdConfig)

### 8.4 安全防护

| 风险 | 防护 |
|---|---|
| SQL 注入 | SQLAlchemy ORM 全部参数化 |
| XSS | Vue 模板默认转义,接口返回 JSON 不带 HTML |
| CSRF | JWT 不依赖 Cookie,免疫 |
| 暴力破解 | 登录限频(5 次/分钟),失败 IP 锁定 |
| 弱密码 | 密码强度校验(长度 ≥ 8,含数字字母) |
| 越权访问 | RBAC 装饰器 `@admin_required` |
| 路径遍历 | `werkzeug.utils.secure_filename` |

### 8.5 测试策略

**坦诚承认局限**:
> "我做了少量集成测试和手工 e2e,没做完整单元测试覆盖。商业化前会用 pytest + pytest-flask 补齐核心 API 单测,前端用 Vitest + Playwright。"

诚实 > 撒谎。

### 8.6 部署

- 单进程 Flask + Gunicorn(生产)
- Nginx 反向代理(SSL 终结)
- 数据每日凌晨自动备份到 `data/backups/`(保留 7 天)
- 日志轮转(每天 + 保留 30 天)

---

## 九、高频面试问题与标准答案

### Q1:为什么用 Flask 不用 FastAPI?
**A**:我评估过两个。FastAPI 异步性能更好,但我项目的瓶颈是 CPU 密集的 YOLO 推理,异步带来的 IO 优化收益小。Flask 的 Blueprint 模块化和生态成熟度更适合个人快速迭代。如果是 IO 密集型(比如纯 LLM 网关),我会选 FastAPI。

### Q2:为什么 SQLite?能撑多少摄像头?
**A**:SQLite 嵌入式部署最简单,适合工地工控机环境。能撑大约 3-5 路摄像头实时写入。**超过这个规模我会换 PostgreSQL**——SQLite 是单文件锁,并发写会成瓶颈。

### Q3:YOLO 和大模型怎么协同?延迟怎么解决的?
**A**:YOLO 同步执行保证视频流不卡;LLM 异步触发(独立线程 + 数据库回写 + SSE 推前端)。这样既享受 LLM 的语义能力,又不影响主链路延迟。如果 LLM 服务不可用,系统自动降级到"全推"模式,功能不丢失。

### Q4:INT8 量化原理?怎么做的?会掉点吗?
**A**:INT8 量化是把 FP32 权重和激活映射到 8-bit 整数,模型小 4 倍,推理快 2-5 倍。我用的是 PTQ(训练后量化),通过 NNCF 工具,准备 100-500 张校准集,统计激活分布,计算 scale 和 zero_point,然后量化权重。我的实测 mAP 掉了约 1 个点,从 0.82 到 0.81,可接受。如果想零掉点,用 QAT 重训,但成本高 10 倍。

### Q5:OpenVINO 比 PyTorch CPU 快多少?为什么?
**A**:实测 3.6 倍。原因有三:**算子融合**(Conv + BN + ReLU 融合成一个 op)、**INT8 量化**(SIMD 一次处理 4 个数)、**Intel CPU 指令集深度优化**(AVX-512 VNNI)。

### Q6:SSE 和 WebSocket 怎么选?
**A**:告警是单向场景(服务器→客户端),SSE 完全够用,实现简单,基于 HTTP 穿墙好,浏览器原生自动重连。WebSocket 是双向,握手复杂,要单独处理鉴权和心跳。**杀鸡用牛刀没必要**。

### Q7:JWT 用了什么算法?怎么防重放?
**A**:HS256(HMAC-SHA256),对称密钥。防重放主要靠两点:exp 短时效(2 小时)+ jti(JWT ID)写黑名单。改密码或登出时,把该用户所有 token 的 jti 拉黑。

### Q8:告警风暴怎么处理?
**A**:三层防护——检测层同类型 N 秒去重 + 推送层冷却(默认 60s)+ AI 分级(只推 immediate/high)。实测推送量降到原始 ~5%。

### Q9:摄像头掉线怎么发现?
**A**:每个 StreamWorker 维护最后成功取帧时间,HealthWatcher 每 5 秒巡检,30 秒无更新标记离线,触发 SSE 推送和摄像头列表状态变更。恢复同理,首次成功取帧推 `camera_online` 事件。

### Q10:如果给你扩展到 100 路摄像头怎么办?
**A**:三个改造:
1. **算力**:GPU 或多机分布式,单个 StreamWorker 跑一路
2. **架构**:Celery + Redis 队列,推理 worker 独立水平扩展
3. **数据库**:PostgreSQL + Redis 缓存 + 读写分离
4. **存储**:截图视频片段走对象存储(MinIO/OSS)

### Q11:模型怎么训练的?数据集多大?
**A**:用 Ultralytics YOLOv8s,在我标注的 5000 张工地图片上训练 100 epochs,数据增强用 Mosaic + MixUp。imgsz 640,Adam 优化器,初始 lr 0.01,cosine 衰减。最终 mAP@0.5 约 0.82。然后用 NNCF 做 INT8 量化导出 OpenVINO。

### Q12:CIoU 和 IoU 的区别?DFL 是什么?
**A**:
- **IoU**:交并比,只看重合度,框完全不重合时梯度为 0,优化困难
- **CIoU**:加了中心点距离 + 长宽比惩罚,解决 IoU 优化死区,收敛快
- **DFL**:Distribution Focal Loss,把框坐标建模为离散分布而非单点,通过期望值出连续坐标,定位精度提升

### Q13:LLM 怎么集成的?成本怎么控?
**A**:用 OpenAI 兼容协议接通义千问 Qwen-VL-Plus(视觉)和 qwen-plus(文本)。控成本三招:
1. 只对**高危**告警走 LLM,不是全量
2. 用 Setting 开关,管理员可随时关
3. 图片走 Base64,缩到 720p 再传,降低输入 token 数

### Q14:前端怎么做权限控制的?
**A**:三层:
1. **路由级**:Vue Router beforeEach 守卫,无 token 跳登录
2. **菜单级**:根据 `auth.role` 渲染不同 menu
3. **按钮级**:`v-if="auth.isAdmin"` 控制敏感按钮显示
4. **接口级**:后端 `@admin_required` 装饰器才是最终防线,前端控制只是 UX

### Q15:你这个项目最大的局限是什么?
**A**:**3 个诚实的局限**:
1. **数据集和真实工地有 gap**:训练数据多来自公开 + 合成,真实工地光照/视角/遮挡会让准确率下降
2. **SQLite 撑不住生产规模**:超过 3-5 路实时摄像头就需要换 PG
3. **没有摄像头厂商 SDK 适配**:只支持通用 RTSP,真实工地多是海康/大华专有协议

**接下来如果商业化,我会按这个优先级解决**。

### Q16:你怎么看 AI 替代传统 CV?
**A**:不是替代,是分层。**传统 CV(模板匹配、Haar、HOG)在低算力嵌入式上仍有价值**;YOLO 等深度学习适合通用目标;大模型适合语义理解和长尾。**好的工程师是根据场景选工具,不是all in 一个方向**。

### Q17:你有没有读过 YOLO 的论文?
**A**:读过 v1、v3、v4、v8 的相关文献(v5/v8 没有正式论文)。v1 把检测做成回归问题是开山;v3 引入 FPN 多尺度;v4 大量 Bag of Freebies/Specials;v8 是 anchor-free + 解耦头 + DFL。**重点关注 v3 的多尺度和 v8 的 anchor-free 思路**。

### Q18:Flask 应用工厂模式好处?
**A**:三个:
1. 解决循环引用(extensions.py 集中初始化)
2. 测试友好(不同配置传不同 Config 类)
3. 多实例可能(一个进程跑多 app,不常用但留有空间)

### Q19:为什么用 Pinia 不用 Vuex?
**A**:Pinia 是 Vue 3 官方推荐,API 更扁平(没有 mutation 概念),TypeScript 支持好,Composition API 心智一致。Vuex 4 仍能用,但社区已经在 sunset。

### Q20:你会怎么改进这个项目?
**A**:**短期(1 个月)**:换 PostgreSQL + Alembic、加 Sentry 监控、单元测试覆盖率到 70%。
**中期(3 个月)**:多租户改造、海康 SDK 适配、Celery 异步任务化。
**长期(6 个月)**:边缘推理(Jetson)+ 云端聚合、移动端 H5、对接 BIM。

---

## 十、反问面试官的高质量问题

> 面试结尾"你有什么想问我的"——**不反问 = 不感兴趣 / 不严谨**。准备 3-5 个。

### 技术深度类(显示你认真思考过岗位)
1. "团队当前最棘手的技术挑战是什么?是模型精度、推理性能还是工程架构?"
2. "你们模型迭代节奏是什么?有数据回流闭环吗?"
3. "团队的代码评审文化怎么样?有 RFC 制度吗?"

### 业务理解类(显示你关心产品)
4. "我们的主要客户是 B 端工厂还是 G 端政府?客单价范围?"
5. "下一个季度产品规划的重点方向是什么?"

### 团队成长类(显示你看长期)
6. "新人前 3 个月一般会被分到什么类型的任务?"
7. "我入职后,我的直属导师是谁?他/她的技术背景是?"
8. "团队对外的技术分享和论文产出鼓励吗?"

### 现实问题(收尾轻松)
9. "团队规模、加班节奏、出差比例大概是怎样的?"(委婉问加班)
10. "公司技术债主要在哪些地方?"(高级问题,展示你成熟)

---

## 📌 临场技巧

### 讲项目时的节奏
1. **先讲背景 + 价值**(30 秒)→ 给面试官 context
2. **再讲架构 + 选型**(60 秒)→ 显示工程思维
3. **重点讲 1-2 个难点**(60 秒)→ 显示深度
4. **被问到再展开**(看面试官兴趣点)

### 不要犯的错
- ❌ 一上来就讲代码细节,面试官没 context
- ❌ "我用了 XX",但说不出"为什么"
- ❌ 吹得过头(你说 "我精通分布式",对方追问立刻穿帮)
- ❌ 对项目局限避而不谈(诚实 > 包装)

### 推荐的口头禅
- "我评估过 A 和 B,最后选 A,是因为..."
- "这里我做了取舍,优势是 X,代价是 Y"
- "如果让我重做,我会改成..."
- "我承认这里有局限,具体是..."

### 紧张时的应对
- 不会的问题:**"这一块我没深入研究过,但凭直觉应该是 XXX,正确答案是?"**——把不会变成请教
- 答错了:**"等等,我刚才说错了一个细节,正确的是..."**——立即纠正比硬撑强

---

## 📚 最后:面试前一周的复习节奏

| 天数 | 内容 |
|---|---|
| D-7 | 通读本文档,标记不熟的地方 |
| D-6 ~ D-5 | 重点啃第五章(算法原理),YOLO/INT8/OpenVINO 要能默写 |
| D-4 | 模拟讲 30/60/180 秒版本介绍,录音回放 |
| D-3 | 第九章 20 题,每题写自己的答案,然后对照 |
| D-2 | 第六章难点,每个用 STAR 法(背景-任务-行动-结果)讲一遍 |
| D-1 | 跑一遍项目 demo,熟悉演示路径;准备反问 |
| D-day | 早睡,中午别吃太饱,提前 15 分钟到 |

---

**祝你 offer 大丰收 🎉**

(本文档持续更新中,遇到面试问题被卡住,记下来回来补充。)

---

## 十一、演示视频操作步骤(逐键说明)

> **这章是手把手指引**,告诉你录视频时**每一步点哪里、说什么**。把这章打印贴在显示器旁照着做。
> 另有详细版本见 `docs/DEMO_SCRIPT.md`,此处是精简版+操作细节。

### 录制前准备(30 分钟)

1. **环境检查**
   - 浏览器:Edge 或 Chrome **隐身窗口**(避免被你日常浏览的标签和扩展干扰)
   - 分辨率:**1920×1080**(右键桌面 → 显示设置 → 1920×1080)
   - 浏览器全屏:**F11** 进入,演示时一直全屏

2. **后端启动**
   ```powershell
   cd D:\Python\PyCharm\PythonProject\工地安防Web项目
   D:/Python/Python/python.exe run.py
   ```
   等到看到 `* Running on http://0.0.0.0:5000` 出现

3. **前端启动**(开发模式,热更新方便临时改)
   ```powershell
   cd frontend
   npm run dev
   ```
   或者用构建好的版本(更稳):`npm run build` 后访问 `localhost:5000`

4. **预填测试数据**(让驾驶舱有内容)
   - 登录 admin/admin123
   - 用图片检测页跑 5-10 张测试图,生成历史记录
   - 在摄像头管理添加 2-3 个 RTSP(可以填假的 `rtsp://test.example.com/stream` 用于展示)

5. **准备素材**(放桌面方便拖拽)
   - `test-image.jpg`:一张含未戴安全帽工人的工地图(网上搜"工地 未戴安全帽")
   - `test-video.mp4`:10-15 秒工地视频片段
   - 桌面隐藏其他文件(右键 → 查看 → 取消勾选"显示桌面图标",或暂时把图标移到一个文件夹)

6. **OBS Studio 配置**
   - 下载:https://obsproject.com/
   - 添加来源:**显示器采集**(整屏)或 **窗口采集**(只录浏览器窗口)
   - 录制设置:1920×1080 / 60fps / mp4 / 比特率 8000-10000kbps
   - 麦克风音量:开始录前在 OBS 看到音柱跳动到 -12dB ~ -6dB 区间
   - **快捷键**:F9 开始/停止录制(避免鼠标移到 OBS 上)

### 录制流程(180 秒,严格按节拍)

#### 【00:00-00:10】片头登录

**操作**:
1. 浏览器停在登录页(`http://localhost:5000` 或 `/login`)
2. 鼠标移到用户名框,**输入** `admin`(慢一点,让观众看清)
3. **输入** `admin123`
4. 点"登录"
5. 跳转到驾驶舱

**说什么(同时配音)**:
> "这是一个基于 YOLO 和大语言模型的工地安全监管系统,9000 多行代码,单人独立开发。"

#### 【00:10-00:30】驾驶舱总览

**操作**:
1. 在驾驶舱页面停留
2. 鼠标**缓慢从左滑到右**,扫过:
   - 实时态势卡片(顶部)
   - 安全分数(大数字,动画跳动)
   - 24 小时告警热力图(中部)
   - 摄像头健康列表(右侧或底部)
3. 在热力图区域**鼠标悬停某个时段**,显示 tooltip "12:00 5 条告警"

**说什么**:
> "首页是数据驾驶舱,综合呈现实时态势、安全分数、24 小时告警热力图,以及所有接入摄像头的健康状态——实时心跳,离线 30 秒自动告警。"

#### 【00:30-00:55】图片检测 + LLM 复核

**操作**:
1. 左侧菜单点"检测中心" → "图片检测"
2. **从桌面拖拽** `test-image.jpg` 到上传区
3. 等待约 0.5 秒,YOLO 框出 2-3 个目标(显示"未戴安全帽" 等标签)
4. 点击"AI 二次复核"按钮(或叫"LLM 复核"、"智能分析")
5. 等 2-3 秒,右侧出现 LLM 输出的整改建议(打字机效果会自动出现)
6. **鼠标滚动一下**让观众看清完整输出

**说什么**:
> "核心是 YOLO 加大模型的双保险:YOLO 快速定位违规——比如未戴安全帽——然后视觉大模型复核场景,给出文字化的整改建议。这一步过滤了大量误报。"

#### 【00:55-01:20】视频检测

**操作**:
1. 左侧菜单 → "视频检测"
2. 点"选择视频",选 `test-video.mp4`
3. 视频开始播放,canvas 浮层叠加检测框(框跟着视频内容动)
4. 当出现高危违规(预先选有未戴安全帽的视频),右上角弹出告警通知 + 蜂鸣声
5. **特意点一下"暂停"再"继续"**,展示控制按钮
6. 不必看完整个视频,15 秒后切下一段

**说什么**:
> "视频检测采用分层渲染——原视频 30fps 流畅播放,AI 检测框独立 10fps 叠加,既不卡顿又能看清告警。命中高危违规自动入库、自动推送。"

**提示**:如果蜂鸣太响,提前去"系统设置 → 告警声音"调音量。

#### 【01:20-01:45】RTSP 摄像头 + 电子围栏

**操作**:
1. 左侧菜单 → "摄像头管理"
2. 列表显示已添加的摄像头(显示在线/离线状态)
3. 点其中一台摄像头,进入"电子围栏配置"或"区域设置"
4. 在画面上**鼠标依次点 4 个角**,画一个多边形(覆盖你要监控的区域)
5. 点"保存围栏"
6. 弹出提示"围栏已启用"

**说什么**:
> "支持 RTSP 网络摄像头,可配置电子围栏——只在指定区域检测,减少干扰画面;同时支持每类违规独立调整置信度阈值。"

**提示**:如果没有真实 RTSP,可以预先填假地址展示界面;围栏画完不需要真的检测,只演示功能。

#### 【01:45-02:05】告警记录 + AI 智能分级

**操作**:
1. 左侧菜单 → "告警记录"
2. 表格里能看到"风险 / AI 紧急度"列,有 `高危` `立即处置` `紧急` 标签
3. **鼠标悬停**某条"立即处置"标签,显示 tooltip "因高空作业未挂安全带,可能立即造成坠落伤亡"
4. **点击一条记录**,详情对话框弹出
5. 对话框里展示:截图 + 视频片段(自动播放) + AI 紧急度标签 + 理由文字

**说什么**:
> "每条高危告警都会被视觉大模型再次评估,判断真实紧急度。只有立即处置和紧急级别才会推送钉钉企微,避免管理员被刷屏。"

**提示**:这一步要求**之前必须开启过 AI 告警分级**(系统设置里),否则记录里没有 urgency 数据。提前在录制前一天开启并跑几条记录积累数据。

#### 【02:05-02:30】AI 智能日报

**操作**:
1. 左侧菜单 → "报表导出"
2. 顶部 4 个统计卡片(检测总数 / 高危 / 未处理 / 已处理)
3. **向下滚动**到"AI 智能日报"卡片
4. 切换右上角周期到"近 7 天"
5. 点"生成报告"按钮
6. 等 3-5 秒,卡片展开:
   - **总览**段
   - **关键发现**列表(3 条)
   - **执行建议**列表(带 → 箭头,3 条)
   - **下阶段重点**段
7. **滚动展示**完整内容,停在最后一条建议上 1 秒

**说什么**:
> "传统报表只能给数字,这里直接由大模型生成可读、可执行的安全日报——总览、关键发现、执行建议、下阶段重点。每天早上 8 点自动推给项目经理。"

**提示**:LLM 生成需要 3-5 秒,**别剪掉这段等待时间**,反而能体现"是真实调用,不是 hard code"。

#### 【02:30-02:50】系统设置全景扫描

**操作**:每个 Tab 停留 2-3 秒,**鼠标快速点击切换**:
1. 左侧菜单 → "系统设置"
2. 点 "报警推送" Tab → 停 2 秒,鼠标扫过 Webhook 输入框
3. 点 "品牌定制" Tab → 停 2 秒,**鼠标悬停 Logo 上传区**
4. 点 "检测灵敏度" Tab → 停 2 秒,**拖动一个滑块**(展示交互)
5. 点 "告警声音" Tab → 停 2 秒
6. 点 "AI 告警分级" Tab → 停 3 秒(**这是新功能,多停 1 秒**)
7. 点 "数据保留" Tab → 停 2 秒
8. 点 "健康指标" Tab → 停 3 秒(展示磁盘/内存/进程状态)

**说什么**:
> "白标定制、灵敏度调节、数据保留策略、健康监控——商业项目所有该有的运营能力都在这里。"

#### 【02:50-03:00】收尾

**操作**:
1. 切到一个准备好的页面,显示:
   - 项目统计(9322 行 / 13 页面 / 64 路由)
   - GitHub 链接 + 二维码
2. 可选:打开终端,跑一下 `git log --oneline | wc -l`(显示 commit 数)

**说什么**:
> "全栈一人开发,从前端组件到后端架构,从模型训练到大模型集成。代码开源在 GitHub,链接放在描述里,欢迎 Star 支持。"

#### 录完检查

- **F9 停止录制**
- 用 VLC 或电脑自带播放器**完整回放一遍**
- 检查:
  - [ ] 没有杂音(空调、键盘声)
  - [ ] 没有露出敏感信息(API Key、个人微信、聊天弹窗)
  - [ ] 没有误操作(点错按钮、操作失败弹错)
  - [ ] 没有黑屏 / 卡顿

如有问题,只重录那一段,后期拼接即可,**不必整段重来**。

### 后期处理(剪映/CapCut)

1. **导入素材**:原始视频 + 旁白录音(如果分开录)
2. **剪辑**:删除停顿、卡顿、误操作
3. **添加字幕**:
   - 用剪映的"识别字幕"自动生成
   - 手动核对错字
   - 字体选**思源黑体** + **白色 + 黑色描边**(任何背景都清晰)
4. **添加背景音乐**:
   - 选轻量电子乐(剪映音乐库免费)
   - 音量调到 **-25dB**(确保不压过旁白)
5. **添加片头/片尾卡**(可选,加专业感):
   - 片头:项目 Logo + 标题(3 秒)
   - 片尾:GitHub + B 站二维码(3 秒)
6. **导出**:1080p / 60fps / mp4

### 视频发布

- **B 站**(主):标题 "工地安防 · 全栈 AI 系统演示 | YOLO + LLM 双保险架构"
- **YouTube**(给海外面试):标题 "Full-Stack AI Construction Safety System | YOLO + LLM Dual-Insurance Architecture"
- **README 顶部**:嵌入封面图链接到 B 站
- **简历**:放短链(用 短链.cn 或 dub.co 生成)+ 二维码

### 演示视频后的延伸用法

视频不只是给 HR 看,你可以:
- **面试自我介绍后主动说**:"如果方便我有个 3 分钟项目演示视频,要不要看一下?"——80% 面试官会点头,**省下你描述细节的 5 分钟**,直接 demo
- **简历下方加二维码**,扫码看视频
- **GitHub Pull Request 自己提一些 issue**,在 issue 里嵌视频片段,让仓库"活着"

---

## 📦 文档转 Word 教程

本文档是 Markdown 格式(`.md`),要转 Word(`.docx`):

### 方法 1:Word 直接打开(推荐,最简单)

1. 把文件后缀**改为 `.docx`** 之前,先打开 Word
2. 文件 → 打开 → 选择类型"**所有文件**"
3. 选 `INTERVIEW_PREP.md`,Word 会自动渲染 Markdown
4. 另存为 `.docx`

(Word 2019/365 原生支持 Markdown 导入。)

### 方法 2:在线转换(0 软件安装)

1. 打开 https://word2md.com/(反向)或 https://cloudconvert.com/md-to-docx
2. 上传 `INTERVIEW_PREP.md`
3. 下载转好的 `.docx`

### 方法 3:VS Code 插件

1. 安装 "Markdown PDF" 或 "Pandoc" 插件
2. 右键 md 文件 → Export
3. 选 docx

### 方法 4:直接打印成 PDF

如果纯阅读,我推荐转 PDF 而非 Word:
- 用 Typora / Obsidian 打开 md → Ctrl+P → 另存为 PDF
- 格式更稳定,不会乱码

---

> ✍️ **最后一句**:这份文档不是"背完就完事",而是**你的知识仓库**。
> 面试遇到不会的,回来补充;新学的知识,加进字典。3 个月后,这就是你最厚实的简历附件。
