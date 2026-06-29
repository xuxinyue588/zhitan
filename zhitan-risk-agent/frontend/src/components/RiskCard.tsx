import type { RiskReport } from '../types/risk';

// gradient per theme: low=green, medium=yellow, high=red, insufficient=purple
const GRADIENT_MAP: Record<string, string> = {
  green:  'linear-gradient(135deg, #d4f5e2 0%, #e8faf0 100%)',
  yellow: 'linear-gradient(135deg, #fef3cd 0%, #fff8e6 100%)',
  red:    'linear-gradient(135deg, #fde8e8 0%, #fff0f0 100%)',
  blue:   'linear-gradient(135deg, #ede8f8 0%, #f4f0fc 100%)',
};

const BADGE_COLOR: Record<string, string> = {
  green:  '#4caf82',
  yellow: '#e6a817',
  red:    '#e86a5a',
  blue:   '#9b7ec8',
};

// light bg → dark text; dark bg → white text
const TEXT_COLOR: Record<string, string> = {
  green:  '#1a4a30',
  yellow: '#7a5a00',
  red:    '#8b1a1a',
  blue:   '#3a2a6a',
};

const SUB_TEXT_COLOR: Record<string, string> = {
  green:  'rgba(20,60,40,0.65)',
  yellow: 'rgba(100,70,0,0.7)',
  red:    'rgba(100,20,20,0.65)',
  blue:   'rgba(50,30,100,0.65)',
};

export default function RiskCard({ report }: { report: RiskReport }) {
  const card = report.renderData.riskCard;
  const theme = card.theme in GRADIENT_MAP ? card.theme : 'blue';
  const gradient = GRADIENT_MAP[theme];
  const badgeColor = BADGE_COLOR[theme];
  const textColor = TEXT_COLOR[theme];
  const subColor = SUB_TEXT_COLOR[theme];
  const scorePanelBg = 'rgba(0,0,0,0.06)';

  return (
    <section className="risk-card-new" style={{ marginBottom: '20px' }}>
      <div className="risk-header" style={{ background: gradient }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
          <img src="/bear-sitting.png" alt="" style={{ height: '100px', width: 'auto', flexShrink: 0 }} />
          <div>
            <h1 className="risk-company" style={{ color: textColor, margin: '0 0 6px', fontSize: '32px', fontWeight: 700 }}>{card.title}</h1>
            {report.queryContext.positionInfo?.title && (
              <p style={{ margin: 0, color: subColor, fontSize: '17px' }}>
                {report.queryContext.positionInfo.title}
              </p>
            )}
          </div>
        </div>
        <div style={{
          background: scorePanelBg,
          backdropFilter: 'blur(8px)',
          borderRadius: '16px',
          padding: '14px 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <strong style={{ fontSize: '44px', fontWeight: 800, color: textColor, lineHeight: 1 }}>{card.scoreText}</strong>
            <span style={{ fontSize: '12px', color: subColor, marginTop: '4px' }}>风险评分</span>
          </div>
          {theme !== 'blue' && <span style={{
            background: badgeColor,
            color: '#fff',
            borderRadius: '999px',
            padding: '8px 18px',
            fontSize: '14px',
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}>✓ {card.levelText}</span>}
        </div>
      </div>
      {card.summary && (
        <p className="risk-summary-new">{card.summary}</p>
      )}
      {report.verdict.conflicts.length > 0 && (
        <div className="conflict-box">
          {report.verdict.conflicts.map((conflict) => (
            <span key={conflict.description}>{conflict.description}</span>
          ))}
        </div>
      )}
    </section>
  );
}
