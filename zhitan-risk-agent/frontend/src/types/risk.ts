export type QueryType = 'company_name' | 'job_link' | 'screenshot';
export type DimensionName = 'scale' | 'capital' | 'legal' | 'online' | 'position';
export type Confidence = 'high' | 'medium' | 'low';
export type RiskLevel = 'low' | 'medium' | 'high' | 'insufficient';
export type QuestionType = 'verify' | 'probe' | 'decision';

export interface PositionInfo {
  title?: string | null;
  salary?: string | null;
  stage?: string | null;
  scale?: string | null;
}

export interface QueryContext {
  queryId: string;
  queryType: QueryType;
  companyName: string;
  standardName?: string | null;
  creditCode?: string | null;
  aliases: string[];
  positionInfo?: PositionInfo | null;
  createdAt: string;
}

export interface RiskSignal {
  type: string;
  title: string;
  description: string;
  source: string;
  sourceType: 'api' | 'search' | 'llm_infer' | 'mock';
  confidence: Confidence;
  fetchedAt: string;
  rawValue?: string | null;
  baseScore: number;
  explanation?: string | null;
  suggestion?: string | null;
}

export interface RiskDimension {
  name: DimensionName;
  riskScore: number;
  confidence: Confidence;
  signals: RiskSignal[];
  summary: string;
}

export interface TopSignal {
  signal: string;
  severity: 'info' | 'warning' | 'critical';
  explanation: string;
  source: string;
  confidence: Confidence;
  suggestion?: string | null;
}

export interface RiskVerdict {
  overallScore: number;
  riskLevel: RiskLevel;
  dataSufficiency: 'sufficient' | 'partial' | 'insufficient';
  topSignals: TopSignal[];
  conflicts: Array<{ dimensions: string[]; description: string }>;
  summary: string;
}

export interface InterviewQuestion {
  id: string;
  type: QuestionType;
  question: string;
  relatedSignal: string;
}

export interface FeedbackTrack {
  type: 'current_employee' | 'former_employee' | 'interviewee';
  title: string;
  tags: string[];
  summary: string;
  count: number;
}

export interface RenderData {
  riskCard: {
    title: string;
    theme: string;
    levelText: string;
    scoreText: string;
    sufficiencyText: string;
    summary: string;
  };
  radar: Array<{ label: string; value: number }>;
  loadingSteps: string[];
}

export interface RiskReport {
  queryContext: QueryContext;
  verdict: RiskVerdict;
  dimensions: RiskDimension[];
  interviewQuestions: InterviewQuestion[];
  feedback: FeedbackTrack[];
  fallbackChecklist: string[];
  quality: { grade: 'excellent' | 'good' | 'poor'; warnings: string[] };
  renderData: RenderData;
  disclaimer: string;
  generatedAt: string;
}

export interface CompanyShortcut {
  name: string;
  type: string;
  description: string;
}
