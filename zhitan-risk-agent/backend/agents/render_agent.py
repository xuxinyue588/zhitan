from __future__ import annotations

from schemas.risk import RadarItem, RenderData, RiskCard, RiskReport

LABELS = {
    "scale": "规模真实性",
    "capital": "资金稳定性",
    "legal": "法律合规",
    "online": "网络透明度",
    "position": "岗位真实性",
}

LEVEL_TEXT = {
    "low": "低风险",
    "medium": "中风险",
    "high": "高风险",
    "insufficient": "数据不足",
}

THEMES = {
    "low": "green",
    "medium": "yellow",
    "high": "red",
    "insufficient": "blue",
}


def render_report(report: RiskReport) -> RiskReport:
    level = report.verdict.riskLevel
    report.renderData = RenderData(
        riskCard=RiskCard(
            title=report.queryContext.standardName or report.queryContext.companyName,
            theme=THEMES[level],
            levelText=LEVEL_TEXT[level],
            scoreText="数据不足" if level == "insufficient" else f"{report.verdict.overallScore:.1f} / 10",
            sufficiencyText={"sufficient": "数据较充分", "partial": "部分信号来源有限", "insufficient": "公开信息不足"}[report.verdict.dataSufficiency],
            summary=report.verdict.summary,
        ),
        radar=[RadarItem(label=LABELS[item.name], value=min(5, max(0, item.riskScore))) for item in report.dimensions],
        loadingSteps=["正在整理公开信息...", "正在识别可能影响投递判断的风险信号...", "即将生成你的投递前速览..."],
    )
    return report
