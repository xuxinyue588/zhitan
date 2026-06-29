import type { RiskReport } from '../types/risk';
import Disclaimer from './Disclaimer';
import FeedbackSummary from './FeedbackSummary';
import InterviewQuestions from './InterviewQuestions';
import RadarChart from './RadarChart';
import RiskCard from './RiskCard';
import RiskSignalList from './RiskSignalList';

interface Props {
  report: RiskReport;
  onBack: () => void;
}

export default function ResultPage({ report, onBack }: Props) {
  return (
    <main className="result-page">
      <button className="back-button" type="button" onClick={onBack}>返回重新查询</button>
      <RiskCard report={report} />
      <section className="content-grid">
        <div className="main-column" style={{ alignSelf: 'start' }}>
          <RiskSignalList dimensions={report.dimensions} />
          {report.verdict.riskLevel === 'insufficient' && (
            <section className="panel">
              <h2 style={{ fontFamily: '"Microsoft YaHei","PingFang SC",sans-serif', borderBottom: '1px solid #f0f1f3', paddingBottom: '8px', marginBottom: '8px' }}>投递前自检5问</h2>
              <ol className="checklist">
                {report.fallbackChecklist.map((item) => <li key={item}>{item}</li>)}
              </ol>
            </section>
          )}
          <InterviewQuestions questions={report.interviewQuestions} theme={report.renderData.riskCard.theme} />
        </div>
        <aside className="side-column" style={{ alignSelf: 'start' }}>
          <RadarChart items={report.renderData.radar} />
          <FeedbackSummary feedback={report.feedback} />
        </aside>
      </section>
      <Disclaimer text={report.disclaimer} warnings={report.quality.warnings} />
    </main>
  );
}
