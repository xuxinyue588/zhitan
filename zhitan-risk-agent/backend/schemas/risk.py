from __future__ import annotations

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

QueryType = Literal["company_name", "job_link", "screenshot"]
DimensionName = Literal["scale", "capital", "legal", "online", "position"]
Confidence = Literal["high", "medium", "low"]
SourceType = Literal["api", "search", "llm_infer", "mock"]
RiskLevel = Literal["low", "medium", "high", "insufficient"]
DataSufficiency = Literal["sufficient", "partial", "insufficient"]
Severity = Literal["info", "warning", "critical"]
QuestionType = Literal["verify", "probe", "decision"]
QualityGrade = Literal["excellent", "good", "poor"]
FeedbackTrackType = Literal["current_employee", "former_employee", "interviewee"]


class PositionInfo(BaseModel):
    title: Optional[str] = None
    salary: Optional[str] = None
    stage: Optional[str] = None
    scale: Optional[str] = None


class QueryContext(BaseModel):
    queryId: str
    queryType: QueryType
    companyName: str
    standardName: Optional[str] = None
    creditCode: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    positionInfo: Optional[PositionInfo] = None
    createdAt: str


class RiskSignal(BaseModel):
    type: str
    title: str
    description: str
    source: str
    sourceType: SourceType
    confidence: Confidence
    fetchedAt: str
    rawValue: Optional[str] = None
    baseScore: float = 0
    explanation: Optional[str] = None
    suggestion: Optional[str] = None


class RiskDimension(BaseModel):
    name: DimensionName
    riskScore: float
    confidence: Confidence
    signals: list[RiskSignal] = Field(default_factory=list)
    summary: str


class TopSignal(BaseModel):
    signal: str
    severity: Severity
    explanation: str
    source: str
    confidence: Confidence
    suggestion: Optional[str] = None


class RiskConflict(BaseModel):
    dimensions: list[str]
    description: str


class RiskVerdict(BaseModel):
    overallScore: float
    riskLevel: RiskLevel
    dataSufficiency: DataSufficiency
    topSignals: list[TopSignal] = Field(default_factory=list)
    conflicts: list[RiskConflict] = Field(default_factory=list)
    summary: str


class InterviewQuestion(BaseModel):
    id: str
    type: QuestionType
    question: str
    relatedSignal: str


class FeedbackTrack(BaseModel):
    type: FeedbackTrackType
    title: str
    tags: list[str]
    summary: str
    count: int


class Quality(BaseModel):
    grade: QualityGrade
    warnings: list[str] = Field(default_factory=list)


class RiskCard(BaseModel):
    title: str
    theme: str
    levelText: str
    scoreText: str
    sufficiencyText: str
    summary: str


class RadarItem(BaseModel):
    label: str
    value: float


class RenderData(BaseModel):
    riskCard: RiskCard
    radar: list[RadarItem]
    loadingSteps: list[str]


class RiskReport(BaseModel):
    queryContext: QueryContext
    verdict: RiskVerdict
    dimensions: list[RiskDimension]
    interviewQuestions: list[InterviewQuestion]
    feedback: list[FeedbackTrack] = Field(default_factory=list)
    fallbackChecklist: list[str] = Field(default_factory=list)
    quality: Quality
    renderData: Optional[RenderData] = None
    disclaimer: str
    generatedAt: str


class QueryRequest(BaseModel):
    query: str
    queryType: Optional[QueryType] = None
    positionInfo: Optional[PositionInfo] = None


class CompanyShortcut(BaseModel):
    name: str
    type: str
    description: str


SampleCompany = dict[str, Any]
