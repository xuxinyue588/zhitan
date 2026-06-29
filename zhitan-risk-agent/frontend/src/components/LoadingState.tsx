import { useEffect, useState } from 'react';

const messages = [
  '正在整理公开信息',
  '正在识别可能影响投递判断的风险信号',
  '即将生成你的投递前速览',
];

export default function LoadingState() {
  // track which messages have been checked off (0-indexed)
  const [checkedUpto, setCheckedUpto] = useState(0);

  useEffect(() => {
    // step through each message every 1s: 0→1 at 1s, 1→2 at 2s, done at 3s
    const timers = messages.slice(1).map((_, i) =>
      window.setTimeout(() => setCheckedUpto(i + 1), (i + 1) * 1000)
    );
    return () => timers.forEach(window.clearTimeout);
  }, []);

  return (
    <main className="loading-page">
      <img src="/bear-phone.gif" alt="" className="loading-bear" />
      <div className="loading-msgs">
        {messages.map((msg, i) => (
          <p
            key={msg}
            className={`loading-msg${i === checkedUpto ? ' active' : ''}${i < checkedUpto ? ' done' : ''}`}
          >
            {i <= checkedUpto && <span className="loading-check">✓</span>}
            {msg}...
          </p>
        ))}
      </div>
    </main>
  );
}
