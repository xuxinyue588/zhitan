export default function Disclaimer({ text, warnings }: { text: string; warnings: string[] }) {
  return (
    <section className="panel disclaimer">
      <h2 style={{ color: '#1a1a2e', WebkitTextFillColor: '#1a1a2e', background: 'none', borderBottom: '1px solid #f0f1f3', paddingBottom: '8px', marginBottom: '8px' }}>数据来源和免责声明</h2>
      {warnings.length > 0 && (
        <div className="warning-box">
          {warnings.map((warning) => <p key={warning}>{warning}</p>)}
        </div>
      )}
      <p>{text}</p>
    </section>
  );
}
