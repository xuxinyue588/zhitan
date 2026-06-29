import { useState } from 'react';
import { queryRisk } from './api/client';
import HomePage from './components/HomePage';
import LoadingState from './components/LoadingState';
import ResultPage from './components/ResultPage';
import type { RiskReport } from './types/risk';

export default function App() {
  const [report, setReport] = useState<RiskReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleQuery(query: string) {
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const [result] = await Promise.all([
        queryRisk(query),
        new Promise<void>((resolve) => setTimeout(resolve, 3000)),
      ]);
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <LoadingState />;
  }

  if (report) {
    return <ResultPage report={report} onBack={() => setReport(null)} />;
  }

  return <HomePage onQuery={handleQuery} error={error} />;
}
