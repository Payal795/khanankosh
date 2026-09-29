import React from 'react';
import { Icon } from '../components/Icon';

export function IntroPage() {
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

  return (
    <div style={{ fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif', color: '#1f2937', background: '#f8fafc', minHeight: '100vh', width: '100%', overflowX: 'hidden' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Roboto:wght@400;500;700&display=swap');

        .mi-condensed {
          font-family: 'Oswald', 'Arial Narrow', sans-serif;
          letter-spacing: 0.02em;
          text-transform: uppercase;
        }

        @keyframes miFadeUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* High-Visibility Left-to-Right Swish Wipe Animation */
        @keyframes miSwishCurtain {
          0% {
            clip-path: polygon(0 0, 0 0, 0 100%, 0 100%);
            opacity: 0;
            transform: translateX(-30px);
          }
          30% {
            opacity: 0.6;
          }
          100% {
            clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
            opacity: 1;
            transform: translateX(0);
          }
        }

        .mi-animate-hero {
          animation: miFadeUp 0.8s ease-out forwards;
        }

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
        .mi-problem-item:hover {
          background-color: #fef2f2;
        }

        .mi-capability-row {
          display: flex;
          gap: 12px;
          align-items: flex-start;
          padding: 14px 0;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          transition: background-color 0.15s ease;
        }
        .mi-capability-row:hover {
          background-color: rgba(255, 255, 255, 0.04);
        }

        /* Restored Card Box Styles */
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
          <div
            className="mi-condensed"
            style={{ color: '#00e676', fontSize: '0.85rem', fontWeight: 600, letterSpacing: '0.1em', marginBottom: 12 }}
          >
            PLATFORM OVERVIEW
          </div>
          <h1
            className="mi-condensed"
            style={{ fontSize: '2.8rem', fontWeight: 700, margin: '0 0 16px', lineHeight: 1.1 }}
          >
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
            
            {/* Box 1: Solution Overview */}
            <div
              style={{
                background: '#f8fafc',
                borderLeft: '4px solid #1e7e34',
                borderTop: '1px solid #e2e8f0',
                borderRight: '1px solid #e2e8f0',
                borderBottom: '1px solid #e2e8f0',
                borderRadius: '0 6px 6px 0',
                padding: 32,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em' }}>
                  CORE ARCHITECTURE
                </div>
                <span className="mi-condensed" style={{ background: '#e6f4ea', color: '#137333', fontSize: '0.65rem', padding: '3px 8px', borderRadius: 2, fontWeight: 700 }}>
                  SOLUTION OVERVIEW
                </span>
              </div>
              <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: '0 0 16px', fontWeight: 700 }}>
                What is this Platform?
              </h2>
              <p style={{ color: '#475569', lineHeight: 1.7, fontSize: '0.925rem', marginBottom: 16 }}>
                The CMPDI Intelligent Mining Platform is an enterprise-grade AI decision-support system built specifically for the needs of Coal India Limited and its subsidiary CMPDI. It combines GIS land feasibility assessment, AI-powered document intelligence, and automated report generation.
              </p>
              <p style={{ color: '#475569', lineHeight: 1.7, fontSize: '0.925rem', margin: 0 }}>
                The system ingests decades of organisational knowledge — geological surveys, production reports, environmental assessments, parliamentary responses — and makes this information instantly accessible and actionable through natural language interaction and structured analysis tools.
              </p>
            </div>

            {/* Box 2: Problem Statement */}
            <div
              style={{
                background: '#fff5f5',
                borderLeft: '4px solid #dc2626',
                borderTop: '1px solid #fee2e2',
                borderRight: '1px solid #fee2e2',
                borderBottom: '1px solid #fee2e2',
                borderRadius: '0 6px 6px 0',
                padding: 32,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <div className="mi-condensed" style={{ color: '#dc2626', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em' }}>
                  OPERATIONAL CHALLENGES
                </div>
                <span className="mi-condensed" style={{ background: '#fee2e2', color: '#b91c1c', fontSize: '0.65rem', padding: '3px 8px', borderRadius: 2, fontWeight: 700 }}>
                  PROBLEM STATEMENT
                </span>
              </div>
              <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: '0 0 16px', fontWeight: 700 }}>
                Why was this Built?
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {[
                  'Thousands of geological and operational reports locked in paper archives or unstructured digital files',
                  'Manual, time-consuming GIS feasibility assessments requiring specialist expertise',
                  'Information silos across departments preventing integrated decision-making',
                  'Difficulty extracting specific data for parliamentary questions or administrative reports',
                  'No unified interface to query historical mining data and institutional knowledge',
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

      {/* Restored Workflow Card Boxes with Circled Badges & Visible Left-to-Right Animation */}
      <div style={{ padding: '56px 48px', background: '#f8fafc' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div style={{ marginBottom: 28 }}>
            <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}>
              HOW IT WORKS
            </div>
            <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: 0, fontWeight: 700 }}>
              Platform Workflow
            </h2>
          </div>

          <div
            className="mi-swish-container"
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(6, 1fr)',
              gap: 24,
              width: '100%',
              position: 'relative',
            }}
          >
            {workflow.map((w, i) => (
              <div key={i} style={{ position: 'relative' }}>
                <div className="mi-workflow-card">
                  {/* Circled Number Badge */}
                  <div style={{ marginBottom: 12 }}>
                    <span
                      className="mi-condensed"
                      style={{
                        background: w.color,
                        color: '#ffffff',
                        width: 34,
                        height: 34,
                        borderRadius: '50%',
                        fontWeight: 700,
                        fontSize: '0.8rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: '0 2px 5px rgba(0, 0, 0, 0.12)',
                      }}
                    >
                      {String(i + 1).padStart(2, '0')}
                    </span>
                  </div>

                  {/* Title */}
                  <div
                    className="mi-condensed"
                    style={{
                      fontWeight: 700,
                      color: w.color,
                      fontSize: '0.92rem',
                      lineHeight: 1.25,
                      marginBottom: 8,
                    }}
                  >
                    {w.step}
                  </div>

                  {/* Body description */}
                  <div style={{ color: '#64748b', fontSize: '0.78rem', lineHeight: 1.45 }}>
                    {w.desc}
                  </div>
                </div>

                {/* Centered Flow Arrow */}
                {i < workflow.length - 1 && (
                  <div
                    style={{
                      position: 'absolute',
                      right: -17,
                      top: '50%',
                      transform: 'translateY(-50%)',
                      color: '#94a3b8',
                      fontSize: '1.2rem',
                      fontWeight: 700,
                      zIndex: 2,
                      userSelect: 'none',
                    }}
                  >
                    &rarr;
                  </div>
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
            <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}>
              SUPPORTED DATA
            </div>
            <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#0d2247', margin: '0 0 6px', fontWeight: 700 }}>
              Supported Information Sources
            </h2>
            <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>
              The platform ingests and processes the following types of organisational data:
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {sources.map((s) => (
              <div key={s.label} className="mi-card">
                <div
                  style={{
                    color: '#0d2247',
                    marginBottom: 16,
                    background: '#e8f0fe',
                    width: 40,
                    height: 40,
                    borderRadius: 4,
                    display: 'flex',
                    alignItems: 'center',
                    justify: 'center',
                    flexShrink: 0,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                    {s.icon}
                  </div>
                </div>
                <div className="mi-condensed" style={{ fontWeight: 700, color: '#0d2247', marginBottom: 6, fontSize: '1.1rem' }}>
                  {s.label}
                </div>
                <p style={{ color: '#64748b', fontSize: '0.85rem', lineHeight: 1.55, margin: 0 }}>
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Key Platform Capabilities */}
      <div style={{ padding: '56px 48px 72px', background: 'linear-gradient(135deg, #0d2247 0%, #081733 100%)', color: '#ffffff' }}>
        <div style={{ maxWidth: 1300, margin: '0 auto' }}>
          <div style={{ marginBottom: 28 }}>
            <div className="mi-condensed" style={{ color: '#00e676', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}>
              CAPABILITIES
            </div>
            <h2 className="mi-condensed" style={{ fontSize: '1.8rem', color: '#ffffff', margin: 0, fontWeight: 700 }}>
              Key Platform Capabilities
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
            {[
              'Automated GIS land feasibility scoring with multi-parameter analysis',
              'Natural language Q&A over geological reports and historical mining data',
              'AI-assisted report generation with source citations and references',
              'Interactive spatial map with layered geological and environmental data',
              'OCR and intelligent processing of scanned PDF documents',
              'Parliamentary Q&A and administrative response drafting support',
              'Production data analysis and trend identification across mine sites',
              'Integration with environmental and satellite geospatial datasets',
            ].map((cap, i) => (
              <div key={i} className="mi-capability-row">
                <div style={{ color: '#00e676', flexShrink: 0, marginTop: 1, display: 'flex', alignItems: 'center' }}>
                  <Icon.CheckCircle />
                </div>
                <span style={{ color: '#cbd5e1', fontSize: '0.9rem', lineHeight: 1.55 }}>{cap}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}