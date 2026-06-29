# 替换预设演示公司为真实头部公司并按实际情况硬编码数据

## 一、需求场景

当前前端首页预设的快捷查询入口为占位符样例公司（XX科技、YY网络、ZZ智能、AA教育、CC传媒、DD咨询），点击后由后端 `SAMPLE_COMPANIES` 通过名称匹配返回预置风险报告。占位符名称缺乏真实感，不利于产品体验和对外演示。

用户要求：
1. 将六个快捷按钮替换为真实中国头部科技公司：**百度、字节跳动、腾讯、拼多多、阿里、美团**
2. 根据「实际情况」硬编码这六家公司的求职前风险评估数据 —— 即基于各公司在公开招聘口碑中的实际特征（用工强度、组织稳定性、法律合规记录等）撰写可信的样例维度数据，而非沿用旧模板的虚构数值

由于现有架构采用 **基于公司名的实体匹配**（`entity_agent.normalize_entity()` 仅依据 query 文本是否命中 `SAMPLE_COMPANIES` 的 key 或 alias 来分发预写报告），仅替换前端文案会导致点击后无法命中后端数据而落入通用兜底分支。因此必须同步更新三处：前端快捷列表、后端 `COMPANY_SHORTCUTS` 列表、后端 `SAMPLE_COMPANIES` 数据字典，并为每家公司补充对应 `FEEDBACK` 条目以保证匿名反馈区域也具备真实性。

> 合规边界：本产品定位为「投递前的辅助参考」，所有内容须保持事实性、可验证性描述口径（如「公开反馈中出现 X 标签」「检索到 N 条劳动争议」），不构成对企业的价值判断或事实认定。对各家公司的负面特征只引用业内广泛流传的客观信号类别，不点名具体事件或个人。

---

## 二、架构与技术方案

### 数据流路径
```
HomePage 快捷卡片 click
    ↓ 提交该公司名作为 query
POST /api/query {query:"百度"}
    ↓ pipeline.run_pipeline()
entity_agent.normalize_entity("百度")
    ↓ 命中 SAMPLE_COMPANIES["百度"] 的 key/alias
返回 deepcopy(company_data)，含 dimensions[]
    ↓ judge/search 等环节使用该预填数据组装最终响应
ResultPage 渲染五个维度的雷达图 + 风险卡 + 匿名反馈区
```

同时首页加载时通过 `GET /api/companies` 返回 `COMPANY_SHORTCUTS` 作为快捷卡片配置（含 name/type/description）。失败时回退到前端内置 `fallbackCompanies`。

### 实体匹配关键约束
`normalize_entity` 仅做字符串包含判断：query 是否等于某 key，或在 alias 列表中找到精确匹配。因此新增公司的中文短名必须即作 dict key 也加入 shortcut.name 保持一致；常见全称需写入 alias 以便用户输入完整名时也能命中。

### 五个评估维度复用既有定义
scale（规模真实性）、capital（资金与成立）、legal（法律合规）、online（网络透明度）、position（岗位风险）。
每个维度可携带多个 signal，signal.baseScore 累加得到 dimension.riskScore。
confidence 取值 high/medium/low；sourceType 默认 mock，纯网页类用 search。

---

## 三、受影响文件清单

| # | 绝对路径 | 改动类型 | 受影响函数/字段 |
|---|---|---|---|
| A | `/Users/xuxinyue/Downloads/zhitan-risk-agent-backup-20260628/zhitan-risk-agent/backend/data/sample_companies.py` | 编辑 | `SAMPLE_COMPANIES`(替换其中 6 个旧条目为新条目)；`FEEDBACK`(新增 6 家条目)；`COMPANY_SHORTCUTS`(重命名 6 个对象) |
| B | `/Users/xuxinyue/Downloads/zhitan-risk-agent-backup-20260628/zhitan-risk-agent/frontend/src/components/HomePage.tsx` | 编辑 | `fallbackCompanies` 数组(行 ~附近)；input placeholder 文案 |
| C | （可选不改）/zhitan-risk-agent/frontend/src/api/client.ts | 不改 | 错误提示文案语义仍适用 |

注：保留非快捷展示用的 BB文化/EE金融/FF互娱/GG科技 等 SAMPLE_COMPANIES 与其 FEEDBACK 条目不动，它们不影响快捷入口且可作为非命中场景下的对照样本继续可用。

---

## 四、六家公司实施方案

公共字段约定：
- `FETCHED_AT="2026-06-18"` 复用全局常量
- creditCode 设为 None 表示不暴露伪造统一社会信用代码（更稳妥）；如需带值则明显标注为示意格式
- positionInfo 各家选用代表性技术岗

### 4.1 百度 (`baidu`, caseType=`low_risk`)
- 别名：百度在线网络技术（北京）、Baidu
- 定位：综合最低风险的标杆案例（成熟大盘股）
- 维度设计：
  * scale(high)：无信号，「招聘页规模庞大且参保人数充分。」
  * capital(high)：「2005 年纳斯达克上市，经营基础稳定。」
  * legal(high)：空
  * online(medium)：1 个信号 `traditional_management`：「公开反馈中重复出现『流程偏传统』『晋升周期较长』『边缘业务调整』等标签」（baseScore 1）
  * position(low→合并到online)：略
  
