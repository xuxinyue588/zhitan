import { useState } from 'react';
import type { RiskDimension } from '../types/risk';

const labels: Record<string, string> = {
  scale: '规模真实性',
  capital: '资金和成立时间',
  legal: '法律合规',
  online: '网络存在和公开反馈',
  position: '岗位风险',
};

const icons: Record<string, string> = {
  scale: '🏢',
  capital: '💰',
  legal: '⚖️',
  online: '🌐',
  position: '💼',
};

function scoreColor(score: number): string {
  if (score <= 3.0) return '#4caf82';
  if (score <= 7.0) return '#e6a817';
  return '#e86a5a';
}

function statusText(score: number): string {
  if (score <= 3.0) return '✓ 无异常';
  if (score <= 7.0) return '⚠ 需关注';
  return '× 高风险';
}

export default function RiskSignalList({ dimensions }: { dimensions: RiskDimension[] }) {
  const [open, setOpen] = useState<string[]>([]);

  function toggle(id: string) {
    setOpen((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);
  }

  return (
    <section className="panel" style={{ padding: 0, overflow: 'hidden' }}>
      <h2 style={{ padding: '16px 20px', margin: 0, borderBottom: '1px solid #f0f1f3' }}>关键风险信号</h2>
      {dimensions.map((dimension, idx) => {
        const color = scoreColor(dimension.riskScore);
        return (
          <div
            key={dimension.name}
            style={{
              padding: '16px 20px',
              borderBottom: idx < dimensions.length - 1 ? '1px solid #f0f1f3' : 'none',
              borderLeft: `4px solid ${color}`,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: '0 0 4px', fontSize: '17px', fontWeight: 700, color: '#1a1a2e', fontFamily: '"Microsoft YaHei","PingFang SC",sans-serif', WebkitTextFillColor: '#1a1a2e', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '18px' }}>{icons[dimension.name]}</span>
                  {labels[dimension.name]}
                </h3>
                <p style={{ margin: '0 0 10px', fontSize: '14px', color: '#666' }}>{dimension.summary}</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {dimension.signals.map((s) => {
                    const id = `${dimension.name}-${s.type}`;
                    const expanded = open.includes(id);
                    return (
                      <div key={id} style={{ display: 'inline-block' }}>
                        <button
                          type="button"
                          onClick={() => toggle(id)}
                          style={{
                            border: `1px solid ${color}`,
                            color,
                            WebkitTextFillColor: color,
                            borderRadius: '999px',
                            padding: '3px 10px',
                            fontSize: '12px',
                            fontWeight: 500,
                            background: 'transparent',
                            cursor: 'pointer',
                            fontFamily: '"Microsoft YaHei","PingFang SC",sans-serif',
                          }}
                        >{s.title} {expanded ? '▴' : '▾'}</button>
                        {expanded && (
                          <div style={{ marginTop: '8px', padding: '10px 14px', background: '#f7f8fa', borderRadius: '10px', fontSize: '13px', color: '#444', lineHeight: 1.7 }}>
                            {s.rawValue && <p style={{ margin: '3px 0' }}><b>原始信息：</b>{s.rawValue}</p>}
                            <p style={{ margin: '3px 0' }}><b>数据来源：</b>{s.source} · {s.fetchedAt} · 置信度 {s.confidence}</p>
                            <p style={{ margin: '3px 0' }}><b>判断逻辑：</b>{s.explanation}</p>
                            <p style={{ margin: '3px 0' }}><b>建议核验：</b>{s.suggestion}</p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
              <div style={{ textAlign: 'right', flexShrink: 0 }}>
                <div style={{ fontSize: '18px', fontWeight: 700, color, fontFamily: '"Microsoft YaHei","PingFang SC",sans-serif', WebkitTextFillColor: color }}>{dimension.riskScore.toFixed(1)} 分</div>
                <div style={{ fontSize: '14px', color, marginTop: '2px', WebkitTextFillColor: color }}>{statusText(dimension.riskScore)}</div>
              </div>
            </div>
          </div>
        );
      })}
    </section>
  );
}
