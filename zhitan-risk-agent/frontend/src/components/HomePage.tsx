import { FormEvent, useEffect, useState } from 'react';
import { fetchCompanies } from '../api/client';
import type { CompanyShortcut } from '../types/risk';

interface Props {
  onQuery: (query: string) => void;
  error: string | null;
}

const fallbackCompanies: CompanyShortcut[] = [
  { name: '百度', type: 'low_risk', description: '低风险·成熟大盘' },
  { name: '字节跳动', type: 'organization_instability', description: '节奏快·业务收缩关注' },
  { name: '腾讯', type: 'low_risk', description: '低风险·BG 差异注意' },
  { name: '拼多多', type: 'high_combo', description: '高风险·高强度组合' },
  { name: '阿里', type: 'organization_instability', description: '分拆期·考核激进' },
  { name: '美团', type: 'organization_instability', description: '组织大幅盘整·关注影响面' },
];

export default function HomePage({ onQuery, error }: Props) {
  const [query, setQuery] = useState('');
  const [companies, setCompanies] = useState<CompanyShortcut[]>(fallbackCompanies);

  useEffect(() => {
    fetchCompanies().then(setCompanies).catch(() => setCompanies(fallbackCompanies));
  }, []);

  function submit(event: FormEvent) {
    event.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      onQuery(trimmed);
    }
  }

  return (
    <main className="home-page">
      <section className="hero-card">
        <div className="logo-row">
          <span className="bear-walker" aria-label="职探小熊">
            <img src="/bear-custom.png" alt="" className="logo-mark" />
          </span>
          <span className="logo-text">职探</span>
        </div>
        <p className="eyebrow">投递前风险侦察</p>
        <h1><span className="hd-dark">投简历前，</span><span className="hd-light">先查一查</span></h1>
        <form className="search-card" onSubmit={submit}>
          <textarea
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="输入公司名，如：百度；也可以粘贴岗位链接或上传岗位截图"
            rows={3}
          />
          <div className="search-actions">
            <span>支持公司名 / 岗位链接 / 岗位截图</span>
            <button type="submit" disabled={!query.trim()}>查一查</button>
          </div>
        </form>
        {error && <p className="error-text">{error}</p>}

        <div className="quick-section">
          <p>猜你想搜</p>
          <div className="quick-grid">
            {companies.slice(0, 6).map((company) => (
              <button key={company.name} type="button" onClick={() => onQuery(company.name)}>
                {company.name}
              </button>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}