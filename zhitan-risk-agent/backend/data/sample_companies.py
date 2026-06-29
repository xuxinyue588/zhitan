from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

FETCHED_AT = "2026-06-18"


def signal(
    type_: str,
    title: str,
    description: str,
    source: str,
    confidence: str,
    base_score: float,
    raw_value: str,
    explanation: str,
    suggestion: str,
    source_type: str = "mock",
) -> dict[str, Any]:
    return {
        "type": type_,
        "title": title,
        "description": description,
        "source": source,
        "sourceType": source_type,
        "confidence": confidence,
        "fetchedAt": FETCHED_AT,
        "rawValue": raw_value,
        "baseScore": base_score,
        "explanation": explanation,
        "suggestion": suggestion,
    }


def dimension(name: str, summary: str, confidence: str, signals: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "name": name,
        "riskScore": sum(item.get("baseScore", 0) for item in signals),
        "confidence": confidence,
        "signals": signals,
        "summary": summary,
    }


FALLBACK_CHECKLIST = [
    "公司官网是否有实质业务内容，而不是只有模板化介绍？",
    "岗位描述是否清晰说明职责、汇报关系和考核方式？",
    "面试流程是否规范，是否能说明团队规模和业务现状？",
    "薪资结构、试用期比例、发薪日和绩效规则是否透明？",
    "同类岗位是否长期大量挂出，是否能说明真实 HC 来源？",
]

DISCLAIMER = "本产品基于公开信息与匿名反馈生成投递前风险提示，仅供求职辅助参考，不构成对任何企业的事实认定或价值判断。请用户结合官方信息、面试沟通及个人判断综合决策。"

