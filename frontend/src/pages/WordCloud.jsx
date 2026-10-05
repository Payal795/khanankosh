import React, { useEffect, useState } from 'react';
import { Icon } from '../components/Icon';
import { apiUrl } from './api';

export default function WordCloud() {
  const [words, setWords] = useState([]);
  const [cloudImage, setCloudImage] = useState('');
  const [viewMode, setViewMode] = useState('pills'); // 'pills' | 'image'
  const [selectedWord, setSelectedWord] = useState('');
  const [snippets, setSnippets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [imgLoading, setImgLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fetchStatus, setFetchStatus] = useState(''); // New: Real-time debug status

  // 1. Fetch word frequencies and generated cloud image concurrently on load
  useEffect(() => {
    fetch(apiUrl('/api/v1/wordcloud'))
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return res.json();
      })
      .then((data) => setWords(data.data || []))
      .catch((err) => {
        console.error('Error fetching word cloud data:', err);
        setError('Could not load topics from the server.');
      });

    fetchCloudImage();
  }, []);

  const fetchCloudImage = () => {
    setImgLoading(true);
    fetch(apiUrl('/api/v1/export-cloud-image'))
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (data.data) {
          setCloudImage(data.data);
        }
      })
      .catch((err) => {
        console.error('Error fetching word cloud image:', err);
      })
      .finally(() => {
        setImgLoading(false);
      });
  };

  const handleWordClick = async (term) => {
    setSelectedWord(term);
    setLoading(true);
    setFetchStatus(`Querying backend for "${term}"...`);
    
    console.log(`[DRILL-DOWN] Request URL: ${apiUrl('/api/v1/drill-down')}?keyword=${encodeURIComponent(term)}&limit=5`);

    try {
      const res = await fetch(
        `${apiUrl('/api/v1/drill-down')}?keyword=${encodeURIComponent(term)}&limit=5`
      );
      
      if (!res.ok) throw new Error(`Server returned HTTP ${res.status}`);
      
      const data = await res.json();
      console.log(`[DRILL-DOWN] Received data:`, data);
      
      setSnippets(data.results || []);
      setFetchStatus(
        (data.results && data.results.length > 0)
          ? `Found ${data.results.length} excerpts.`
          : `No document excerpts matched "${term}".`
      );
    } catch (err) {
      console.error('[DRILL-DOWN] Fetch error:', err);
      setSnippets([]);
      setFetchStatus(`Error connecting to API: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadImage = () => {
    if (!cloudImage) return;
    const link = document.createElement('a');
    link.href = cloudImage;
    link.download = `cmpdi_geological_wordcloud_${Date.now()}.png`;
    link.click();
  };

  return (
    <div
      style={{
        fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif',
        color: '#1f2937',
        background: '#f8fafc',
        minHeight: '100vh',
        padding: '36px 48px',
        boxSizing: 'border-box',
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Roboto:wght@400;500;700&display=swap');

        .mi-condensed {
          font-family: 'Oswald', 'Arial Narrow', sans-serif;
          letter-spacing: 0.02em;
          text-transform: uppercase;
        }

        .mi-cloud-pill {
          font-family: 'Roboto', -apple-system, sans-serif !important;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border: 1px solid #cbd5e1;
          cursor: pointer;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          line-height: 1.1;
        }

        .mi-cloud-pill:hover {
          border-color: #0d2247;
          background-color: #f1f5f9 !important;
          transform: translateY(-2px);
          box-shadow: 0 4px 10px rgba(13, 34, 71, 0.1);
        }

        .mi-snippet-card {
          background-color: #ffffff;
          padding: 16px;
          border-radius: 4px;
          border: 1px solid #cbd5e1;
          border-left: 4px solid #0d2247;
          font-size: 0.85rem;
          color: #334155;
          line-height: 1.55;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
          transition: all 0.15s ease;
        }

        .mi-snippet-card:hover {
          border-left-color: #1e7e34;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        }

        .mi-scroll-area::-webkit-scrollbar { width: 6px; }
        .mi-scroll-area::-webkit-scrollbar-track { background: #dbeafe; border-radius: 4px; }
        .mi-scroll-area::-webkit-scrollbar-thumb { background: #93c5fd; border-radius: 4px; }
        .mi-scroll-area::-webkit-scrollbar-thumb:hover { background: #60a5fa; }
      `}</style>

      {/* Main Container Grid */}
      <div
        style={{
          maxWidth: 1300,
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: '1.1fr 0.9fr',
          gap: '28px',
        }}
      >
        {/* Left Panel: Extracted Themes */}
        <div
          style={{
            backgroundColor: '#ffffff',
            padding: '28px',
            borderRadius: '6px',
            border: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ color: '#1e7e34', display: 'flex', alignItems: 'center' }}>
                <Icon.Database />
              </div>
              <div
                className="mi-condensed"
                style={{
                  color: '#1e7e34',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  letterSpacing: '0.08em',
                }}
              >
                DOCUMENT CORPUS INTELLIGENCE
              </div>
            </div>

            {/* Mode Switcher: Interactive Pills vs Official Python Render */}
            <div style={{ display: 'flex', gap: 6 }}>
              <button
                type="button"
                onClick={() => setViewMode('pills')}
                style={{
                  padding: '4px 10px',
                  fontSize: '0.75rem',
                  borderRadius: '4px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: '1px solid #cbd5e1',
                  background: viewMode === 'pills' ? '#0d2247' : '#ffffff',
                  color: viewMode === 'pills' ? '#ffffff' : '#475569',
                }}
              >
                Interactive Cloud
              </button>
              <button
                type="button"
                onClick={() => setViewMode('image')}
                style={{
                  padding: '4px 10px',
                  fontSize: '0.75rem',
                  borderRadius: '4px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: '1px solid #cbd5e1',
                  background: viewMode === 'image' ? '#0d2247' : '#ffffff',
                  color: viewMode === 'image' ? '#ffffff' : '#475569',
                }}
              >
                Statutory Export (PNG)
              </button>
            </div>
          </div>

          <h2
            className="mi-condensed"
            style={{
              fontSize: '1.6rem',
              color: '#0d2247',
              margin: '0 0 18px',
              fontWeight: 700,
            }}
          >
            Extracted Geological & Statutory Themes
          </h2>

          {error && (
            <p style={{ color: '#dc2626', marginBottom: '16px', fontSize: '0.875rem' }}>
              {error}
            </p>
          )}

          {/* View Container */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '16px',
              background: '#f8fafc',
              borderRadius: '6px',
              border: '1px solid #f1f5f9',
              minHeight: 420,
              flex: 1,
              position: 'relative',
            }}
          >
            {/* View Mode 1: Interactive Pills Cloud */}
            {viewMode === 'pills' && (
              <div
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '8px 10px',
                  alignItems: 'center',
                  justifyContent: 'center',
                  maxWidth: '96%',
                  margin: '0 auto',
                }}
              >
                {words.length === 0 && !error && (
                  <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                    Loading keyword clusters...
                  </span>
                )}

                {words.map((w, idx) => {
                  const isActive = selectedWord === w.text;
                  const fontSize = Math.max(11, Math.min(15, Math.round(10 + (w.value || 10) * 0.18)));
                  const borderRadius = idx % 2 === 0 ? '16px 6px 16px 6px' : '6px 16px 6px 16px';

                  return (
                    <button
                      key={idx}
                      type="button"
                      className="mi-cloud-pill"
                      onClick={() => handleWordClick(w.text)}
                      style={{
                        fontSize: `${fontSize}px`,
                        padding: '6px 14px',
                        borderRadius,
                        fontWeight: isActive ? 700 : 600,
                        backgroundColor: isActive ? '#0d2247' : '#ffffff',
                        color: isActive ? '#ffffff' : '#334155',
                        borderColor: isActive ? '#0d2247' : '#cbd5e1',
                        transform: isActive ? 'scale(1.05)' : 'none',
                        boxShadow: isActive
                          ? '0 4px 10px rgba(13, 34, 71, 0.18)'
                          : '0 1px 2px rgba(0,0,0,0.03)',
                      }}
                    >
                      {w.text}
                    </button>
                  );
                })}
              </div>
            )}

            {/* View Mode 2: Base64 Generated Image from WordCloud library */}
            {viewMode === 'image' && (
              <div
                style={{
                  width: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 12,
                }}
              >
                {imgLoading && (
                  <span style={{ fontSize: '0.85rem', color: '#1d4ed8' }}>
                    Rendering high-resolution wordcloud graphic...
                  </span>
                )}

                {!imgLoading && cloudImage ? (
                  <>
                    <img
                      src={cloudImage}
                      alt="CMPDI Mining Topic Word Cloud"
                      style={{
                        maxWidth: '100%',
                        height: 'auto',
                        borderRadius: '6px',
                        border: '1px solid #334155',
                        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
                      }}
                    />
                    <div style={{ display: 'flex', gap: 10, marginTop: 6 }}>
                      <button
                        type="button"
                        onClick={handleDownloadImage}
                        style={{
                          padding: '6px 14px',
                          fontSize: '0.78rem',
                          borderRadius: '4px',
                          background: '#1e7e34',
                          color: '#ffffff',
                          border: 'none',
                          cursor: 'pointer',
                          fontWeight: 600,
                        }}
                      >
                        Download Report Artifact (PNG)
                      </button>
                      <button
                        type="button"
                        onClick={fetchCloudImage}
                        style={{
                          padding: '6px 14px',
                          fontSize: '0.78rem',
                          borderRadius: '4px',
                          background: '#ffffff',
                          color: '#334155',
                          border: '1px solid #cbd5e1',
                          cursor: 'pointer',
                          fontWeight: 600,
                        }}
                      >
                        Regenerate
                      </button>
                    </div>
                  </>
                ) : (
                  !imgLoading && (
                    <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                      No cloud image available from server.
                    </span>
                  )
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Source Citations */}
        <div
          style={{
            backgroundColor: '#eff6ff',
            padding: '28px',
            borderRadius: '6px',
            border: '1px solid #bfdbfe',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <div style={{ color: '#1d4ed8', display: 'flex', alignItems: 'center' }}>
              <Icon.FileText />
            </div>
            <div
              className="mi-condensed"
              style={{
                color: '#1d4ed8',
                fontSize: '0.78rem',
                fontWeight: 700,
                letterSpacing: '0.08em',
              }}
            >
              EVIDENCE RETRIEVAL
            </div>
          </div>

          <h2
            className="mi-condensed"
            style={{
              fontSize: '1.6rem',
              color: '#0d2247',
              margin: '0 0 16px',
              fontWeight: 700,
            }}
          >
            Source Citations {selectedWord ? `for "${selectedWord}"` : ''}
          </h2>

          {/* Real-time Status / Debug Bar */}
          {fetchStatus && (
            <div
              style={{
                fontSize: '0.8rem',
                padding: '8px 12px',
                borderRadius: '4px',
                marginBottom: '14px',
                backgroundColor: snippets.length > 0 ? '#dcfce7' : '#fee2e2',
                color: snippets.length > 0 ? '#166534' : '#991b1b',
                border: `1px solid ${snippets.length > 0 ? '#bbf7d0' : '#fecaca'}`,
                fontWeight: 500,
              }}
            >
              {fetchStatus}
            </div>
          )}

          {/* State 1: Loading */}
          {loading && (
            <div
              style={{
                color: '#1e40af',
                fontSize: '0.875rem',
                fontWeight: 500,
                fontStyle: 'italic',
                padding: '12px 0',
              }}
            >
              Querying indexed document corpus...
            </div>
          )}

          {/* State 2: Default view when no word has been clicked yet */}
          {!loading && !selectedWord && (
            <div
              style={{
                color: '#475569',
                fontSize: '0.875rem',
                background: '#ffffff',
                border: '1px solid #cbd5e1',
                padding: '24px',
                borderRadius: '4px',
                textAlign: 'center',
                margin: 'auto 0',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <div style={{ color: '#94a3b8' }}>
                <Icon.MessageSquare />
              </div>
              Click any keyword on the left to inspect original PDF excerpts and statutory citations.
            </div>
          )}

          {/* State 3: Word clicked, but 0 matches came back from backend */}
          {!loading && selectedWord && snippets.length === 0 && (
            <div
              style={{
                color: '#334155',
                fontSize: '0.85rem',
                background: '#ffffff',
                border: '1px solid #e2e8f0',
                padding: '20px',
                borderRadius: '4px',
                textAlign: 'center',
                margin: 'auto 0',
              }}
            >
              <p style={{ margin: '0 0 8px 0', fontWeight: 600, color: '#b91c1c' }}>
                0 passages found for "{selectedWord}".
              </p>
              <p style={{ margin: 0, fontSize: '0.78rem', color: '#64748b' }}>
                Check if the word exists under singular form or inspect terminal logs in <code>api.py</code>.
              </p>
            </div>
          )}

          {/* State 4: Matching snippets */}
          {!loading && snippets.length > 0 && (
            <div
              className="mi-scroll-area"
              style={{
                maxHeight: '480px',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                paddingRight: '6px',
              }}
            >
              {snippets.map((s) => (
                <div key={s.chunk_id} className="mi-snippet-card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                    <div style={{ color: '#1e7e34', display: 'flex', alignItems: 'center' }}>
                      <Icon.CheckCircle />
                    </div>
                    <span
                      className="mi-condensed"
                      style={{
                        fontSize: '0.75rem',
                        color: '#1e7e34',
                        fontWeight: 700,
                        letterSpacing: '0.04em',
                      }}
                    >
                      Passage #{s.chunk_id}
                    </span>
                  </div>
                  {s.content}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}