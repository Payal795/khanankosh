import { Icon } from '../components/Icon';

export function HomePage({ onNavigate }) {
  const modules = [
    {
      page: 'gis',
      title: 'GIS Feasibility',
      desc: 'Analyse land suitability using geological, environmental and spatial parameters. Get automated feasibility scores with AI-driven insights.',
      icon: <Icon.Layers />,
      chipBg: '#e6f4ea',
      badge: 'SPATIAL ANALYSIS',
    },
    {
      page: 'wordcloud',
      title: 'Word Cloud Explorer',
      desc: 'Technical passages are identified from reports and grouped into six mining-related context clusters and these generate the interactive word cloud, linking each term to related information.',
      icon: <Icon.Cloud />,
      chipBg: '#e8f0fe',
      badge: 'WORD CLOUD',
    },
    {
      page: 'qa',
      title: 'Q&A Agent',
      desc: 'Ask questions across organisational reports, historical documents and mining records using intelligent retrieval.',
      icon: <Icon.MessageSquare />,
      chipBg: '#fef7e0',
      badge: 'DOCUMENT INTELLIGENCE',
    },
    {
      page: 'report',
      title: 'Report Generation',
      desc: 'Generate structured reports using verified organisational information, GIS data and AI-assisted synthesis.',
      icon: <Icon.FileText />,
      chipBg: '#fce8e6',
      badge: 'AI GENERATION',
    },
  ];

  const capabilities = [
    { icon: <Icon.Layers />, title: 'GIS Intelligence', desc: 'Spatial analysis of land, geology, vegetation and infrastructure parameters.' },
    { icon: <Icon.Database />, title: 'Document Intelligence', desc: 'OCR, indexing and retrieval across scanned PDFs and historical archives.' },
    { icon: <Icon.Cpu />, title: 'AI-Assisted Analysis', desc: 'Large language model reasoning over verified organisational knowledge bases.' },
    { icon: <Icon.FileText />, title: 'Automated Reporting', desc: 'Structured report generation for parliamentary, administrative and technical use.' },
    { icon: <Icon.Globe />, title: 'Historical Data Retrieval', desc: 'Decades of mining records, geological surveys and production data, indexed and searchable.' },
    { icon: <Icon.BarChart />, title: 'Decision Support', desc: 'Consolidate multi-source intelligence to support mine planning and regulatory decisions.' },
  ];

  const recent = [
    { act: 'GIS Feasibility Assessment', mod: 'GIS', user: 'S. Kumar', time: 'Today 14:32', status: 'COMPLETED' },
    { act: 'Report: Jharia Block Analysis', mod: 'Report', user: 'R. Mishra', time: 'Today 13:15', status: 'GENERATED' },
    { act: 'Q&A: Production data FY2023', mod: 'Q&A', user: 'P. Verma', time: 'Today 12:48', status: 'ANSWERED' },
    { act: 'Map Layer: Vegetation', mod: 'Map', user: 'A. Singh', time: 'Today 11:20', status: 'VIEWED' },
    { act: 'Feasibility Report Export', mod: 'GIS', user: 'R.K. Sharma', time: 'Today 10:55', status: 'EXPORTED' },
  ];

  const systemStatus = [
    { name: 'GIS Engine', status: 'OPERATIONAL', ok: true },
    { name: 'Document Index', status: 'OPERATIONAL', ok: true },
    { name: 'AI Q&A Engine', status: 'OPERATIONAL', ok: true },
    { name: 'Report Generator', status: 'OPERATIONAL', ok: true },
    { name: 'Data Pipeline', status: 'PROCESSING', ok: false },
  ];

  return (
    <div style={{ fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif', color: '#1f2937', background: '#f8fafc', minHeight: '100vh' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Roboto:wght@400;500;700&display=swap');

        .mi-condensed {
          font-family: 'Oswald', 'Arial Narrow', sans-serif;
          letter-spacing: 0.02em;
          text-transform: uppercase;
        }

        /* Subtle Fade In Animations */
        @keyframes miFadeUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .mi-animate-hero {
          animation: miFadeUp 0.8s ease-out forwards;
        }

        .mi-hero-layout {
          max-width: 1300px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: minmax(0, 1.35fr) minmax(260px, 0.8fr);
          gap: 48px;
          align-items: center;
        }

        .mi-hero-title {
          margin: 0 0 16px;
          font-size: 3.8rem;
          font-weight: 700;
          line-height: 1.1;
        }

        .mi-hero-title span {
          display: block;
          color: #ffb703;
        }

        .mi-hero-description {
          max-width: 720px;
          margin: 0 0 24px;
          color: #dbe4ee;
          font-size: 1rem;
          line-height: 1.65;
        }

        .mi-hero-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
        }

        .mi-mining-scene {
          position: relative;
          height: 220px;
          overflow: hidden;
          border: 1px solid rgba(255, 255, 255, 0.14);
          border-radius: 4px;
          background: linear-gradient(160deg, rgba(42, 86, 76, 0.5), rgba(7, 24, 43, 0.72));
        }

        .mi-scene-ridge {
          position: absolute;
          bottom: 52px;
          width: 78%;
          height: 120px;
          clip-path: polygon(0 100%, 18% 52%, 32% 73%, 55% 18%, 76% 61%, 90% 38%, 100% 100%);
          background: #43534e;
        }

        .mi-scene-ridge-back {
          right: -8%;
          bottom: 62px;
          opacity: 0.55;
          transform: scale(0.82);
        }

        .mi-scene-ridge-front {
          left: -14%;
          background: #566058;
        }

        .mi-scene-ground {
          position: absolute;
          right: 0;
          bottom: 0;
          left: 0;
          height: 62px;
          background: linear-gradient(180deg, #4b5149, #292f2d);
          border-top: 2px solid #d89b43;
        }

        .mi-haul-truck {
          position: absolute;
          z-index: 2;
          bottom: 35px;
          left: 24%;
          width: 190px;
          height: 82px;
          animation: miTruckTravel 5s ease-in-out infinite alternate;
        }

        .mi-truck-bed {
          position: absolute;
          bottom: 28px;
          left: 0;
          width: 124px;
          height: 42px;
          clip-path: polygon(0 0, 84% 0, 100% 100%, 8% 100%);
          border-top: 4px solid #d99a43;
          background: #b86d27;
        }

        .mi-truck-cab {
          position: absolute;
          right: 3px;
          bottom: 28px;
          width: 64px;
          height: 54px;
          clip-path: polygon(0 25%, 55% 0, 100% 18%, 100% 100%, 0 100%);
          background: #d89237;
        }

        .mi-truck-window {
          position: absolute;
          right: 11px;
          bottom: 52px;
          width: 27px;
          height: 19px;
          clip-path: polygon(0 22%, 78% 0, 100% 100%, 0 100%);
          background: #b8d4d3;
        }

        .mi-coal-piece {
          position: absolute;
          bottom: 65px;
          z-index: 1;
          width: 22px;
          height: 15px;
          border-radius: 55% 45% 30% 40%;
          background: #252a2c;
          transform: rotate(-12deg);
        }

        .mi-coal-piece:nth-of-type(1) { left: 27px; }
        .mi-coal-piece:nth-of-type(2) { left: 48px; bottom: 68px; width: 19px; height: 13px; transform: rotate(18deg); }
        .mi-coal-piece:nth-of-type(3) { left: 69px; bottom: 64px; width: 24px; height: 16px; transform: rotate(-5deg); }

        .mi-truck-wheel {
          position: absolute;
          bottom: 9px;
          width: 29px;
          height: 29px;
          border: 5px solid #171e22;
          border-radius: 50%;
          background: #dbe4e4;
          box-shadow: inset 0 0 0 4px #68777a;
          animation: miWheelSpin 2.2s linear infinite;
        }

        .mi-truck-wheel-front { right: 12px; }
        .mi-truck-wheel-back { left: 36px; }

        .mi-road-mark {
          position: absolute;
          right: 8%;
          bottom: 27px;
          width: 25%;
          height: 3px;
          background: repeating-linear-gradient(90deg, #f2c26b 0 16px, transparent 16px 28px);
          animation: miRoadMove 1.2s linear infinite;
        }

        @keyframes miTruckTravel {
          from { transform: translateX(-10px) translateY(0); }
          to { transform: translateX(12px) translateY(-2px); }
        }

        @keyframes miWheelSpin {
          to { transform: rotate(360deg); }
        }

        @keyframes miRoadMove {
          to { background-position: -28px 0; }
        }

        @media (max-width: 760px) {
          .mi-hero-layout { grid-template-columns: 1fr; gap: 24px; }
          .mi-home-hero { padding: 36px 22px 40px !important; }
          .mi-mining-scene { height: 150px; }
          .mi-hero-title { font-size: 2.9rem; }
          .mi-haul-truck { transform: scale(0.82); transform-origin: left bottom; }
        }

        @media (prefers-reduced-motion: reduce) {
          .mi-animate-hero, .mi-haul-truck, .mi-truck-wheel, .mi-road-mark { animation: none; }
        }

        /* Hero Buttons */
        .mi-btn-hero-primary {
          background-color: #1e7e34;
          color: #ffffff;
          border: none;
          font-family: 'Oswald', sans-serif;
          font-weight: 600;
          font-size: 0.9rem;
          letter-spacing: 0.08em;
          padding: 12px 28px;
          border-radius: 2px;
          cursor: pointer;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }
        .mi-btn-hero-primary:hover {
          background-color: #156227;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }

        .mi-btn-hero-outline {
          background-color: transparent;
          color: #ffffff;
          border: 1px solid rgba(255, 255, 255, 0.4);
          font-family: 'Oswald', sans-serif;
          font-weight: 600;
          font-size: 0.9rem;
          letter-spacing: 0.08em;
          padding: 12px 28px;
          border-radius: 2px;
          cursor: pointer;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .mi-btn-hero-outline:hover {
          border-color: #ffffff;
          background-color: rgba(255, 255, 255, 0.08);
          transform: translateY(-1px);
        }

        /* Card Button with Icon Push */
        .mi-btn-navy {
          background-color: #0d2247;
          color: #ffffff;
          border: none;
          font-family: 'Oswald', sans-serif;
          font-weight: 600;
          font-size: 0.85rem;
          letter-spacing: 0.08em;
          padding: 10px;
          border-radius: 2px;
          width: 100%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          transition: all 0.2s ease;
        }
        .mi-btn-navy:hover {
          background-color: #081733;
        }
        .mi-btn-navy:hover .mi-arrow {
          transform: translateX(4px);
        }
        .mi-arrow {
          transition: transform 0.2s ease;
          display: inline-block;
        }

        /* Interactive Module Cards */
        .mi-module-card {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 4px;
          padding: 24px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
          transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .mi-module-card:hover {
          transform: translateY(-4px);
          border-color: #cbd5e1;
          box-shadow: 0 12px 24px -6px rgba(13, 34, 71, 0.12);
        }

        /* Table Row Hover */
        .mi-table-row {
          transition: background-color 0.15s ease;
        }
        .mi-table-row:hover {
          background-color: #f8fafc;
        }

        /* Capability Card Hover */
        .mi-capability-card {
          background: #f8fafc;
          border-left: 3px solid #0d2247;
          padding: 20px;
          border-radius: 0 4px 4px 0;
          transition: all 0.2s ease;
        }
        .mi-capability-card:hover {
          background: #ffffff;
          box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
          border-left-color: #1e7e34;
        }
      `}</style>

      {/* Hero Header with Green to Blue Gradient */}
      <div
        className="mi-animate-hero mi-home-hero"
        style={{
          background: 'linear-gradient(135deg, #09261a 0%, #0c3e38 35%, #0d2847 75%, #081733 100%)',
          padding: '56px 48px 60px',
          color: '#ffffff',
          position: 'relative',
        }}
      >
        <div className="mi-hero-layout">
          <div className="mi-hero-copy">
            <h1 className="mi-condensed mi-hero-title">
              Welcome to
              <span lang="hi">खनन Kosh</span>
            </h1>

            <p className="mi-hero-description">
              खनन Kosh is an AI-powered decision-support platform that centralizes mining data from CMPDI and CIL subsidiaries, enabling intelligent analysis and evidence-backed insights for informed decision-making.
            </p>

            <div className="mi-hero-actions">
              <button className="mi-btn-hero-primary" onClick={() => onNavigate('gis')}>
                EXPLORE PLATFORM
              </button>
              <button className="mi-btn-hero-outline" onClick={() => onNavigate('intro')}>
                PLATFORM OVERVIEW
              </button>
            </div>
          </div>

          <div className="mi-mining-scene" role="img" aria-label="Animated haul truck carrying coal across a mine road">
            <div className="mi-scene-ridge mi-scene-ridge-back" />
            <div className="mi-scene-ridge mi-scene-ridge-front" />
            <div className="mi-scene-ground" />
            <div className="mi-haul-truck">
              <div className="mi-coal-piece" />
              <div className="mi-coal-piece" />
              <div className="mi-coal-piece" />
              <div className="mi-truck-bed" />
              <div className="mi-truck-cab" />
              <div className="mi-truck-window" />
              <div className="mi-truck-wheel mi-truck-wheel-back" />
              <div className="mi-truck-wheel mi-truck-wheel-front" />
            </div>
            <div className="mi-road-mark" />
          </div>
        </div>
      </div>

      {/* Platform Modules */}
      <div style={{ padding: '48px 48px 56px' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div style={{ marginBottom: 24 }}>
            <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em' }}>
              PLATFORM MODULES
            </div>
            <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: '4px 0 0', fontWeight: 700 }}>
              Integrated Intelligence Modules
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20 }}>
            {modules.map((mod) => (
              <div key={mod.page} className="mi-module-card">
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                    {/* Perfectly Centered Flexbox Icon Box */}
                    <div
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: 4,
                        background: mod.chipBg,
                        color: '#1f2937',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                        {mod.icon}
                      </div>
                    </div>
                    <span
                      className="mi-condensed"
                      style={{
                        background: '#f1f5f9',
                        color: '#475569',
                        fontSize: '0.65rem',
                        fontWeight: 600,
                        padding: '3px 8px',
                        borderRadius: 2,
                        letterSpacing: '0.06em',
                      }}
                    >
                      {mod.badge}
                    </span>
                  </div>

                  <h3 className="mi-condensed" style={{ fontSize: '1.25rem', color: '#0d2247', margin: '0 0 10px', fontWeight: 700 }}>
                    {mod.title}
                  </h3>
                  <p style={{ color: '#64748b', fontSize: '0.85rem', lineHeight: 1.5, margin: 0 }}>
                    {mod.desc}
                  </p>
                </div>

                <button className="mi-btn-navy" style={{ marginTop: 28 }} onClick={() => onNavigate(mod.page)}>
                  OPEN MODULE <span className="mi-arrow">&rarr;</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Architecture / Capabilities */}
      <div style={{ padding: '48px 48px 56px', background: '#ffffff', borderTop: '1px solid #e2e8f0', borderBottom: '1px solid #e2e8f0' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div style={{ marginBottom: 24 }}>
            <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em' }}>
              SYSTEM ARCHITECTURE
            </div>
            <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: '4px 0 0', fontWeight: 700 }}>
              Platform Capabilities
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {capabilities.map((cap) => (
              <div key={cap.title} className="mi-capability-card">
                <div style={{ color: '#0d2247', marginBottom: 12, display: 'flex', alignItems: 'center' }}>
                  {cap.icon}
                </div>
                <h4 className="mi-condensed" style={{ fontSize: '1.1rem', color: '#0d2247', margin: '0 0 6px', fontWeight: 700 }}>
                  {cap.title}
                </h4>
                <p style={{ color: '#64748b', fontSize: '0.85rem', lineHeight: 1.5, margin: 0 }}>
                  {cap.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dashboard Section */}
      <div style={{ padding: '48px 48px 64px' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 340px', gap: 24 }}>
          {/* Table Container */}
          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 4, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 className="mi-condensed" style={{ fontSize: '1.2rem', color: '#0d2247', margin: 0, fontWeight: 700 }}>
                Recent Platform Activity
              </h3>
              <button
                className="mi-condensed"
                style={{
                  background: 'transparent',
                  border: '1px solid #0d2247',
                  color: '#0d2247',
                  padding: '5px 14px',
                  borderRadius: 2,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                VIEW ALL
              </button>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                  {['ACTIVITY', 'MODULE', 'USER', 'TIME', 'STATUS'].map((h) => (
                    <th
                      key={h}
                      className="mi-condensed"
                      style={{
                        textAlign: 'left',
                        padding: '8px 10px',
                        color: '#64748b',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {recent.map((row, i) => (
                  <tr key={i} className="mi-table-row" style={{ borderBottom: i < recent.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                    <td style={{ padding: '12px 10px', color: '#1f2937', fontWeight: 500 }}>{row.act}</td>
                    <td style={{ padding: '12px 10px' }}>
                      <span
                        className="mi-condensed"
                        style={{
                          background: '#e8f0fe',
                          color: '#1a73e8',
                          fontSize: '0.68rem',
                          fontWeight: 600,
                          padding: '3px 8px',
                          borderRadius: 2,
                        }}
                      >
                        {row.mod}
                      </span>
                    </td>
                    <td style={{ padding: '12px 10px', color: '#64748b' }}>{row.user}</td>
                    <td style={{ padding: '12px 10px', color: '#64748b' }}>{row.time}</td>
                    <td style={{ padding: '12px 10px' }}>
                      <span
                        className="mi-condensed"
                        style={{
                          background: '#e6f4ea',
                          color: '#137333',
                          fontSize: '0.68rem',
                          fontWeight: 700,
                          padding: '3px 8px',
                          borderRadius: 2,
                        }}
                      >
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Side Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* System Status */}
            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 4, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
              <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 16 }}>
                SYSTEM STATUS
              </div>
              {systemStatus.map((item, idx) => (
                <div
                  key={item.name}
                  style={{
                    display: 'flex',
                    justify: 'space-between',
                    alignItems: 'center',
                    padding: '8px 0',
                    borderBottom: idx < systemStatus.length - 1 ? '1px solid #f1f5f9' : 'none',
                  }}
                >
                  <span style={{ fontSize: '0.85rem', color: '#1f2937', fontWeight: 500 }}>{item.name}</span>
                  <span
                    className="mi-condensed"
                    style={{
                      background: item.ok ? '#e6f4ea' : '#fef7e0',
                      color: item.ok ? '#137333' : '#b06000',
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      padding: '3px 8px',
                      borderRadius: 2,
                    }}
                  >
                    {item.status}
                  </span>
                </div>
              ))}
            </div>

            {/* Support Widget */}
            <div style={{ background: 'linear-gradient(135deg, #0d2247 0%, #081733 100%)', borderRadius: 4, padding: 20, color: '#ffffff' }}>
              <div className="mi-condensed" style={{ color: '#00e676', fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 8 }}>
                NEED HELP?
              </div>
              <p style={{ fontSize: '0.85rem', color: '#cbd5e1', margin: '0 0 16px', lineHeight: 1.5 }}>
                Access the Q&A Agent for platform guidance or contact IT support.
              </p>
              <button className="mi-btn-hero-primary" style={{ width: '100%', padding: '10px' }} onClick={() => onNavigate('qa')}>
                OPEN Q&A AGENT
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}