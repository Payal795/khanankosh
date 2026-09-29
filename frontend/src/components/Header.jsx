import React, { useState } from 'react';
import { Icon } from './Icon';
import khananKoshLogo from '../../Public/khanan khosh logo.png';

const HomeIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M3 11.5 12 4l9 7.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M5 10v9a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1v-9" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const InfoIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="9" />
    <line x1="12" y1="11" x2="12" y2="16" strokeLinecap="round" />
    <circle cx="12" cy="8" r="0.5" fill="currentColor" />
  </svg>
);
const BellIcon = () => (
  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M13.7 21a2 2 0 0 1-3.4 0" strokeLinecap="round" />
  </svg>
);
const ChevronDownIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
    <path d="m6 9 6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const navItems = [
  { page: 'home', label: 'Home', icon: <HomeIcon /> },
  { page: 'intro', label: 'Introduction', icon: <InfoIcon /> },
  
  { page: 'gis', label: 'GIS Feasibility', icon: <Icon.Layers /> },
  { page: 'qa', label: 'Q&A Agent', icon: <Icon.MessageSquare /> },
  { page: 'report', label: 'Report Generation', icon: <Icon.FileText /> },
  { page: 'wordcloud', label: 'Word Cloud', icon: <Icon.Cloud /> },
];

