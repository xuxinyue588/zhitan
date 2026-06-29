# 职探 Risk Agent · 免费云部署方案设计书(doc)

> 功能代号:`deploy-to-cloud-free`
> 适用范围:让目前仅本机运行的「职探风险侦察 Agent」(FastAPI + Vite React 全栈)能够通过互联网被外部访问,同时严守 DeepSeek / Exa 两枚 API Key 不外泄。

---

## 1. 需求理解

用户的两个核心诉求:
1. **要免费的**:不能产生持续订阅费用;
2. **帮我上线**:希望尽量减少手工摸索,由 AI 把可以自动化的工程准备全部做完,留下少量必须在网页点击的操作交还给人来完成(因为涉及 GitHub 授权、PaaS 控制台登录这些无法代劳的动作)。
3. **隐含的安全要求**(承接上一轮对话):保护好两枚 API Key,不让别人拿到线上 URL 就能把你的模型额度刷爆。

由此推出三个不可妥协的目标 G1/G2/G3:

| 编号 | 目标 | 衡量标准 |
|------|------|----------|
| G1 | 应用可通过 HTTPS 公网访问 | 打开 `<xxx>.onrender.com` 返回健康检查 JSON;打开 `<yyy>.vercel.app` 渲染页面并能成功发起一次风险侦察 |
| G2 | API Key 全程只在服务器侧出现 | 前端 dist 构建产物 grep 不到 `sk-...`;Git 历史 grep 不到这两枚 key;`.env` 不入仓 |
| G3 | 别人即便知道后端 URL 也难以滥用 | CORS 白名单限制到自己的前端域名;引入基于 IP 的简单限流 |

---

## 2. 技术选型(为什么是这套)

候选方案横向比较(均声称"free"):

| 方案 | 后端载体 | 前端载体 | 真·长期免费? | 结论 |
|------|----------|----------|--------------|------|
| A | **Render Web Service Free** | **Vercel Hobby** | ✅ 月度实例小时数充足 | **采用** |
| B | Railway Trial Plan | Vercel | ❌ $5 trial credit 用完就要绑卡 | 否决 |
| C | Fly.io Free Allowance | Netlify | ⚠️ 政策多次变动且要求信用卡验证 | 否决 |
| D | Cloudflare Workers(Python beta)+Pages | CF Pages | ⚠️ FastAPI ASGI 生态适配不全 | 否决 |

**最终架构**

```
┌───────────────────────────────────────────────────────────────┐
│ 终端浏览器                                                    │
│   ↓ https://职探.vercel.app                                   │
│ Vercel Edge CDN(静态 HTML/CSS/JS,全球加速,无密钥)            │
│   ↓ fetch(`${VITE_API_BASE}/api/companies`, ...)             │
│ Render Web Service(FastAPI @ uvicorn on port $PORT)          │
│   │ env 注入:DEEPSEEK_API_KEY / EXA_API_KEY / ALLOWED_ORIGINS │
│   ├──► DeepSeek Chat Completions                              │
│   └──► Exa Search                                             │
└───────────────────────────────────────────────────────────────┘
```

要点:
- API Key 由 Render 控制台 Environment 页签手动录入,**绝不进入 Git 仓库**;
- 前端打包产物只会嵌入「后端公网 URL」,这是公开信息不算秘密;
- 由于代理转发发生在服务端,浏览器的 DevTools Network 面板看不到原始 LLM 供应商返回头里的计费标识之外的任何东西(Key 本身永不下行)。

已知约束(Render Free):
- 单个 web service 连续 ≥15 分钟无流量会被挂起,下一次冷启动耗时约 30–60 s。这一点会在前端加载态文案里如实告知用户,不影响功能完整性。

---

## 3. 影响范围(文件级变更矩阵)

### 3.1 新增文件