SAMPLE_COMPANIES: dict[str, dict[str, Any]] = {
    "百度": {
        "aliases": ["百度在线网络技术（北京）有限公司", "Baidu", "baidu"],
        "creditCode": None,
        "caseType": "low_risk",
        "positionInfo": {"title": "高级研发工程师", "salary": "30-50K", "stage": "已上市(NASDAQ)", "scale": "10000人以上"},
        "dimensions": [
            dimension("scale", "招聘页规模庞大且参保人数充分可验证。", "high", []),
            dimension("capital", "2005 年纳斯达克上市多年，经营基础稳定。", "high", []),
            dimension("legal", "未检索到明显劳动争议或处罚信号。", "high", []),
            dimension("online", "公开反馈以中性为主，部分提到流程偏传统。", "medium", [
                signal("traditional_management", "流程与晋升偏传统",
                       "公开搜索结果丰富，匿名反馈中重复出现『流程相对传统』『晋升周期较长』『边缘业务线定期调整』等标签。",
                       "网页检索(样例摘要)", "medium", 1,
                       "晋升慢；边缘业务调整；管理较层级化",
                       "大型成熟企业常见特征，整体风险可控但需结合具体业务线判断。",
                       "建议确认岗位所在 BU 是否为核心利润线及近一年组织调整情况。", "search")
            ]),
            dimension("position", "岗位职责描述清晰。", "medium", []),
        ],
    },
    "字节跳动": {
        "aliases": ["ByteDance", "字节"],
        "creditCode": None,
        "caseType": "organization_instability",
        "positionInfo": {"title": "推荐算法工程师", "salary": "35-60K", "stage": "未上市(E轮+)", "scale": "10000人以上"},
        "dimensions": [
            dimension("scale", "未上市但融资估值公开披露充分。", "high", []),
            dimension("capital", "连续盈利传闻稳定，现金流充足。", "high", []),
            dimension("legal", "随规模化出现零星劳动争议记录，整体可控。", "medium", [
                signal("labor_disputes_minor", "少量劳动争议记录",
                       "近年存在若干劳动仲裁相关公开记录，符合大体量互联网企业的常规水平。",
                       "企业公开信息(样例数据)", "medium", 1,
                       "争议数量低于行业均值区间",
                       "零星记录不必然反映系统性问题，可作为辅助观察项。",
                       "建议面试中确认劳动合同条款、试用期比例和绩效申诉机制。")
            ]),
            dimension("online", "节奏强度信号显著且伴随结构调整讨论。", "medium", [
                signal("intense_pace", "高强度节奏标签密集",
                       "公开反馈中高频出现『OKR 变动频繁』『上下班弹性但不规律』『目标迭代极快』等描述。",
                       "网页检索(样例摘要)", "high", 2,
                       "OKR 频繁调整；目标迭代快；作息弹性大",
                       "强目标导向是公司增长引擎的一部分，但也意味着个人需适应高变化环境。",
                       "建议确认所在团队 OKR 周期、汇报频率以及加班补偿政策。", "search"),
                signal("business_contraction", "多条业务收缩讨论",
                       "出现『教育业务关停』『商业化团队优化』『海外产品合并』等多轮结构调整话题。",
                       "网页检索(样例摘要)", "medium", 2,
                       "教育关停；商业化优化；多业务盘点",
                       "结构性调整会直接影响新入职员工的稳定性预期。",
                       "建议确认拟入岗位所属业务是否在持续投入清单内。", "search")
            ]),
            dimension("position", "JD 通常明确并强调结果导向。", "medium", []),
        ],
    },
    "腾讯": {
        "aliases": ["腾讯控股有限公司", "Tencent", "tencent"],
        "creditCode": None,
        "caseType": "low_risk",
        "positionInfo": {"title": "后端开发工程师", "salary": "28-45K", "stage": "已上市(HKEX)", "scale": "10000人以上"},
        "dimensions": [
            dimension("scale", "规模庞大且社保参保充分可验证。", "high", []),
            dimension("capital", "港股主板长期上市公司，现金流稳健。", "high", []),
            dimension("legal", "未发现明显法律合规风险。", "high", []),
            dimension("online", "不同 BG 体感差异较大，游戏 BG 强度偏高。", "medium", [
                signal("bg_variance", "BG 体感差异明显",
                       "在职与离职反馈普遍指出各事业群在加班强度、考核机制和文化氛围上差异较大；游戏 BG 反馈中『项目制压力大』较为集中。",
                       "网页检索(样例摘要)", "medium", 1,
                       "BG 差异大；游戏项目制压力；其他 BG 相对稳定",
                       "体感差异意味着同公司内部体验高度依赖所分配的团队。",
                       "建议明确告知 HR 目标 BG 与项目组，并在 offer 中固化归属关系。", "search")
            ]),
            dimension("position", "职责划分规范。", "medium", []),
        ],
    },
    "拼多多": {
        "aliases": ["PDD Holdings", "上海寻梦信息技术有限公司", "Pinduoduo"],
        "creditCode": None,
        "caseType": "high_combo",
        "positionInfo": {"title": "服务端开发工程师", "salary": "40-70K", "stage": "已上市(NASDAQ)", "scale": "1000人以上"},
        "dimensions": [
            dimension("scale", "市值进入前列，人员规模持续扩张。", "high", []),
            dimension("capital", "2018 年美股上市，近年财报显示强劲盈利能力。", "high", []),
            dimension("legal", "曾因工时安排引起社会关注的合规讨论。", "medium", [
                signal("working_hours_attention", "工时相关社会关注",
                       "公开招聘口碑渠道多次提及工作时长相关的社会关注事件，监管部门亦有过约谈类报道。",
                       "网页检索(样例摘要)", "medium", 1,
                       "存在过工时合规相关社会关注",
                       "此类历史信号提示需重点核验当前实际排班制度是否符合自身承受能力。",
                       "建议直接询问每日下班时间常态、周末调休规则与节假日安排。", "search")
            ]),
            dimension("online", "高强度与严管理的负面信号最为集中的一家。", "high", [
                signal("extreme_overtime", "极端加班标签高频出现",
                       "公开反馈大量集中出现『每月仅一次单休』『常态晚于 22 点下班』『强制末位淘汰』『午休时间极短』等强烈强度信号。",
                       "网页检索(样例摘要)", "high", 3,
                       "每月一休；22 点后下班常见；末位淘汰",
                       "强度信号密度远高于行业平均，属于求职决策前必须直面的核心变量。",
                       "若接受 offer 应同步评估健康成本、家庭协调方案和中短期退出计划。", "search"),
                signal("strict_management", "强势管理与严苛绩效反复被提及",
                       "匿名评价中频繁出现『管理风格非常强势』『罚款式扣罚』『绩效考核严苛不留情面』等关键词。",
                       "匿名反馈(样例数据)", "medium", 2,
                       "管理强势；绩效严苛；罚款机制",
                       "高压管理模式可能放大心理负担，需评估个人适配度而非单纯薪资吸引力。",
                       "建议面试时观察面试官风格并向在职员工侧面了解真实日常。")
            ]),
            dimension("position", "JD 明确但隐含高压预期。", "medium", [
                signal("implicit_pressure_jd", "JD 中隐含高压暗示",
                       "部分 JD 使用『极致投入』『快速迭代到极限』『结果导向无上限』等表述，需识别其中隐含的工作量预期。",
                       "招聘页信息(样例数据)", "medium", 1,
                       "JD 含极致投入表述",
                       "措辞本身不构成风险，但是对实际强度的间接佐证。",
                       "建议将 JD 措辞作为面谈切入点逐句澄清量化标准。")
            ]),
        ],
    },
    "BB文化": {
        "aliases": ["BB文化传媒"],
        "creditCode": "91110000BB20260005",
        "caseType": "mixed_feedback",
        "positionInfo": {"title": "内容策划", "salary": "10-16K", "stage": "未融资", "scale": "50-99人"},
        "dimensions": [
            dimension("scale", "规模信息基本正常。", "medium", []),
            dimension("capital", "经营基础未见明显异常。", "medium", []),
            dimension("legal", "未发现明显法律合规风险。", "high", []),
            dimension("online", "评价呈现两极化。", "medium", [
                signal("mixed_feedback", "员工评价两极", "匿名反馈同时出现“成长快”和“管理强势”等标签。", "匿名反馈（样例数据）", "medium", 2, "成长快；管理强势；晋升一般", "评价分歧说明体验可能与团队和直属管理者强相关。", "建议确认汇报关系、工作节奏和晋升标准。")
            ]),
            dimension("position", "岗位职责较清楚。", "medium", []),
        ],
    },
    "阿里": {
        "aliases": ["阿里巴巴集团控股有限公司", "Alibaba Group", "阿里巴巴"],
        "creditCode": None,
        "caseType": "organization_instability",
        "positionInfo": {"title": "Java 开发工程师(P6)", "salary": "30-55K", "stage": "已上市(NYSE/HKEX)", "scale": "10000人以上"},
        "dimensions": [
            dimension("scale", "大体量集团主体，人员规模信息完整。", "high", []),
            dimension("capital", "多地上市成熟企业，资本结构透明。", "high", []),
            dimension("legal", "存在若干劳动仲裁公开案件，处于常规水平区间。", "medium", [
                signal("labor_disputes_normal_scale", "大体量下常规水平案件",
                       "公开司法文书中可见一定数量的劳动争议案件，绝对数量不低但在同等员工基数的企业间属正常分布。",
                       "企业公开信息(样例数据)", "medium", 1,
                       "劳动争议数量级正常",
                       "数字本身不应单独定性为高风险，宜与其他维度交叉观察。",
                       "建议重点关注 P 级对应的转正条件与离职竞业协议范围。")
            ]),
            dimension("online", "分拆重组期不确定性成为近期主旋律。", "medium", [
                signal("restructure_discussion", "重组进展讨论热度高",
                       "自 1+6+N 分拆启动以来，公开渠道反复出现『独立融资进度不明朗』『BU 边界仍在磨合』『中台拆解影响协同效率』等讨论。",
                       "网页检索(样例摘要)", "medium", 2,
                       "1+6+N 进行中；BU 边界磨合；独立融资待定",
                       "过渡期内的新员工可能面临汇报线和资源池变动。",
                       "建议确认拟加入实体法人主体、汇报路径稳定性及未来半年预算冻结状态。", "search"),
                signal("performance_pressure", "361 考核体系压力反复出现",
                       "匿名社区中长期活跃关于『361 末位强制分布』『向上汇报链路长』『年中述职消耗精力』的话题。",
                       "匿名反馈(样例数据)", "medium", 1,
                       "361 末位；汇报链路长；述职压力大",
                       "成熟的硬性考核并非缺陷，但对适应扁平文化的候选人构成额外挑战。",
                       "建议提前了解 P 序列对应 KPI 结构与最近两次校准的实际分布。")
            ]),
            dimension("position", "P 级定义清晰。", "medium", []),
        ],
    },
    "美团": {
        "aliases": ["北京三快科技有限公司", "Meituan", "美团点评"],
        "creditCode": None,
        "caseType": "organization_instability",
        "positionInfo": {"title": "后端工程师", "salary": "25-42K", "stage": "已上市(HKEX)", "scale": "10000人以上"},
        "dimensions": [
            dimension("scale", "外卖/本地生活龙头规模庞大，但近一年经历多轮业务收缩调整。", "high", []),
            dimension("capital", "港股上市并实现规模化盈利，资本结构稳健。", "high", []),
            dimension("legal", "随组织优化推进，劳动争议相关记录数量较上一周期有所增长。", "medium", [
                signal("labor_disputes_increase", "劳动仲裁数量同比上升",
                       "公开裁判文书库中该公司涉劳动争议案件数量较前一周期出现可见增长，主要集中在经济补偿金与违法解除劳动合同两类案由。",
                       "企业公开信息(样例数据)", "medium", 2,
                       "案件数量同比增长",
                       "案件量的变化往往滞后反映实际用工动作，可作为辅助观察指标。",
                       "建议面试前查阅拟入职城市最新的裁判文书了解趋势走向。")
            ]),
            dimension("online", "大规模组织优化的舆情显著升温，超出往常周期性盘整水平。", "medium", [
                signal("major_layoff_discussion", "大规模组织优化舆情密集",
                       "2025 年以来围绕『社区团购事业部大幅缩减』『到店事业群合并编制』『无人配送团队关停』『部分区域骑手运力转外包』等话题在匿名社区高频出现，并被多家财经媒体跟进报道，讨论热度与覆盖业务线条数均高于过往季度性盘整。",
                       "网页检索(样例摘要)", "high", 3,
                       "多条业务线同步盘点；媒体广泛跟踪跟进",
                       "本轮调整覆盖面广于常规盘整，对新员工的中短期稳定性预期构成实质影响。",
                       "建议确认拟入岗位所属 BU 是否在本轮受影响清单内，以及是否存在 HC 冻结窗口期。", "search")
            ]),
            dimension("position", "HC 审批趋于严格，部分岗位放出速度放缓。", "medium", [
                signal("hc_freeze_signal", "HC 收紧迹象显现",
                       "招聘平台数据显示多个技术岗位连续挂出周期延长、补岗速度放缓，疑似与新业务缩编后的总量管控有关；个别候选人反馈 offer 发放后被推迟入职日期。",
                       "招聘页信息(样例数据)", "low", 1,
                       "岗位更新频率下降；个别 offer 推迟入职",
                       "HC 收紧并不等同于全面停招，但对个人的入职时点与部门选择提出了更高敏感度。",
                       "建议确认 offer 发放的主体法人与是否绑定特定项目预算。")
            ]),
        ],
    },
    "EE金融": {
        "aliases": ["EE金融科技"],
        "creditCode": "91110000EE20260008",
        "caseType": "funding_claim",
        "positionInfo": {"title": "风控产品经理", "salary": "20-30K", "stage": "自称B轮", "scale": "50-99人"},
        "dimensions": [
            dimension("scale", "规模信息基本正常。", "medium", []),
            dimension("capital", "融资真实性有待核验。", "medium", [
                signal("unverified_funding", "融资披露无法验证", "招聘页自称 B 轮，但未检索到公开融资披露。", "网页检索（样例摘要）", "medium", 2, "自称 B 轮；无公开融资记录", "融资信息不一致会影响对稳定性和现金流的判断。", "建议面试中询问融资主体、投资方和资金使用周期。", "search")
            ]),
            dimension("legal", "未发现明显合规风险。", "high", []),
            dimension("online", "网络存在正常但披露有限。", "medium", [
                signal("limited_disclosure", "信息披露有限", "官网介绍完整，但融资和客户案例披露较少。", "网页检索（样例摘要）", "medium", 1, "融资披露少；客户案例少", "关键经营信息披露有限时需进一步核验。", "建议确认业务资质、客户类型和收入来源。", "search")
            ]),
            dimension("position", "岗位描述较明确。", "medium", []),
        ],
    },
    "FF互娱": {
        "aliases": ["FF互动娱乐"],
        "creditCode": "91110000FF20260009",
        "caseType": "weak_online_presence",
        "positionInfo": {"title": "游戏运营", "salary": "12-20K", "stage": "未知", "scale": "50-99人"},
        "dimensions": [
            dimension("scale", "公开规模信息有限。", "medium", []),
            dimension("capital", "成立 2 年，资本信息一般。", "medium", []),
            dimension("legal", "未发现明显法律合规风险。", "medium", []),
            dimension("online", "官网质量和搜索丰富度偏弱。", "medium", [
                signal("poor_website", "官网质量偏低", "官网内容较少，产品与团队介绍不完整。", "官网公开信息（样例数据）", "medium", 1, "官网模板化；内容少", "官网简陋不等于高风险，但会降低透明度。", "建议核验真实产品、上线渠道和团队规模。", "search"),
                signal("few_search_results", "搜索结果稀少", "公开搜索结果较少，难以交叉验证业务真实性。", "网页检索（样例摘要）", "medium", 1, "搜索结果少", "外部可验证信息不足。", "建议询问产品数据、收入来源和主要项目。", "search")
            ]),
            dimension("position", "岗位描述基本完整。", "medium", []),
        ],
    },
    "GG科技": {
        "aliases": ["GG科技集团"],
        "creditCode": "91110000GG20260010",
        "caseType": "organization_instability",
        "positionInfo": {"title": "产品运营", "salary": "16-24K", "stage": "C轮", "scale": "500-999人"},
        "dimensions": [
            dimension("scale", "规模信息较完整。", "high", []),
            dimension("capital", "融资和成立时间信息较完整。", "medium", []),
            dimension("legal", "少量劳动争议记录。", "high", [
                signal("labor_disputes_minor", "存在劳动争议记录", "近年存在 2 条劳动争议相关记录。", "企业公开信息（样例数据）", "high", 1, "劳动争议 2 条", "记录数量不高，但可结合口碑信号观察。", "建议确认绩效与转正规则。")
            ]),
            dimension("online", "组织稳定性反馈偏弱。", "medium", [
                signal("layoff_discussion", "组织调整讨论较多", "公开反馈中多次出现“裁员”“优化”“业务调整”等标签。", "网页检索（样例摘要）", "medium", 2, "裁员；优化；业务调整", "重复出现的组织调整信号会影响岗位稳定性。", "建议确认岗位所在业务线是否稳定、团队近期是否调整。", "search"),
                signal("negative_interview", "面试反馈偏负面", "部分面试反馈提到流程反复、反馈周期较长。", "匿名反馈（样例数据）", "medium", 2, "流程反复；反馈慢", "流程体验可能反映内部协同效率。", "建议确认流程节点和录用决策人。")
            ]),
            dimension("position", "岗位职责较明确。", "medium", []),
        ],
    },
}

