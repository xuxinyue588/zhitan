import type { InterviewQuestion } from '../types/risk';

const typeLabels: Record<string, string> = { verify: '🔍 求证型', probe: '🧭 试探型', decision: '✅ 决策型' };

const THEME_COLOR: Record<string, string> = {
  green:  '#4caf82',
  yellow: '#e6a817',
  red:    '#e86a5a',
  blue:   '#9b7ec8',
};

export default function InterviewQuestions({ questions, theme }: { questions: InterviewQuestion[]; theme?: string }) {
  const accentColor = THEME_COLOR[theme ?? 'green'] ?? '#4caf82';

  async function copy(text: string) {
    if (navigator.clipboard) await navigator.clipboard.writeText(text);
  }

  return (
    <section className="panel">
      <div className="panel-title-row">
        <h2>建议你在沟通中重点确认</h2>
        <button
          type="button"
          style={{ background: 'rgba(255,255,255,0.72)', border: `1.5px solid ${accentColor}`, color: accentColor, borderRadius: '999px', padding: '6px 14px', fontSize: '13px', fontWeight: 600, cursor: 'pointer', backdropFilter: 'blur(4px)' }}
          onClick={() => copy(questions.map((item) => item.question).join('\n'))}
        >一键复制全部</button>
      </div>
      <div className="question-list">
        {questions.map((item) => (
          <article key={item.id}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ flex: 1 }}>
                <span>{typeLabels[item.type] ?? item.type}</span>
                <p>{item.question}</p>
                <small>关联信号：{item.relatedSignal}</small>
              </div>
              <button
                type="button"
                style={{ flexShrink: 0, background: accentColor, color: '#fff', WebkitTextFillColor: '#fff', fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif', border: 0, borderRadius: '999px', padding: '6px 14px', fontSize: '12px', fontWeight: 600, cursor: 'pointer', alignSelf: 'center' }}
                onClick={() => copy(item.question)}
              >复制问题</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