export function Header({ currentPage, onNavigate, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogoClick = () => {
    if (onNavigate) {
      onNavigate('home');
    }
    // Forces clean reset to root origin without hash or query params
    window.location.href = window.location.origin + window.location.pathname;
  };

  return (
    <header
      style={{
        background: 'linear-gradient(90deg, #05101e 0%, #091b31 50%, #05101e 100%)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        padding: '0 28px',
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        height: 68,
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        position: 'relative',
        zIndex: 50,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      }}
    >
      {/* Brand logo */}
      <div
        style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer', flexShrink: 0 }}
        onClick={handleLogoClick}
        title="Go to Home"
      >
        <img
          src={khananKoshLogo}
          alt="खनन Kosh logo"
          style={{ width: 42, height: 42, objectFit: 'contain', flexShrink: 0 }}
        />
        <div>
          <div
            style={{
              color: '#ffffff',
              fontWeight: 700,
              fontSize: '1.02rem',
              lineHeight: 1.1,
              letterSpacing: '-0.01em',
            }}
          >
            खनन Kosh
          </div>
          <div style={{ color: '#94a3b8', fontSize: '0.66rem', lineHeight: 1.1, marginTop: 3, fontWeight: 400 }}>
            Mining Intelligence Platform
          </div>
        </div>
      </div>

      {/* Centered Navigation */}
      <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, flex: 1 }}>
        {navItems.map((item) => {
          const active = currentPage === item.page;
          return (
            <button
              key={item.page}
              onClick={() => onNavigate(item.page)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justify: 'center',
                gap: 8,
                minWidth: 140,
                height: 38,
                borderRadius: 6,
                background: active ? 'rgba(30, 126, 52, 0.22)' : 'rgba(255, 255, 255, 0.04)',
                border: active ? '1px solid #00e676' : '1px solid rgba(255, 255, 255, 0.08)',
                color: active ? '#ffffff' : '#cbd5e1',
                fontSize: '0.82rem',
                fontWeight: active ? 600 : 400,
                letterSpacing: '0.01em',
                cursor: 'pointer',
                transition: 'all 0.15s ease-in-out',
                boxShadow: active ? '0 0 10px rgba(0, 230, 118, 0.15)' : 'none',
                boxSizing: 'border-box',
                padding: '0 12px',
              }}
              onMouseEnter={(e) => {
                if (!active) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.18)';
                  e.currentTarget.style.color = '#ffffff';
                }
              }}
              onMouseLeave={(e) => {
                if (!active) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                  e.currentTarget.style.color = '#cbd5e1';
                }
              }}
            >
              <span style={{ display: 'flex', width: 15, height: 15, color: active ? '#00e676' : '#94a3b8', flexShrink: 0 }}>
                {item.icon}
              </span>
              <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      {/* Right User Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexShrink: 0 }}>
        {/* Bell Notifications */}
        <button
          style={{
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 6,
            width: 38,
            height: 38,
            color: '#cbd5e1',
            cursor: 'pointer',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justify: 'center',
            transition: 'all 0.15s ease',
          }}
          aria-label="Notifications"
          onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)')}
        >
          <BellIcon />
          <span
            style={{
              position: 'absolute',
              top: 7,
              right: 7,
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: '#00e676',
              boxShadow: '0 0 6px #00e676',
            }}
          />
        </button>

        {/* User Profile Box */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setMenuOpen((v) => !v)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              height: 38,
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: 6,
              padding: '0 12px 0 8px',
              cursor: 'pointer',
              color: '#ffffff',
              fontSize: '0.85rem',
              fontWeight: 500,
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)')}
          >
            <span
              style={{
                width: 24,
                height: 24,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #1e7e34 0%, #156227 100%)',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justify: 'center',
                fontSize: '0.75rem',
                fontWeight: 700,
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
              }}
            >
              RK
            </span>
            <span>R.K. Sharma</span>
            <span style={{ color: '#94a3b8', display: 'flex', marginLeft: 2 }}><ChevronDownIcon /></span>
          </button>

          {menuOpen && (
            <div
              style={{
                position: 'absolute',
                top: 'calc(100% + 8px)',
                right: 0,
                background: '#0d2247',
                borderRadius: 6,
                boxShadow: '0 12px 28px rgba(0, 0, 0, 0.35)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                minWidth: 160,
                overflow: 'hidden',
                zIndex: 100,
              }}
            >
              <button
                onClick={() => {
                  setMenuOpen(false);
                  if (onLogout) onLogout();
                }}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  padding: '10px 14px',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#cbd5e1',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                  e.currentTarget.style.color = '#ffffff';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'none';
                  e.currentTarget.style.color = '#cbd5e1';
                }}
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export function IntroPage({ currentPage = 'intro', onNavigate = () => {}, onLogout = () => {} }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  const workflow = [
    { step: 'Data Sources', desc: 'Scanned PDFs, GIS layers, satellite data, historical records', color: '#0d2247' },
    { step: 'Document Processing / OCR', desc: 'Automated extraction, digitisation and structuring of unstructured documents', color: '#10325e' },
    { step: 'Knowledge & GIS Layer', desc: 'Indexed vector database with spatial layers and document embeddings', color: '#1e7e34' },
    { step: 'AI Analysis Engine', desc: 'Large language model reasoning over verified knowledge bases', color: '#156227' },
    { step: 'Q&A / Feasibility / Reports', desc: 'User-facing modules for querying, assessment and report generation', color: '#b06000' },
    { step: 'Decision Support', desc: 'Evidence-backed outputs for mine planning, administration and compliance', color: '#9a3412' },
  ];

  const sources = [
    { icon: <Icon.FileText />, label: 'Scanned PDFs', desc: 'Historical geological reports, survey documents and administrative records' },
    { icon: <Icon.Database />, label: 'Digital Reports', desc: 'Production reports, environmental assessments and technical analyses' },
    { icon: <Icon.BarChart />, label: 'Spreadsheets', desc: 'Production data, financial records and operational metrics' },
    { icon: <Icon.Globe />, label: 'GIS / Spatial Data', desc: 'Satellite imagery, topographic maps and geospatial layers' },
    { icon: <Icon.Layers />, label: 'Mining Records', desc: 'Block-level data, mine plans and operational histories' },
    { icon: <Icon.Database />, label: 'Historical Archives', desc: 'Decades of institutional knowledge and legacy documentation' },
  ];

  const capabilities = [
    {
      title: 'Automated GIS Land Feasibility Scoring',
      desc: 'Multi-parameter spatial analysis for evaluating mining feasibility and terrain constraints.',
      details: 'Integrates slope analysis, land use overlay, environmental buffers, and soil stability models to output real-time site scores.',
    },
    {
      title: 'Natural Language Document Q&A',
      desc: 'Query thousands of geological reports and historical mining records instantly.',
      details: 'Powered by RAG to ground AI responses directly in internal archive PDFs with exact line references.',
    },
    {
      title: 'AI-Assisted Report Generation',
      desc: 'Automated synthesis of feasibility studies with integrated citations.',
      details: 'Drafts comprehensive technical reports with executive summaries, data tables, and verifiable document source links.',
    },
    {
      title: 'Interactive Spatial Mapping',
      desc: 'Dynamic map canvas with layered geological and environmental datasets.',
      details: 'Overlay satellite imagery, borehole locations, mine boundary polygons, and administrative boundaries seamlessly.',
    },
    {
      title: 'OCR & Intelligent Document Processing',
      desc: 'Extract structured information from legacy scanned paper records.',
      details: 'High-accuracy OCR tuned for technical mining terminology, extracting tables, handwritten notes, and vintage survey maps.',
    },
    {
      title: 'Parliamentary & Admin Response Support',
      desc: 'Draft precise responses for legislative inquiries and compliance audits.',
      details: 'Cross-references historical parliamentary questions with live operational database metrics to generate structured drafts.',
    },
    {
      title: 'Production Data & Trend Analytics',
      desc: 'Identify operational trends and output anomalies across multiple mine sites.',
      details: 'Provides predictive yield modeling, historical production comparison, and real-time dashboard visualization.',
    },
    {
      title: 'Satellite Geospatial Data Integration',
      desc: 'Continuous monitoring using multi-spectral satellite imagery layers.',
      details: 'Tracks land subsidence, vegetation loss, surface water changes, and operational footprint expansion over time.',
    },
  ];

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const leftCapabilities = capabilities.filter((_, i) => i % 2 === 0);
  const rightCapabilities = capabilities.filter((_, i) => i % 2 !== 0);

  return (
    <div style={{ fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif', color: '#1f2937', background: '#f8fafc', minHeight: '100vh', width: '100%', overflowX: 'hidden' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Roboto:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

        .mi-condensed {
          font-family: 'Oswald', 'Arial Narrow', sans-serif;
          letter-spacing: 0.02em;
          text-transform: uppercase;
        }

        @keyframes miFadeUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @keyframes miSwishCurtain {
          0% {
            clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
            opacity: 0;
            transform: translateX(-30px);
          }
          30% { opacity: 0.6; }
          100% {
            clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
            opacity: 1;
            transform: translateX(0);
          }
        }

        .mi-animate-hero { animation: miFadeUp 0.8s ease-out forwards; }
        .mi-swish-container {
          animation: miSwishCurtain 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
          animation-delay: 0.2s;
          will-change: clip-path, transform, opacity;
        }

        .mi-card {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 4px;
          padding: 24px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
          transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .mi-card:hover {
          transform: translateY(-3px);
          border-color: #cbd5e1;
          box-shadow: 0 12px 24px -6px rgba(13, 34, 71, 0.1);
        }

        .mi-problem-item {
          display: flex;
          gap: 12px;
          align-items: flex-start;
          padding: 8px 10px;
          border-radius: 4px;
          transition: background-color 0.15s ease;
        }
        .mi-problem-item:hover { background-color: #fef2f2; }

        .mi-workflow-card {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          padding: 20px 14px;
          display: flex;
          flex-direction: column;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
          transition: all 0.2s ease;
          height: 220px;
          box-sizing: border-box;
          position: relative;
        }
        .mi-workflow-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.08);
          border-color: #cbd5e1;
        }
      `}</style>

      {/* Global Header */}
      <Header currentPage={currentPage} onNavigate={onNavigate} onLogout={onLogout} />

      {/* Hero Header */}
      <div
        className="mi-animate-hero"
        style={{
          background: 'linear-gradient(135deg, #09261a 0%, #0c3e38 35%, #0d2847 75%, #081733 100%)',
          padding: '72px 48px 48px',
          color: '#ffffff',
        }}
      >
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div className="mi-condensed" style={{ color: '#00e676', fontSize: '0.85rem', fontWeight: 600, letterSpacing: '0.1em', marginBottom: 12 }}>
            PLATFORM OVERVIEW
          </div>
          <h1 className="mi-condensed" style={{ fontSize: '2.8rem', fontWeight: 700, margin: '0 0 16px', lineHeight: 1.1 }}>
            Integrated Mining Intelligence Platform
          </h1>
          <p style={{ color: '#cbd5e1', fontSize: '1rem', lineHeight: 1.65, maxWidth: 660, margin: 0 }}>
            A purpose-built AI system for CMPDI and Coal India Limited, designed to bring institutional knowledge, spatial intelligence and AI-assisted reasoning together in one unified platform.
          </p>
        </div>
      </div>

      {/* Solution vs Problem Grid */}
      <div style={{ padding: '56px 48px', background: '#ffffff', borderBottom: '1px solid #e2e8f0' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32 }}>
            <div style={{ background: '#f8fafc', borderLeft: '4px solid #1e7e34', borderTop: '1px solid #e2e8f0', borderRight: '1px solid #e2e8f0', borderBottom: '1px solid #e2e8f0', borderRadius: '0 6px 6px 0', padding: 32 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em' }}>CORE ARCHITECTURE</div>
                <span className="mi-condensed" style={{ background: '#e6f4ea', color: '#137333', fontSize: '0.65rem', padding: '3px 8px', borderRadius: 2, fontWeight: 700 }}>SOLUTION OVERVIEW</span>
              </div>
              <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: '0 0 16px', fontWeight: 700 }}>What is this Platform?</h2>
              <p style={{ color: '#475569', lineHeight: 1.7, fontSize: '0.925rem', marginBottom: 16 }}>The CMPDI Intelligent Mining Platform is an enterprise-grade AI decision-support system built specifically for the needs of Coal India Limited and its subsidiary CMPDI.</p>
              <p style={{ color: '#475569', lineHeight: 1.7, fontSize: '0.925rem', margin: 0 }}>The system ingests decades of organisational knowledge and makes this information instantly accessible through natural language interaction.</p>
            </div>

            <div style={{ background: '#fff5f5', borderLeft: '4px solid #dc2626', borderTop: '1px solid #fee2e2', borderRight: '1px solid #fee2e2', borderBottom: '1px solid #fee2e2', borderRadius: '0 6px 6px 0', padding: 32 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <div className="mi-condensed" style={{ color: '#dc2626', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em' }}>OPERATIONAL CHALLENGES</div>
                <span className="mi-condensed" style={{ background: '#fee2e2', color: '#b91c1c', fontSize: '0.65rem', padding: '3px 8px', borderRadius: 2, fontWeight: 700 }}>PROBLEM STATEMENT</span>
              </div>
              <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: '0 0 16px', fontWeight: 700 }}>Why was this Built?</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {[
                  'Thousands of geological reports locked in paper archives',
                  'Manual, time-consuming GIS feasibility assessments',
                  'Information silos across departments',
                  'Difficulty extracting specific data for administrative reports',
                  'No unified interface to query historical mining data',
                ].map((item, i) => (
                  <div key={i} className="mi-problem-item">
                    <div style={{ width: 18, height: 18, background: '#fca5a5', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 1 }}>
                      <span style={{ color: '#7f1d1d', fontSize: '0.7rem', fontWeight: 800 }}>!</span>
                    </div>
                    <p style={{ color: '#475569', fontSize: '0.85rem', lineHeight: 1.45, margin: 0 }}>{item}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Workflow */}
      <div style={{ padding: '56px 48px', background: '#f8fafc' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div style={{ marginBottom: 28 }}>
            <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}>HOW IT WORKS</div>
            <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: 0, fontWeight: 700 }}>Platform Workflow</h2>
          </div>
          <div className="mi-swish-container" style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 24, width: '100%', position: 'relative' }}>
            {workflow.map((w, i) => (
              <div key={i} style={{ position: 'relative' }}>
                <div className="mi-workflow-card">
                  <div style={{ marginBottom: 12 }}>
                    <span className="mi-condensed" style={{ background: w.color, color: '#ffffff', width: 34, height: 34, borderRadius: '50%', fontWeight: 700, fontSize: '0.8rem', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 5px rgba(0,0,0,0.12)' }}>
                      {String(i + 1).padStart(2, '0')}
                    </span>
                  </div>
                  <div className="mi-condensed" style={{ fontWeight: 700, color: w.color, fontSize: '0.92rem', lineHeight: 1.25, marginBottom: 8 }}>{w.step}</div>
                  <div style={{ color: '#64748b', fontSize: '0.78rem', lineHeight: 1.45 }}>{w.desc}</div>
                </div>
                {i < workflow.length - 1 && (
                  <div style={{ position: 'absolute', right: -17, top: '50%', transform: 'translateY(-50%)', color: '#94a3b8', fontSize: '1.2rem', fontWeight: 700, zIndex: 2 }}>&rarr;</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Supported Data Sources */}
      <div style={{ padding: '56px 48px', background: '#ffffff', borderTop: '1px solid #e2e8f0', borderBottom: '1px solid #e2e8f0' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div style={{ marginBottom: 28 }}>
            <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}>SUPPORTED DATA</div>
            <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: '0 0 6px', fontWeight: 700 }}>Supported Information Sources</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {sources.map((s) => (
              <div key={s.label} className="mi-card">
                <div style={{ color: '#0d2247', marginBottom: 16, background: '#e8f0fe', width: 40, height: 40, borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {s.icon}
                </div>
                <div className="mi-condensed" style={{ fontWeight: 700, color: '#0d2247', marginBottom: 6, fontSize: '1.1rem' }}>{s.label}</div>
                <p style={{ color: '#64748b', fontSize: '0.85rem', lineHeight: 1.55, margin: 0 }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Toggleable Side-by-Side Capabilities Section */}
      <div style={{ padding: '64px 48px', background: '#f1f5f9' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div style={{ marginBottom: 36 }}>
            <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}>CAPABILITIES</div>
            <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: 0, fontWeight: 700 }}>Key Platform Capabilities</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'start' }}>
            {/* Left Column (Blue) */}
            <div style={{ background: 'linear-gradient(135deg, #0d2247 0%, #081733 100%)', borderRadius: 6, padding: 24, color: '#ffffff', display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div className="mi-condensed" style={{ color: '#00e676', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 4 }}>
                CORE INTELLIGENCE & ANALYTICS
              </div>

              {leftCapabilities.map((cap, leftIdx) => {
                const originalIndex = leftIdx * 2;
                const isExpanded = expandedIndex === originalIndex;

                return (
                  <div
                    key={originalIndex}
                    onClick={() => toggleExpand(originalIndex)}
                    style={{
                      background: isExpanded ? 'rgba(255, 255, 255, 0.12)' : 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: 4,
                      padding: 14,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
                      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <div style={{ color: '#00e676', marginTop: 1, flexShrink: 0 }}>
                          <Icon.CheckCircle />
                        </div>
                        <div>
                          <div style={{ fontSize: '0.925rem', fontWeight: 600, color: '#ffffff' }}>{cap.title}</div>
                          <p style={{ margin: '4px 0 0', fontSize: '0.825rem', color: '#cbd5e1', lineHeight: 1.4 }}>{cap.desc}</p>
                        </div>
                      </div>
                      <span style={{ color: '#00e676', fontSize: '0.75rem', fontWeight: 700 }}>{isExpanded ? '▲' : '▼'}</span>
                    </div>
                    {isExpanded && (
                      <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid rgba(255, 255, 255, 0.15)', fontSize: '0.8rem', color: '#e2e8f0', lineHeight: 1.45 }}>
                        <strong>Details: </strong>{cap.details}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Right Column (White) */}
            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 6, padding: 24, color: '#1f2937', display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 4 }}>
                SPATIAL & REPORTING MODULES
              </div>

              {rightCapabilities.map((cap, rightIdx) => {
                const originalIndex = rightIdx * 2 + 1;
                const isExpanded = expandedIndex === originalIndex;

                return (
                  <div
                    key={originalIndex}
                    onClick={() => toggleExpand(originalIndex)}
                    style={{
                      background: isExpanded ? '#f8fafc' : '#ffffff',
                      border: isExpanded ? '1px solid #cbd5e1' : '1px solid #f1f5f9',
                      borderRadius: 4,
                      padding: 14,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
                      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <div style={{ color: '#1e7e34', marginTop: 1, flexShrink: 0 }}>
                          <Icon.CheckCircle />
                        </div>
                        <div>
                          <div style={{ fontSize: '0.925rem', fontWeight: 600, color: '#0d2247' }}>{cap.title}</div>
                          <p style={{ margin: '4px 0 0', fontSize: '0.825rem', color: '#64748b', lineHeight: 1.4 }}>{cap.desc}</p>
                        </div>
                      </div>
                      <span style={{ color: '#1e7e34', fontSize: '0.75rem', fontWeight: 700 }}>{isExpanded ? '▲' : '▼'}</span>
                    </div>
                    {isExpanded && (
                      <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid #e2e8f0', fontSize: '0.8rem', color: '#475569', lineHeight: 1.45 }}>
                        <strong>Details: </strong>{cap.details}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}