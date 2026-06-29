# 替换预设演示公司为真实头部公司并按实际情况硬编码数据 — 完成总结

## 一、需求回顾

用户要求将前端首页预设的占位符快捷入口（XX 科技、YY 网络等）替换为中国六大真实互联网公司 —— **百度、字节跳动、腾讯、拼多多、阿里、美团**，并根据各家公司在公开招聘口碑中的实际特征硬编码求职前风险评估样例数据。

## 二、改动范围与执行结果

### 后端 `backend/data/sample_companies.py`
- **SAMPLE_COMPANIES** 字典：原地替换六个占位符槽位为新公司条目，保留非快捷展示用的 `BB文化`、`EE金融`、`FF互娱乐`、`GG科技` 四个对照样本不动，共维持 10 条。
- **FEEDBACK** 字典：在原字典起始处注入六个真实公司的匿名反馈数组（每家三条：在职员工／已离职员工／面试者），原有 BB文化、GG科技 反馈保留不变。
- **COMPANY_SHORTCUTS** 列表：整段重写为六家新公司的 name/type/description。

各家公司维度要点：
| 公司 | caseType | 总风险分 | 主要信号 |
|---|---|---:|---|
| 百度 | low_risk | 1 | online.traditional_management |
| 字节跳动 | organization_instability | 5 | legal.labor_disputes_minor + online.intense_pace + business_contraction |
| 腾讯 | low_risk | 1 | online.bg_variance |
| 拼多多 | high_combo | **7** | legal.working_hours_attention + online.extreme_overtime + strict_management + position.implicit_pressure_jd |
| 阿里 | organization_instability | 4 | legal + restructure_discussion + performance_pressure |
| 美团 | mixed_feedback | 1 | line_adjustment + neutral_overall |

拼多多总分明朗高于其他五家，形成清晰的「高风险组合」演示锚点。

合规口径上所有信号均以「公开反馈中出现 X 标签」「检索到 N 条记录」等可验证性描述呈现，未对任何企业做主观价值定性。

### 前端 `frontend/src/components/HomePage.tsx`
- 重写本地兜底常量 `fallbackCompanies` 为同一组六家公司及对应 description 文案。
- 将搜索框 placeholder 由「如：XX 科技」改为「如：百度」。

未修改其他文件；类型定义 `CompanyShortcut.type` 本就是字符串透传字段，新增的 type 取值无需扩展枚举表即可正常工作。

## 三、关键架构约束处理

由于实体匹配走「基于名称的字串命中」路径（`entity_agent.normalize_entity()` 仅比对 query 与 SAMPLE_COMPANIES 的 key 或 aliases），单纯改前端文案会导致点击后无法触发预置报告而掉入通用 insufficient 兜底。因此必须三处联动同步更新：前端快捷列表 ↔ 后端 COMPANY_SHORTCUTS ↔ 后端 SAMPLE_COMPANIES。本次实现已确保三者名称完全一致并通过脚本校验：「shortcut 未命中 SAMPLE_COMPANIES 的项」结果为空。

别名覆盖方面也做了准备：例如输入「ByteDance」「阿里巴巴」「美团点评」「寻梦信息」等全称或英文别称也能命中对应主体，便于粘贴场景使用。

## 四、验收情况

执行 Python 导入测试通过以下检查项：
- 无语法错误，模块正常加载；
- 六个新 sample 键存在；
- 快捷名集合 = 样本键子集 ∩ 排除保留的四个旧 fixture；
- 各公司 baseScore 累加值梯度合理；
- DEFAULT_FEEDBACK 与原有保留 feedback 不受影响。

> 注：因运行环境限制未启动完整前后端服务跑端到端点击流程，但核心正确性已由数据层一致性校验保证。建议在具备依赖的环境下进一步手动确认 UI 渲染细节（雷达图分布、匿名反馈卡片数量）以及别名搜索行为是否符合预期。

## 五、后续可选增强

- 若希望展示更逼真的统一社会信用代码，可将 creditCode 从 None 改写为示意格式字符串并在渲染层明确标注「示意」。当前选择留空遵循保守原则避免误导。
- 可考虑给 EE金融/FF互娱乐/GG文化等保留 fixture 也补充中文短句描述以便未来若加入更多快捷卡片时复用。
