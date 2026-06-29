# 免费云部署改造 · tasks.md

> 对应 doc:`.comate/specs/deploy-to-cloud-free/doc.md`
> 共五个顶层任务,**严格顺序执行**(每个依赖前一项的安全基线或产物)。完成后整体达成 G1/G2/G3 三个核心目标。

---

- [ ] **Task 1:基线安全加固 — 强化 .gitignore 并核查历史是否曾泄密钥**
    - 1.1 在仓库根 `.gitignore` 中追加显式忽略规则:`__pycache__/`、`*.py[cod]`、`node_modules/`、`dist/`、`.DS_Store`;保留现有 `.env` 与 `*.env` 条目不变
    - 1.2 执行 `git log -p --all -- '*.env' 'backend/.env'` 核查历史上是否存在被纳入版本控制的 `.env` 文件内容
    - 1.3 若发现历史 commit 中出现真实的 `DEEPSEEK_API_KEY` 或 `EXA_API_KEY`:在本文件附录标记 `[需 Rotate]`,并在 DEPLOY_GUIDE 里给出三方平台轮换链接;若无则直接判定"Git 无残留"
    - 1.4 运行 `git status` 复核本次提交仅涉及 `.gitignore`,未误伤业务代码

- [ ] **Task 2:后端入口手术 — CORS 白名单化 + 进程内限流中间件**
    - 2.1 新建 `zhitan-risk-agent/backend/ratelimit.py`,实现 `RateLimitMiddleware(BaseHTTPMiddleware)`:`cachetools.TTLCache(maxsize=10000, ttl=600s)` 按 `request.client.host` 计数,默认上限 20 次/10 分钟;放行 `/` 与 `/health`;超限返回 `JSONResponse(status_code=429, content={"detail":"请求过于频繁..."})`
    - 2.2 在 `zhitan-risk-agent/backend/requirements.txt` 追加一行 `cachetools>=5.3,<7`
    - 2.3 编辑 `zhitan-risk-agent/backend/main.py`:顶部新增 `import os`,以及 `from ratelimit import RateLimitMiddleware`
    - 2.4 解析 `os.getenv("ALLOWED_ORIGINS")`(逗号分隔),空值时回退到 `["http://localhost:5173"]`;替换原第13–19行 CORSMiddleware 的 `allow_origins=["*"]` 为此变量,`allow_methods=["GET","POST","OPTIONS"]`,`allow_headers=["Content-Type"]`,`allow_credentials=False`
    - 2.5 在 CORS 之后追加 `app.add_middleware(RateLimitMiddleware, max_requests=20, window_seconds=600)`
    - 2.6 本地起 uvicorn 自测三条断言:(a) GET `/` 正常返回 health check;(b) cURL 发带 `Origin: http://evil.com` 的预检 OPTIONS 时响应头**不**含 `Access-Control-Allow-Origin`;(c) shell 循环连续发 21 次 `/api/query` 最后一次命中 HTTP 429

- [ ] **Task 3:渲染渲染器(Render)Blueprint 三件套**
    - 3.1 新建 `zhitan-risk-agent/backend/runtime.txt`,单行写入 `3.11.9`
    - 3.2 新建 `zhitan-risk-agent/backend/render.yaml`:声明单个 web service(`name: zhitan-risk-api`,`runtime: python`,`plan: free`,`buildCommand: pip install -r requirements.txt`,`startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT`,`healthCheckPath: /`)
    - 3.3 同一 yaml 内列出 envVars:`PYTHON_VERSION=3.11.9`(明文)、`DEEPSEEK_API_KEY`/`EXA_API_KEY`/`ALLOWED_ORIGINS` 全部设 `sync: false`(由你在 Dashboard 手工录入,yaml 即使公开也不漏 secret)
    - 3.4 使用 `python -c "import yaml;yaml.safe_load(open('render.yaml'))"` 本地校验 YAML 合法性

- [ ] **Task 4:Vite/Vercel 生产配置与友好降级文案**
    - 4.1 新建 `zhitan-risk-agent/frontend/.env.production`,唯一一行 `VITE_API_BASE=__REPLACE_WITH_RENDER_URL__`(明文占位符,非机密)
    - 4.2 新建 `zhitan-risk-agent/frontend/vercel.json`:`{"$schema":"https://openapi.vercel.sh/vercel.json","buildCommand":"npm run build","outputDirectory":"dist","rewrites":[{"source":"/(.*)","destination":"/index.html"}]}`
    - 4.3 编辑 `zhitan-risk-agent/frontend/src/api/client.ts` 的 `queryRisk` 异常分支文案,从 `'风险侦察失败,请确认后端服务已启动'` 改为 `'风险侦察失败,服务可能正从睡眠状态恢复,请稍候重试'`;不修改函数签名与其他逻辑
    - 4.4 进入 frontend 目录执行 `npm install && npm run build` 验证产物正常产出 `dist/index.html`,并对 `dist/**/*.{js}` 全文 grep 关键字 `DEEPSEEK_API_KEY` 与 `EXA_API_KEY`,确认均为零命中(局部验证 doc §7 的 G2)

- [ ] **Task 5:《DEPLOY_GUIDE.md》逐步图形界面操作指南**
    - 5.1 新建仓库根 `DEPLOY_GUIDE.md`,章节 A 说明如何创建 GitHub 公开 repo 并 push 当前已加固代码(强调不要单独 add `.env`)
    - 5.2 章节 B 给出 render.com 操作流:New → Blueprint → 选择刚才推送的 repo → 自动加载 `render.yaml` → 在 Variables 页签手动粘贴 `DEEPSEEK_API_KEY`、`EXA_API_KEY`(从此处开始它们才真正落进服务器侧)→ 等 Deploy Live 变绿 → 抄下形如 `https://zhitan-risk-api.onrender.com` 的 Service URL
    - 5.3 章节 C:把上一步得到的 URL 回填到 `frontend/.env.production` 的 `VITE_API_BASE`,commit+push 触发下一步的前端重新构建链路准备
    - 5.4 章节 D:登录 vercel.com Import Project 选同一 repo,Root Directory 必须选 `zhitan-risk-agent/frontend`,Framework Preset 会自动识别为 Vite,Build Output 默认 dist,Deploy 即可拿到 `<proj>.vercel.app` 终极公网地址
    - 5.5 章节 E 反向收口:回到 Render 该服务的 Environment,给 `ALLOWED_ORIGINS` 填入刚拿到的完整 vercel app URL(含 https://),Save Changes 触发 Manual Deploy,等其变绿
    - 5.6 章节 F 六步验收清单(对照 doc §7):GET `/` 健康 OK、跨域拒绝、自域调用 200、超限触发 429、bundle grep key 零命中、git 历史 grep .env 零输出
    - 5.7 附录 R(Key Rotation Emergency Playbook):万一未来发现误推了真 key,如何在 DeepSeek 平台与 Exa Console 各自 revoke&regenerate,以及在 Render 重置变量的位置截图位预留

> 所有五个任务勾掉之后我会汇总出一份 `summary.md`,包含此次变更的全部新文件清单、关键命令速查、与你需要在浏览器里完成的剩余点击清单。
