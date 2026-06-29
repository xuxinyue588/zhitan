const MOCK_ITEMS = [
  { label: '规模真实性', value: 3.2 },
  { label: '资金与成立', value: 2.1 },
  { label: '法律合规', value: 1.5 },
  { label: '网络透明度', value: 3.8 },
  { label: '岗位风险', value: 2.6 },
];

function labelColor(value: number): string {
  if (value <= 3.0) return '#e86a5a';  // 高风险 红
  if (value <= 7.0) return '#e6a817';  // 中风险 黄
  return '#4caf82';                    // 低风险 绿
}
const LABEL_EMOJI: Record<string, string> = {
  '规模真实性': '🏢',
  '资金与成立': '💰',
  '资金稳定性': '💰',
  '法律合规': '⚖️',
  '网络透明度': '🌐',
  '网络存在': '🌐',
  '岗位风险': '💼',
};

function normalizeLabel(label: string): string {
  if (label === '岗位真实性' || label === '岗位风险') return '岗位风险';
  return label;
}

export default function RadarChart({ items }: { items: Array<{ label: string; value: number }> }) {
  const data = (items && items.length > 0 ? items : MOCK_ITEMS).map((item) => ({
    ...item,
    label: normalizeLabel(item.label),
  }));
  const size = 360;
  const center = size / 2;
  const radius = 88;
  const points = data.map((item, index) => {
    const angle = -Math.PI / 2 + (Math.PI * 2 * index) / data.length;
    const valueRadius = radius * (item.value / 5);
    // extra padding for labels that are mostly horizontal (left/right sides)
    const extraPad = Math.abs(Math.cos(angle)) > 0.5 ? 36 : 24;
    return {
      ...item,
      x: center + Math.cos(angle) * valueRadius,
      y: center + Math.sin(angle) * valueRadius,
      lx: center + Math.cos(angle) * (radius + extraPad),
      ly: center + Math.sin(angle) * (radius + extraPad),
      ax: center + Math.cos(angle) * radius,
      ay: center + Math.sin(angle) * radius,
    };
  });
  const polygon = points.map((point) => `${point.x},${point.y}`).join(' ');

  return (
    <section className="panel radar-panel">
      <h2>岗位风险雷达</h2>
      <svg viewBox={`0 0 ${size} ${size}`} className="radar">
        {[0.25, 0.5, 0.75, 1].map((scale) => (
          <polygon key={scale} points={data.map((_, index) => {
            const angle = -Math.PI / 2 + (Math.PI * 2 * index) / data.length;
            return `${center + Math.cos(angle) * radius * scale},${center + Math.sin(angle) * radius * scale}`;
          }).join(' ')} className="radar-grid" />
        ))}
        {points.map((point) => <line key={point.label} x1={center} y1={center} x2={point.ax} y2={point.ay} className="radar-axis" />)}
        <polygon points={polygon} className="radar-area" />
        {points.map((point) => {
          const emoji = LABEL_EMOJI[point.label] ?? '';
          return (
            <text key={point.label} textAnchor="middle" fill={labelColor(point.value)}>
              {emoji && <tspan x={point.lx} y={point.ly - 9} fontSize="13">{emoji}</tspan>}
              <tspan x={point.lx} y={point.ly + (emoji ? 9 : 0)} fontSize="13">{point.label}</tspan>
            </text>
          );
        })}
      </svg>
    </section>
  );
}