| 路径 | 类型 | 用途 |
|------|------|------|
| `zhitan-risk-agent/backend/runtime.txt` | 文本 | Pin Python 解释器版本,Render 据此安装运行时 |
| `zhitan-risk-agent/backend/render.yaml` | Blueprint IaC | 让 Render 一键导入服务定义,免去逐项表单填写 |
| `zhitan-risk-agent/backend/ratelimit.py` | Python 模块 | 基于 `cachetools.TTLCache` 的进程内 IP 计数器中间件 |
| `zhitan-risk-agent/frontend/vercel.json` | SPA routing config | History mode 下刷新子路由不再 404 |
| `zhitan-risk-agent/frontend/.env.production` | 构建参数 | 仅存放 `VITE_API_BASE=https://<backend>.onrender.com`,非机密 |
| `DEPLOY_GUIDE.md`(位于仓库根) | 操作手册 | 你照着点点鼠标就能完成的图文分步指引 |

### 3.2 修改文件

#### `zhitan-risk-agent/backend/main.py`
当前 main.py:13-19 将 `allow_origins=["*"]` 作为开放策略,违反 G3。改造方向:
```python
# 解析环境变量中的逗号分隔来源名单
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if o.strip()
] or ["http://localhost:5173"]  # 开发兜底

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["Content-Type"],
)
```
并在 app 创建之后挂载 ratelimit 中间件:
```python
from ratelimit import RateLimitMiddleware
app.add_middleware(
    RateLimitMiddleware,
    max_requests=20,
    window_seconds=600,
)
```
其余三个 endpoint (`/`、`/api/companies`、`/api/query`) 业务逻辑零修改。

#### `zhitan-risk-agent/backend/requirements.txt`
追加 `cachetools>=5.3,<7` 用于限流的 TTL 存储。其它依赖维持不变。

#### `zhitan-risk-agent/frontend/src/api/client.ts`
第 3 行已经具备 `import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'`,**不需要改代码本身**;只要保证构建阶段存在 `.env.production` 即可。同时为了让冷启动期间用户体验更好,在该文件的 queryRisk 出错分支追加一条友好提示,告知可能是后端正从睡眠中恢复。

#### 顶层 `.gitignore`
现仅有 `*.env`。补齐常用条目防止误推:
```
.env
*.env
__pycache__/
*.py[cod]
node_modules/
dist/
.DS_Store
```

### 3.3 不动的文件
- `agents/pipeline.py` 及下游 agents/scoring/services 各模块:纯业务逻辑,不在此次范围内触碰,降低回归面;
- `data/sample_companies.py`:静态样例数据无变化。

---

## 4. 详细实现细节

### 4.1 限流中间件(ratelimit.py)

选用进程内 `TTLCache` 而不是 Redis:
- 免费层级单实例足够,水平扩展之前不必引外部状态存储;
- 实现 ≤40 行,易读易审计。

伪码骨架:
```python
from collections import defaultdict
from cachetools import TTLCache
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests=20, window_seconds=600):
        super().__init__(app)
        self.max_requests = max_requests
        self.bucket: TTLCache[str,int] = TTLCache(maxsize=10000,
                                                  ttl=window_seconds)

    async def dispatch(self, request:Request, call_next):
        if request.url.path in ("/", "/health"):
            return await call_next(request)        # 健康/探活不限速
        ip = request.client.host if request.client else "unknown"
        n = self.bucket.get(ip, 0) + 1
        self.bucket[ip] = n
        if n > self.max_requests:
            return JSONResponse(status_code=429,
                                content={"detail":"请求过于频繁,请稍后再试"})
        return await call_next(request)
```
阈值依据:DeepSeek 平均一次完整 pipeline ≈ 数千 tokens,假设每次消耗 ¥0.05,20 次/10 分钟封顶日耗可控;同时正常人类交互远低于此频率,体感无影响。

### 4.2 render.yaml(Blueprint)