### 4.2 字节跳动 (`bytedance`, caseType=`organization_instability`)
- 别名：ByteDance、字节
- 特征映射：高速增长型独角兽 + 文化强调效率导致强度高 + 近年教育与商业化等多轮业务收缩
- 维度：
  * scale(high): 空，「未上市但融资估值公开披露充分。」
  * capital(high): 「连续多年盈利传闻稳定，现金流充足。」
  * legal(medium): 「随规模化出现零星劳动争议记录，整体可控。」baseScore 1
  * online(medium):
      - `intense_pace`: 公开反馈高频出现『OKR 变动频繁』『上下班弹性但不规律』『目标迭代极快』 baseScore 2
      - `business_contraction`: 出现『教育业务关停』『商业化团队优化』等结构调整讨论 baseScore 2
  * position(medium): 空

### 4.3 腾讯 (`tencent`, caseType=`low_risk`)
- 别名：腾讯控股、Tencent
- 口碑在六大中最稳健之一（鹅厂文化相对宽松）
- 维度基本同百度甚至更低分；legal 全清；
  * online(medium): 单一信号 `bg_variance`：「不同 BG 体感差异较大，游戏 BG 反馈中『项目制压力大』较为集中。」baseScore 1

### 4.4 拼多多 (`pinduoduo`, caseType=`high_combo`)
- 别名：PDD Holdings、寻梦信息
- 业界公认高强度代表；本次唯一明确高总分公司样本
- 维度：
  * scale(high): 「2024 年市值进入前列，人员规模持续扩张。」
  * capital(high): 「2018 年美股上市，利润表现强劲。」
  * legal(medium): 「伴随快速扩张曾引起社会关注的工时合规讨论。」baseScore 1
  * online(high):
      - `extreme_overtime`: 公开反馈大量出现『每月调休一次』『常态晚于22 点下班』『强考核末位』等标签 baseScore 3
      - `strict_management`: 『管理风格强势』『绩效严苛』频次较高 baseScore 2
  * position(medium): 「JD 通常明确但隐含高压预期。」baseScore 1

### 4.5 阿里巴巴 (`alibaba`, caseType=`organization_instability`)
- 别名：Alibaba Group、阿里集团
- 关键现实背景：近两年推行 1+6+N 分拆带来组织不确定性 + 历史 361 考核争议
- 维度：
  * scale(high)/capital(high): 成熟上市主体
  * legal(medium): 存在若干劳动仲裁公开案件，符合大体量企业常规水平 baseScore 1
  * online(medium):
      - `restructure_discussion`: 公开渠道反复出现『分拆重组』『独立融资进展不明朗』『BU 边界仍在磨合』 baseScore 2
      - `performance_pressure`: 『361 末位』『向上汇报成本高』反复提及 baseScore 1
  * position(medium): 空

### 4.6 美团 (`meituan`, caseType=`mixed_feedback`)
- 别名：Meituan、美团点评
- 工程师社区普遍视其为务实派，但有阶段性业务线裁撤（如美团优选局部收缩）
- 维度：
  * scale(capital/legal 均 high/empty)
  * online(medium):
      - `line_adjustment`: 『新业务定期盘点』『社区团购编制波动』讨论中等频率 baseScore 1
      - `neutral_overall`: 主流反馈偏向中性『工程氛围扎实』『福利一般』 baseScore 0
  * position(medium): 空

### 4.7 FEEDBACK 表项规划
为上述 6 家分别写入三条匿名反馈（在职员工 / 已离职员工 / 面试者），tags 与 summary 围绕各自线上口碑主题拟定，count 给出合理量级数字（10~80 区间体现大厂样本丰富度）。

---

## 五、前端改动细节

### HomePage.tsx
将原 `fallbackCompanies` 六元素替换：

```ts
const fallbackCompanies: CompanyShortcut[] = [
  { name: '百度', type: 'low_risk', description: '低风险·成熟大盘' },
  { name: '字节跳动', type: 'organization_instability', description: '节奏快·业务收缩关注' },
  { name: '腾讯', type: 'low_risk', description: '低风险·BG差异注意' },
  { name: '拼多多', type: 'high_combo', description: '高风险·高强度组合' },
  { name: '阿里', type: 'organization_instability', description: '分拆期·考核激进' },
  { name: '美团', type: 'mixed_feedback', description: '中性·业务线波动' },
];
```

placeholder 由 `如：XX科技` 更换为 `如：百度`。

type 字段取值集合扩展支持 `organization_instability`、`high_combo`、`mixed_feedback`、`low_risk` 等（均为字符串透传至样式逻辑，无需类型表更新）。

---

## 六、边界条件与异常处理

1. 名称一致性陷阱：shortcut.name 必须能直接触发 normalize_entity 命中，因此选择日常称呼而非工商全称作为主键（例如选「阿里」「字节跳动」「美团」这种最常用简称），把全称放入 aliases 兜底。
2. 中文标点统一半角逗号分隔 tags。
3. baseScore 总和不刻意追求分级阈值，因为最终风险等级由 judge agent 二次判定；保证拼多多明显高于其他几家即可形成对比梯度。
4. creditCode 用 None 避免生成虚假社会信用代码造成误导，渲染层已有兜底显示「暂不可查」。
5. FEEDBACK count 数字仅供 UI 展示，不做累加校验。
6. DEFAULT_FEEDBACK 在六家之外的公司依旧生效不受影响。

---

## 七、验收标准

- 启动前后端服务后访问首页，快捷卡片依次显示六家真实公司及其 description。
- 点击任一家立即跳转结果页并正确呈现五维雷达图与本方案设计的信号说明文本（不再走 insufficient-data 兜底）。
- 在搜索框粘贴别名（例：输入「ByteDance」「阿里集团」「美团点评」）也能命中相应预置数据。
- 拼多多页面各项分数显著高于其他五家，体现差异化对比效果。
- 所有正文措辞均以「公开反馈／检索结果」口吻陈述，不含主观定性结论词句，遵守 DISCLAIMER 文风一致原则。
