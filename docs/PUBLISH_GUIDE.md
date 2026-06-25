# GitHub 发布指南

## 一、本地仓库初始化

在项目根目录(`工地安防Web项目`)打开 PowerShell:

```powershell
# 1. 初始化 git
git init
git branch -M main

# 2. 检查会被提交的文件(应只包含源码,不含 model/ data/ frontend/dist 等)
git status

# 3. 首次提交
git add .
git commit -m "feat: 工地安防系统 v1.0 — YOLO + LLM 全栈实现"
```

> **如果 `git status` 里看到了 `model/` 或 `data/` 里的大文件**,说明 `.gitignore` 没生效——确认仓库根目录确实有 `.gitignore` 文件,然后 `git rm -r --cached model data` 后再次提交。

## 二、在 GitHub 创建仓库

1. 浏览器打开 https://github.com/new
2. **Repository name**: `construction-safety-web`(或你喜欢的名字)
3. **Description**: `🏗️ YOLO + LLM 双保险工地安全监管系统 · Vue 3 + Flask 全栈 · 9000+ 行单人项目`
4. **Public**(简历项目必须公开)
5. **不要**勾选 "Initialize this repository with README"
6. 点 "Create repository"

## 三、推送到远程

```powershell
# 替换 YOUR_USERNAME 为你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/construction-safety-web.git
git push -u origin main
```

如果提示要登录:GitHub 不再支持密码,需要用 **Personal Access Token**:
1. https://github.com/settings/tokens → Generate new token (classic)
2. 勾选 `repo` 权限
3. 复制 token,push 时用作密码

## 四、仓库优化(让访客眼前一亮)

### 1. 仓库主页 About 配置

进入仓库 → 右侧齿轮(About):
- **Description**: 与上面一致
- **Website**: 演示视频 B 站链接
- **Topics**(标签,会影响搜索):
  - `yolo` `llm` `vue3` `flask` `fullstack`
  - `computer-vision` `safety-detection`
  - `element-plus` `openvino` `qwen`

### 2. 添加演示截图到 README

录完演示视频后,截图 3-5 张关键画面放到 `docs/screenshots/`,然后编辑 README,在"功能矩阵"下方加一段:

```markdown
## 📸 系统截图

### 实时驾驶舱
![Cockpit](docs/screenshots/cockpit.png)

### 图片检测 + LLM 二次复核
![Image Detect](docs/screenshots/image-detect.png)

### AI 智能日报
![AI Report](docs/screenshots/ai-report.png)

### 系统设置
![Settings](docs/screenshots/settings.png)
```

### 3. 嵌入演示视频

B 站视频的封面 + 链接放 README 最顶部:

```markdown
[![Demo Video](docs/screenshots/cover.png)](https://www.bilibili.com/video/BVxxxxxxxx)
```

### 4. Star 引导

README 末尾已经有"欢迎 Star 支持",可以再补一行:

```markdown
**觉得有用?给我一个 ⭐ Star 让更多人看到!**
```

## 五、模型文件分发(不入 git)

模型 `.pt` 和 `best_openvino_model/` 体积大(几十 MB ~ 几百 MB),**不要塞进 git**:

**推荐**:GitHub Releases 上传

1. 仓库主页 → Releases → "Create a new release"
2. Tag: `v1.0`,Title: `v1.0 — 首发版本`
3. Description: 简单写下版本特性
4. **拖拽上传** `best.pt` 和 `best_openvino_model.zip`
5. Publish release

然后在 README 的"模型文件"章节加一行:

```markdown
> 📥 下载预训练模型:[Releases 页面](https://github.com/YOUR_USERNAME/construction-safety-web/releases/latest)
```

## 六、简历怎么写这个项目

```
工地安防 · 智能违规检测系统  |  个人独立项目  |  2025.10 - 2026.06
GitHub: github.com/YOUR_USERNAME/construction-safety-web  ⭐ N
Demo: bilibili.com/video/BVxxxxxxxx

技术栈: Vue 3 + Flask + YOLOv8 + OpenVINO + Qwen-VL + SQLAlchemy + Element Plus

• 单人独立完成 9000+ 行代码全栈项目,13 个功能页面,64 条 API 路由
• 设计 YOLO + 视觉大模型「双保险」检测架构,YOLO 快速定位 + LLM 复核降误报
• 实现 SSE 实时告警推送、电子围栏、安全分数、告警热力图等商业化功能
• 集成 OpenVINO INT8 量化,CPU 单路 RTSP 推理达 15+ FPS
• 设计 AI 智能日报和告警智能分级,LLM 自动生成可执行报告 + 过滤无效推送
• 完成企业级基建:JWT 鉴权、RBAC、操作审计、数据保留、备份、日志轮转
```

## 七、面试时怎么讲

**60 秒电梯版**(自我介绍后被问"讲一下你的项目"):

> "我做了一个工地安防系统,核心特色是用 YOLO 加大模型的双保险架构——YOLO 第一道筛快速定位违规,视觉大模型第二道审做语义复核,显著降低了纯 YOLO 的误报率。9000 多行代码全栈单人完成,Vue 3 加 Flask,包含从图片视频 RTSP 三种检测、实时 SSE 告警、电子围栏、AI 智能日报到白标定制等商业级功能。技术细节上,我做了 OpenVINO INT8 量化让 CPU 单路达到 15FPS,也独立实现了一套异步告警分级系统,只有大模型判定为'立即处置'的高危才推送钉钉,过滤了大量无效干扰。"

**面试官常问的 3 个追问**:

1. **"YOLO 和 LLM 怎么协同的?延迟怎么解决的?"**
   答:YOLO 同步执行,LLM 异步触发(线程池 + 数据库回写 + SSE 推前端),避免阻塞主检测链路。

2. **"为什么用 OpenVINO 不用 TensorRT?"**
   答:目标客户是工地,大部分只有 CPU 工控机,OpenVINO 在 Intel CPU 上比 ONNX Runtime 快 3-5 倍,部署成本低。

3. **"告警风暴怎么处理?"**
   答:三层防护——同类告警 N 秒冷却 + 推送 webhook 冷却 + AI 分级过滤,实测可降低推送量 70% 以上。

## 八、后续维护节奏(可选)

公开后建议每月小迭代,让 commit 历史"活着":
- 修 bug 即时提交
- 每月一个小功能(响应 Issue)
- README 顶部加 "Last updated: 2026-XX"

招聘 HR 会看仓库的 commit 活跃度。

---

**完成上述步骤后,这个项目对你的求职价值就完整释放了。** 下一步把精力转到智慧社区项目和具身智能学习上。