```yaml
services:
  - type: web
    name: zhitan-risk-api
    runtime: python
    rootDirectory: zhitan-risk-agent/backend
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: DEEPSEEK_API_KEY
        sync: false      # 手工在 Dashboard 录入,不入 yaml 明文
      - key: EXA_API_KEY
        sync: false
      - key: ALLOWED_ORIGINS
        # 待前端域名确定后填入,例如 https://zhitan.vercel.app
        sync: false
```
关键安全属性:`sync:false` 表示此变量仅在控制台可见,yaml 即使进了公开仓库也不会泄露 secret。

### 4.3 frontend/vercel.json
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

### 4.4 frontend/.env.production
```
VITE_API_BASE=__REPLACE_WITH_RENDER_URL__
```
⚠️ 占位符待后端 Deploy 成功后替换成真实 URL 再重新触发一次 Vercel 构建。这条占位符不含任何机密,即使提前入库也无害。

---

## 5. 边界条件与异常处置一览

| 场景 | 表现 | 处置方式 |
|------|------|----------|
| 有人 curl 直击 `/api/query` 但 Origin 不在白名单 | CORS preflight 失败 | 浏览器自带拦截;curl 因不带 Origin 会绕过 CORS,故再叠加 IP 限流作第二防线 |
| 同一 NAT 多人共享出口 IP(公司网络) | 可能集体触发 429 | 阈值取保守偏松(20/10min);必要时升级 plan 或换 keyed-by-userId 方案 |
| 后端冷启动期间前端报错 | 显示"风险侦察失败…" | client.ts 异常文案改为提示稍候重试,Vercel 端不受影响仍展示静态页 |
| 误把 .env push 到远程 | Key 进入公共视野 | 本次实施第一步即在 `.gitignore` 强化规则;并在指南末尾附轮换 key 步骤 |
| Exa 国内可达性波动 | 个别查询超时 | 维持现状(httpx 默认 timeout=5s 太短的话留待下一迭代单独优化,本期不开新口子) |

---

## 6. 数据流总览(G2 合规性证明)

构造产物中是否会泄露 Key?
- 前端构建产物只有 JS bundle,bundle 内出现的常量为 `VITE_API_BASE=<public url>`;
- 后端容器镜像虽包含 requirements,但不携带 `.env`(由 Build 过程跳过);
- 远程 Git 仓库:强化后的 `.gitignore` 保证 `.env` 永不上传;

结论:**G2 成立**。

---

## 7. 验收准则(Done Definition)

部署完成后应满足下列全部断言:
1. `GET https://<backend>.onrender.com/` 返回 `{"status":"ok"...}`;
2. 从其他网站 origin 调上述 host 的 `/api/companies` 被 CORS 拒绝(响应缺 Access-Control-Allow-Origin);
3. 从你自己 Vercel 域名的同一路径调用返回 200 且 body 为样例公司数组;
4. 快速连续 POST `/api/query` 达到 21 次后收到 HTTP 429;
5. 在任一前端 chunk.js 内搜索 `DEEPSEEK_API_KEY` 字符串命中数为 0;
6. `git log -p --all -- '*.env'` 无输出(从未追踪);

满足以上六条即视为交付达成。

---

## 8. 工作分解预告(tasks.md 将据此细化)

为了让你随时叫停,大致拆分为五块独立可测的工作包:
- T1 加固 `.gitignore` 与清理潜在泄漏隐患(前置基线动作)
- T2 编写后端限流模块并把 CORS 改造落地(main.py 微手术)
- T3 产出 `runtime.txt`、`render.yaml`、`start.sh` 三件套
- T4 产出前端 `vercel.json`、`.env.production`,完善 client.ts 友好降级文案
- T5 整理一份《DEPLOY_GUIDE.md》逐步手册,覆盖 Render/Vercel 双平台的图形界面操作以及最终的占位符回填闭环

接下来我将根据这份 doc.md 生成对应的 tasks.md,请你审阅本文档是否符合预期。