FEEDBACK: dict[str, list[dict[str, Any]]] = {
    "百度": [
        {"type": "current_employee", "title": "在职员工", "tags": ["薪资稳定", "流程规范", "晋升偏慢"], "summary": "发薪准时、福利齐全，但晋升通道较长，边缘业务线偶有调整。", "count": 42},
        {"type": "former_employee", "title": "已离职员工", "tags": ["体系成熟", "内部政治一般", "成长放缓"], "summary": "适合作为长期平台，但部分老业务增长乏力，个人空间受限。", "count": 33},
        {"type": "interviewee", "title": "面试过的人", "tags": ["流程正规", "反馈及时", "问题基础"], "summary": "校招与社招均规范，技术面以算法和系统设计为主。", "count": 28},
    ],
    "字节跳动": [
        {"type": "current_employee", "title": "在职员工", "tags": ["薪资有竞争力", "OKR 节奏快", "弹性工作"], "summary": "薪酬包亮眼且期权流动性较好；强度高但目标清晰。", "count": 55},
        {"type": "former_employee", "title": "已离职员工", "tags": ["成长极快", "强度高", "业务变动"], "summary": "高密度训练场但身心消耗明显，建议规划好退出节奏。", "count": 48},
        {"type": "interviewee", "title": "面试过的人", "tags": ["题目硬核", "流程紧凑", "多轮交叉面"], "summary": "对算法与项目深度要求较高，HR 反馈通常较快。", "count": 40},
    ],
    "腾讯": [
        {"type": "current_employee", "title": "在职员工", "tags": ["氛围相对宽松", "福利好", "BG 差异大"], "summary": "整体待遇与文化在头部中靠前，体验取决于所在事业群。", "count": 50},
        {"type": "former_employee", "title": "已离职员工", "tags": ["节奏可控", "游戏线压力大", "转岗机制存在"], "summary": "多数人评价正面，但游戏及 To C 业务加班较多。", "count": 38},
        {"type": "interviewee", "title": "面试过的人", "tags": ["流程规范", "HR 专业", "周期适中"], "summary": "笔试到 offer 通常一个月内完成，沟通顺畅。", "count": 35},
    ],
    "拼多多": [
        {"type": "current_employee", "title": "在职员工", "tags": ["薪资极高", "工作强度极大", "单休为主"], "summary": "收入领先行业但要付出几乎全部时间精力，性价比因人而异。", "count": 36},
        {"type": "former_employee", "title": "已离职员工", "tags": ["现金回报可观", "身心透支", "文化强势"], "summary": "短期赚钱效率高的选择之一，长期可持续性需自行评估。", "count": 44},
        {"type": "interviewee", "title": "面试过的人", "tags": ["轮次精简", "决策迅速", "实用导向"], "summary": "面试务实高效，但需提前确认能否接受作息安排再投递。", "count": 25},
    ],
    "阿里": [
        {"type": "current_employee", "title": "在职员工", "tags": ["P 序列成熟", "中台资源多", "重组过渡期"], "summary": "技术与工程底蕴深厚，分拆后 BU 边界仍在磨合。", "count": 47},
        {"type": "former_employee", "title": "已离职员工", "tags": ["考核严格(361)", "向上汇报成本高", "业务波动增加"], "summary": "管理体系高度结构化，适应与否差异显著。", "count": 39},
        {"type": "interviewee", "title": "面试过的人", "tags": ["HRG 全程参与", "P 级评定明确", "述职氛围浓"], "summary": "晋升答辩文化浓厚，新人需要时间熟悉述职范式。", "count": 31},
    ],
    "美团": [
        {"type": "current_employee", "title": "在职员工", "tags": ["主业底盘尚稳", "BU 合并频繁", "HC 审批收紧"], "summary": "核心本地商业基本盘稳定，但多个新业务事业部处于盘整合并状态，内部转岗窗口收窄。", "count": 38},
        {"type": "former_employee", "title": "已离职员工", "tags": ["N+1 相对规范", "项目被砍被动离开", "转岗机会有限"], "summary": "多数人评价离职补偿兑现较为规范，但所在项目一旦进入缩减名单个人腾挪空间不大。", "count": 32},
        {"type": "interviewee", "title": "面试过的人", "tags": ["部分岗位暂停放号", "流程偶有中断", "决策周期延长"], "summary": "受影响 BU 存在 offer 进程延迟乃至撤销情形，投递前最好确认 HC 是否已锁定。", "count": 24},
    ],

    "BB文化": [
        {"type": "current_employee", "title": "在职员工", "tags": ["薪资准时", "加班偏多", "团队氛围尚可"], "summary": "多数反馈认为发薪稳定，但工作节奏较快。", "count": 6},
        {"type": "former_employee", "title": "已离职员工", "tags": ["成长快", "管理强势", "晋升一般"], "summary": "适合作为过渡和积累经验的平台，但管理风格两极化。", "count": 4},
        {"type": "interviewee", "title": "面试过的人", "tags": ["流程透明", "HR专业", "反馈较慢"], "summary": "流程整体规范，但反馈周期偏长。", "count": 5},
    ],
    "GG科技": [
        {"type": "current_employee", "title": "在职员工", "tags": ["业务调整", "节奏较快", "目标变化"], "summary": "反馈集中在组织节奏和目标调整频繁。", "count": 8},
        {"type": "former_employee", "title": "已离职员工", "tags": ["成长快", "压力大", "稳定性一般"], "summary": "适合能接受高变化节奏的人群。", "count": 7},
        {"type": "interviewee", "title": "面试过的人", "tags": ["流程反复", "反馈较慢", "问题深入"], "summary": "面试问题较细，但流程周期偏长。", "count": 6},
    ],
}

DEFAULT_FEEDBACK = [
    {"type": "current_employee", "title": "在职员工", "tags": ["信息有限", "需自行核验"], "summary": "当前匿名反馈样本有限，建议以面试核验为主。", "count": 2},
    {"type": "former_employee", "title": "已离职员工", "tags": ["样本较少"], "summary": "离职反馈不足，暂不形成明确判断。", "count": 1},
    {"type": "interviewee", "title": "面试过的人", "tags": ["流程待确认"], "summary": "建议重点确认流程节点和反馈周期。", "count": 1},
]

COMPANY_SHORTCUTS = [
    {"name": "百度", "type": "low_risk", "description": "低风险·成熟大盘"},
    {"name": "字节跳动", "type": "organization_instability", "description": "节奏快·业务收缩关注"},
    {"name": "腾讯", "type": "low_risk", "description": "低风险·BG 差异注意"},
    {"name": "拼多多", "type": "high_combo", "description": "高风险·高强度组合"},
    {"name": "阿里", "type": "organization_instability", "description": "分拆期·考核激进"},
    {"name": "美团", "type": "organization_instability", "description": "组织大幅盘整·关注影响面"},
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
