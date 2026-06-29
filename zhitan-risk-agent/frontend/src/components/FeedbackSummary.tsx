import type { FeedbackTrack } from '../types/risk';

const TITLE_MAP: Record<string, string> = {
  '面试过的人': '面试人员',
};

const ICON_MAP: Record<string, string> = {
  '在职员工': '/bear-employed.png',
  '已离职员工': '/bear-resigned.png',
  '面试过的人': '/bear-interview.gif',
  '面试人员': '/bear-interview.gif',
};

export default function FeedbackSummary({ feedback }: { feedback: FeedbackTrack[] }) {
  return (
    <section className="panel feedback-panel">
      <h2>过来人评价摘要</h2>
      {feedback.map((track) => (
        <article key={track.type}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            {ICON_MAP[track.title] && (
              <img src={ICON_MAP[track.title]} alt="" style={{ height: '40px', width: 'auto' }} />
            )}
            <h3 style={{ margin: 0 }}>{TITLE_MAP[track.title] ?? track.title}</h3>
          </div>
          <div className="tag-row">{track.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
          <p>{track.summary}</p>
          <small>数据基于 {track.count} 条匿名反馈（样例）</small>
        </article>
      ))}
    </section>
  );
}
