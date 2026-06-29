import type { CompanyShortcut, PositionInfo, QueryType, RiskReport } from '../types/risk';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

export async function fetchCompanies(): Promise<CompanyShortcut[]> {
  const response = await fetch(`${API_BASE}/api/companies`);
  if (!response.ok) {
    throw new Error('样例公司加载失败');
  }
  const data = (await response.json()) as { companies: CompanyShortcut[] };
  return data.companies;
}

export async function queryRisk(query: string, queryType?: QueryType, positionInfo?: PositionInfo): Promise<RiskReport> {
  const response = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, queryType, positionInfo }),
  });
  if (!response.ok) {
    throw new Error('风险侦察失败，请确认后端服务已启动');
  }
  return (await response.json()) as RiskReport;
}
