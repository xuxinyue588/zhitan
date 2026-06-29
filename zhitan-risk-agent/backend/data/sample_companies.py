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
    "XX科技": {
        "aliases": ["XX科技有限公司", "XX Tech"],
        "creditCode": "91110000XX20260001",
        "caseType": "low_risk",
        "positionInfo": {"title": "前端开发工程师", "salary": "18-25K", "stage": "A轮", "scale": "100-499人"},
        "dimensions": [
            dimension("scale", "招聘页规模与公开参保人数大体匹配。", "high", [
                signal("scale_match", "规模信息基本匹配", "招聘页显示 100-499 人，公开参保人数 186 人，未发现明显差异。", "企业公开信息（样例数据）", "high", 0, "招聘规模 100-499；参保人数 186", "参保人数与招聘页区间匹配度较高。", "可继续了解团队结构和岗位 HC。")
            ]),
            dimension("capital", "成立时间和实缴信息较稳定。", "high", [
                signal("stable_foundation", "经营基础较稳定", "公司成立 6 年，注册资本与实缴信息较完整。", "国家企业信用信息公示系统（样例数据）", "high", 0, "成立 6 年；注册资本 1000 万；实缴 800 万", "成立时间和资本信息未呈现明显异常。", "面试中可进一步了解业务增长和团队规划。")
            ]),
            dimension("legal", "未检索到明显劳动争议或处罚信号。", "high", []),
            dimension("online", "官网与公开搜索结果较完整。", "medium", [
                signal("normal_presence", "网络存在正常", "官网、产品介绍和招聘信息较完整，公开反馈以中性为主。", "网页检索（样例摘要）", "medium", 0, "官网完整；搜索结果丰富", "公开信息可见度较好。", "可核验岗位所在业务是否仍在投入。", "search")
            ]),
            dimension("position", "岗位描述较清晰。", "medium", []),
        ],
    },
    "YY网络": {
        "aliases": ["YY网络科技", "YY Network"],
        "creditCode": "91110000YY20260002",
        "caseType": "scale_inflated",
        "positionInfo": {"title": "新媒体运营", "salary": "12-18K", "stage": "未融资", "scale": "100-499人"},
        "dimensions": [
            dimension("scale", "招聘规模与参保人数存在明显差异。", "high", [
                signal("scale_gap", "规模真实性存疑", "招聘页显示 100-499 人，公开参保人数为 12 人，存在明显差异。", "企业公开信息（样例数据）", "high", 3, "招聘规模 100-499；参保人数 12", "团队实际规模可能小于招聘页展示。", "建议确认当前团队人数、岗位 HC 是新增还是替补。")
            ]),
            dimension("capital", "资本和成立时间未见明显异常。", "high", []),
            dimension("legal", "未检索到明显法律合规风险。", "high", []),
            dimension("online", "公开评价信息较少。", "medium", [
                signal("limited_feedback", "公开反馈有限", "公开网络反馈数量较少，难以充分判断员工体验。", "网页检索（样例摘要）", "medium", 1, "搜索结果较少", "信息透明度有限时需要通过面试补充核验。", "建议询问团队稳定性和业务现状。", "search")
            ]),
            dimension("position", "岗位描述基本完整。", "medium", []),
        ],
    },
    "ZZ智能": {
        "aliases": ["ZZ人工智能", "ZZ AI"],
        "creditCode": "91110000ZZ20260003",
        "caseType": "legal_risk",
        "positionInfo": {"title": "算法工程师", "salary": "25-40K", "stage": "B轮", "scale": "100-499人"},
        "dimensions": [
            dimension("scale", "规模信息基本可验证。", "high", []),
            dimension("capital", "融资和经营基础公开信息较完整。", "medium", []),
            dimension("legal", "存在较多劳动争议相关记录。", "high", [
                signal("labor_disputes", "劳动争议较多", "近年存在 4 条劳动争议相关记录，建议关注劳动制度与管理规范。", "企业公开信息（样例数据）", "high", 3, "劳动争议 4 条", "劳动争议数量较多，可能反映管理或用工规范需进一步确认。", "建议面试中确认绩效、加班、离职交接和劳动合同条款。"),
                signal("administrative_penalty", "行政处罚记录", "存在 1 条行政处罚记录，需结合处罚性质判断影响。", "企业公开信息（样例数据）", "high", 2, "行政处罚 1 条", "处罚记录不一定直接影响员工体验，但属于需核验信号。", "建议了解公司合规管理和业务资质情况。")
            ]),
            dimension("online", "面试反馈中出现流程拖沓信号。", "medium", [
                signal("negative_interview", "面试反馈偏负面", "公开反馈中重复出现“流程拖沓”“反馈较慢”等标签。", "网页检索（样例摘要）", "medium", 2, "流程拖沓；反馈较慢", "多条相似反馈具有一定参考价值。", "建议确认面试流程、反馈周期和岗位紧急程度。", "search")
            ]),
            dimension("position", "岗位要求较明确。", "medium", []),
        ],
    },
    "AA教育": {
        "aliases": ["AA教育咨询"],
        "creditCode": None,
        "caseType": "insufficient",
        "positionInfo": {"title": "课程顾问", "salary": "8-15K", "stage": "未知", "scale": "少于50人"},
        "dimensions": [
            dimension("online", "公开信息较少。", "low", [
                signal("insufficient_public_info", "公开信息不足", "仅检索到少量基础信息，无法形成稳定判断。", "网页检索（样例摘要）", "low", 0, "搜索结果稀少", "数据覆盖不足时不宜输出明确风险结论。", "建议按自检清单在沟通中逐项核验。", "search")
            ])
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
    "CC传媒": {
        "aliases": ["CC传媒有限公司"],
        "creditCode": "91110000CC20260006",
        "caseType": "high_combo",
        "positionInfo": {"title": "短视频运营", "salary": "15-25K", "stage": "天使轮", "scale": "100-499人"},
        "dimensions": [
            dimension("scale", "招聘规模与公开参保人数差异明显。", "high", [
                signal("scale_gap", "规模真实性存疑", "招聘页显示 100-499 人，公开参保人数为 8 人。", "企业公开信息（样例数据）", "high", 3, "招聘规模 100-499；参保人数 8", "规模差异明显，需确认团队真实性。", "建议确认团队人数、业务线人数和岗位 HC 来源。")
            ]),
            dimension("capital", "成立时间短且实缴资本为 0。", "high", [
                signal("new_company", "成立时间较短", "公司成立不足 1 年，组织稳定性仍需观察。", "企业公开信息（样例数据）", "high", 2, "成立 8 个月", "新成立公司并非必然有问题，但不确定性更高。", "建议确认融资、现金流和团队规划。"),
                signal("zero_paid_capital", "实缴资本较低", "注册资本 1000 万，实缴资本显示为 0。", "企业公开信息（样例数据）", "high", 2, "注册资本 1000 万；实缴 0", "实缴较低可能意味着资金到位情况需进一步核验。", "建议询问薪资发放稳定性和业务收入来源。")
            ]),
            dimension("legal", "暂未发现法律纠纷。", "medium", []),
            dimension("online", "官网与搜索结果较少。", "medium", [
                signal("limited_presence", "公开透明度不足", "官网内容较少，公开网络足迹有限。", "网页检索（样例摘要）", "medium", 1, "官网内容少；搜索结果少", "公开信息少会降低判断置信度。", "建议要求对方清楚说明业务模式和客户来源。", "search")
            ]),
            dimension("position", "岗位薪资偏高且职责偏泛。", "medium", [
                signal("vague_jd", "JD 描述较模糊", "岗位职责以“参与增长”“打造爆款”为主，缺少明确产出和汇报关系。", "招聘页信息（样例数据）", "medium", 1, "职责描述泛化", "职责模糊会增加入职后预期偏差。", "建议确认具体工作内容、考核指标和汇报对象。")
            ]),
        ],
    },
    "DD咨询": {
        "aliases": ["DD管理咨询"],
        "creditCode": "91110000DD20260007",
        "caseType": "position_risk",
        "positionInfo": {"title": "战略分析师", "salary": "30-45K", "stage": "稳定经营", "scale": "100-499人"},
        "dimensions": [
            dimension("scale", "公司规模信息正常。", "high", []),
            dimension("capital", "经营基础较稳定。", "high", []),
            dimension("legal", "未发现明显合规风险。", "high", []),
            dimension("online", "公开反馈正常。", "medium", []),
            dimension("position", "岗位本身存在异常信号。", "medium", [
                signal("long_posting", "岗位长期挂出", "同岗位连续发布超过 6 个月，建议确认是否真实在招。", "招聘页信息（样例数据）", "medium", 2, "连续挂出 7 个月", "长期挂岗可能来自持续扩招，也可能是候选人筛选或虚位。", "建议确认岗位 HC 是新增还是替补、入职时间和历史流失情况。"),
                signal("high_salary", "薪资显著偏高", "该岗位薪资高于同类岗位均值约 45%。", "招聘页信息（样例数据）", "medium", 2, "30-45K；行业均值约 18-28K", "高薪可能包含绩效或高强度要求，需要核验结构。", "建议确认薪资结构、绩效占比和试用期薪资比例。")
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
    {"name": "XX科技", "type": "low_risk", "description": "低风险样例"},
    {"name": "YY网络", "type": "scale_inflated", "description": "规模真实性风险"},
    {"name": "ZZ智能", "type": "legal_risk", "description": "劳动争议较多"},
    {"name": "AA教育", "type": "insufficient", "description": "数据不足兜底"},
    {"name": "CC传媒", "type": "high_combo", "description": "高风险组合"},
    {"name": "DD咨询", "type": "position_risk", "description": "岗位风险突出"},
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
