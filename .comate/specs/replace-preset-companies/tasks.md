# 替换预设演示公司为真实头部公司并按实际情况硬编码数据 — 任务计划

- [ ] Task 1: 在 `sample_companies.py` 中新增六家真实公司的 `SAMPLE_COMPANIES` 条目
    - 1.1: 新增「百度」条目（low_risk 标杆，含 scale/capital/legal/online/position 五维，online 携 `traditional_management` 单信号）
    - 1.2: 新增「字节跳动」条目（organization_instability，legal+online 双信号，online 含 intense_pace 与 business_contraction）
    - 1.3: 新增「腾讯」条目（low_risk，仅 online 携 bg_variance 单信号）
    - 1.4: 新增「拼多多」条目（high_combo，online 高分双信号 + legal 中等信号，position 一弱信号）
    - 1.5: 新增「阿里」条目（organization_instability，legal 中等 + online restructure_discussion/performance_pressure）
    - 1.6: 新增「美团」条目（mixed_feedback，online line_adjustment 与 neutral_overall）
    - 1.7: 为六家公司补充对应 aliases、creditCode=None 与代表性 positionInfo

- [ ] Task 2: 为六家公司在 `FEEDBACK` 字典中写入匿名反馈数据
    - 2.1: 编写百度三条反馈（在职 / 离职 / 面试者），tags 围绕流程规范但晋升慢
    - 2.2: 编写字节跳动三条反馈，tags 强调 OKR 节奏与业务收缩
    - 2.3: 编写腾讯三条反馈，突出 BG 体感差异
    - 2.4: 编写拼多多三条反馈，反映高强度与严管理
    - 2.5: 编写阿里三条反馈，覆盖重组期不确定性与考核压力
    - 2.6: 编写美团三条反馈，体现务实工程氛围与新业务波动

- [ ] Task 3: 重命名 `COMPANY_SHORTCUTS` 列表为六家真实公司
    - 3.1: 将六个旧占位符对象替换为 百度 / 字节跳动 / 腾讯 / 拼多多 / 阿里 / 美团
    - 3.2: 校对 type/description 文案与本方案一致

- [ ] Task 4: 更新前端 `HomePage.tsx`
    - 4.1: 替换 `fallbackCompanies` 数组内容为新公司名及 description
    - 4.2: 将搜索框 placeholder 由「如：XX科技」改为「如：百度」

- [ ] Task 5: 本地启动验证与回归检查
    - 5.1: 启动后端确认无导入错误且 `/api/companies` 返回新列表
    - 5.2: 启动前端首页核对快捷卡片渲染正确
    - 5.3: 抽样点击拼多多等高风险卡片，确认结果页命中预置维度而非兜底分支；别名搜索校验一次

