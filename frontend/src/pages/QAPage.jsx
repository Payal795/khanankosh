import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { apiUrl } from './api';
import { 
  Send, Plus, Database, BookOpen, ShieldCheck, Sparkles, ChevronDown, CheckCircle2, FileSearch 
} from 'lucide-react';

function extractSuggestedFollowups(answer) {
  const marker = /(?:^|\r?\n)[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*|__)?S?uggested Follow[-\u2010-\u2015]up Questions(?::)?(?:\*\*|__)?[ \t]*:?[ \t]*(?:\r?\n|$)/i;
  const match = marker.exec(answer);
  if (!match) return { answer, suggestions: [] };

  const suggestions = answer.slice(match.index + match[0].length)
    .split(/\r?\n/)
    .map((line) => line.trim()
      .replace(/^(?:[-*+]|\d+[.)])\s*/, '')
      .replace(/^[*_`]+|[*_`]+$/g, '')
      .trim())
    .filter(Boolean);

  return {
    answer: answer.slice(0, match.index).trim(),
    suggestions
  };
}

export default function QAPage() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'agent',
      text: "Welcome to the **खनन Kosh Q&A Agent**. You can query verified geological seam records, statutory production data, environmental clearances, and safety audit protocols across all operational mining regions.",
      suggestions: [
        "What are Coal India's main worker safety or training policies",
        "How does Coal India measure the effectiveness of its safety training programs?",
        "What specific technologies are being adopted to enhance safety in underground mining operations?"
      ]
    }
  ]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (questionToSend) => {
    const text = questionToSend || query;
    if (!text.trim() || loading) return;

    const userMsg = { id: Date.now(), sender: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch(apiUrl('/api/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Backend request failed");
      }

      const rawAnswer = data.answer || data.response || "No records found matching the requested query parameters.";
      const parsedAnswer = extractSuggestedFollowups(rawAnswer);
      const suggestions = Array.isArray(data.suggestions)
        ? data.suggestions.filter((suggestion) => typeof suggestion === 'string' && suggestion.trim())
        : [];
      const agentMsg = {
        id: Date.now() + 1,
        sender: 'agent',
        text: parsedAnswer.answer || rawAnswer,
        suggestions: suggestions.length ? suggestions : parsedAnswer.suggestions
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'agent',
          text: "⚠️ **Gateway Communication Notice**: Unable to connect to intelligence services. Please try again shortly.",
          suggestions: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif', background: '#F8FAFC' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Roboto:wght@400;500;700&display=swap');

        .mi-condensed {
          font-family: 'Oswald', 'Arial Narrow', sans-serif;
          letter-spacing: 0.02em;
          text-transform: uppercase;
        }

        .mi-btn-navy {
          background-color: #0D2247;
          color: #FFFFFF;
          border: none;
          font-family: 'Oswald', sans-serif;
          font-weight: 600;
          font-size: 0.85rem;
          letter-spacing: 0.08em;
          padding: 10px 16px;
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          transition: background 0.15s ease;
        }
        .mi-btn-navy:hover {
          background-color: #081733;
        }

        .mi-chat-input:focus {
          border-color: #0D2247 !important;
          box-shadow: 0 0 0 2px rgba(13, 34, 71, 0.1);
        }
      `}</style>

      {/* ── MAIN WORKSPACE ── */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* SIDEBAR */}
        <aside style={{ width: '280px', borderRight: '1px solid #E2E8F0', background: '#FFFFFF', padding: '24px 18px', display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' }}>
          <button 
            onClick={() => setMessages([messages[0]])}
            className="mi-btn-navy"
            style={{ width: '100%' }}
          >
            <Plus size={15} /> NEW INQUIRY
          </button>

          <div>
            <div className="mi-condensed" style={{ fontSize: '0.75rem', fontWeight: '700', color: '#1E7E34', letterSpacing: '0.08em', marginBottom: '12px' }}>
              INDEXED DATA SOURCES
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem', color: '#334155' }}>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}><BookOpen size={15} color="#0D2247"/> CMPDI Geological Records</div>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}><Database size={15} color="#0D2247"/> CIL Reserve Inventory</div>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}><ShieldCheck size={15} color="#0D2247"/> Statutory Safety Protocols</div>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}><FileSearch size={15} color="#0D2247"/> Environmental Clearances</div>
            </div>
          </div>

          <div>
            <div className="mi-condensed" style={{ fontSize: '0.75rem', fontWeight: '700', color: '#1E7E34', letterSpacing: '0.08em', marginBottom: '12px' }}>
              QUERY SCOPE
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ border: '1px solid #CBD5E1', borderRadius: '4px', padding: '8px 12px', fontSize: '0.825rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#475569', background: '#F8FAFC' }}>
                <span>All Coalfields & Basins</span> <ChevronDown size={14}/>
              </div>
              <div style={{ border: '1px solid #CBD5E1', borderRadius: '4px', padding: '8px 12px', fontSize: '0.825rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#475569', background: '#F8FAFC' }}>
                <span>All Seams (G1-G17)</span> <ChevronDown size={14}/>
              </div>
            </div>
          </div>
        </aside>

        {/* CHAT DISPLAY */}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#F8FAFC' }}>
          
          {/* Section Header */}
          <div style={{ padding: '16px 32px', borderBottom: '1px solid #E2E8F0', background: '#FFFFFF' }}>
            <div className="mi-condensed" style={{ color: '#1E7E34', fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: '2px' }}>
              DECISION SUPPORT ENGINE
            </div>
            <h1 className="mi-condensed" style={{ margin: 0, fontSize: '1.5rem', color: '#0D2247', fontWeight: '700' }}>
              Mining Knowledge Q&A Agent
            </h1>
            <p style={{ margin: '2px 0 0 0', fontSize: '0.825rem', color: '#64748B' }}>
              Enterprise Geological, Reserve & Statutory Compliance Intelligence Portal
            </p>
          </div>

          {/* Messages Feed (Padding Bottom reduced to 12px) */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '18px 32px 12px 32px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {messages.map((msg) => (
              <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
                
                <span className="mi-condensed" style={{ fontSize: '0.7rem', color: '#94A3B8', marginBottom: '4px', fontWeight: '600', letterSpacing: '0.04em' }}>
                  {msg.sender === 'user' ? 'Authorized Operator' : 'खनन Kosh Intelligence Core'}
                </span>

                {msg.sender === 'user' ? (
                  <div style={{ background: '#0D2247', color: '#FFFFFF', padding: '10px 16px', borderRadius: '6px 6px 2px 6px', maxWidth: '72%', fontSize: '0.875rem', lineHeight: '1.5' }}>
                    {msg.text}
                  </div>
                ) : (
                  <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '6px', padding: '14px 18px', maxWidth: '85%', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
                    
                    {/* Validation Badge */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#E6F4EA', border: '1px solid #A7F3D0', padding: '3px 8px', borderRadius: '4px', width: 'fit-content', marginBottom: '10px' }}>
                      <CheckCircle2 size={12} color="#137333" />
                      <span className="mi-condensed" style={{ fontSize: '0.68rem', fontWeight: '700', color: '#137333' }}>
                        Validated via Verified CIL Production Datastores & Statutory Archives
                      </span>
                    </div>

                    {/* Markdown Output */}
                    <div style={{ fontSize: '0.875rem', lineHeight: '1.6', color: '#1E293B' }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.text}
                      </ReactMarkdown>
                    </div>

                    {/* Follow-up Suggestions (Reduced Spacing) */}
                    {msg.suggestions && msg.suggestions.length > 0 && (
                      <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid #F1F5F9' }}>
                        <span className="mi-condensed" style={{ fontSize: '0.68rem', fontWeight: '700', color: '#1E7E34', display: 'block', marginBottom: '6px', letterSpacing: '0.06em' }}>
                          RECOMMENDED EXPLORATORY QUERIES:
                        </span>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                          {msg.suggestions.map((sugg, sIdx) => (
                            <button
                              key={sIdx}
                              type="button"
                              onClick={() => handleSend(sugg)}
                              disabled={loading}
                              style={{
                                background: '#E8F0FE', border: '1px solid #BAE6FD', color: '#1A73E8',
                                borderRadius: '4px', padding: '4px 10px', fontSize: '0.75rem', cursor: 'pointer',
                                display: 'flex', alignItems: 'center', gap: '5px', transition: 'all 0.15s ease',
                                opacity: loading ? 0.6 : 1
                              }}
                              onMouseOver={(e) => (e.currentTarget.style.background = '#Dbeafe')}
                              onMouseOut={(e) => (e.currentTarget.style.background = '#E8F0FE')}
                            >
                              <Sparkles size={11} color="#1A73E8" /> {sugg}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#0D2247', fontSize: '0.825rem', fontWeight: '500', padding: '4px 0' }}>
                <Sparkles size={14} color="#0D2247" />
                <span>Aggregating data from institutional records...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* INPUT BAR (Tightened Padding Top: 8px, Bottom: 14px) */}
          <div style={{ padding: '8px 32px 14px 32px', background: '#FFFFFF', borderTop: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                className="mi-chat-input"
                type="text"
                placeholder="Inquire regarding coal reserve volumes, safety protocols, extraction feasibility..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                style={{ flex: 1, padding: '10px 14px', border: '1px solid #CBD5E1', borderRadius: '4px', fontSize: '0.85rem', outline: 'none', transition: 'all 0.15s ease' }}
              />
              <button
                className="mi-btn-navy"
                onClick={() => handleSend()}
                disabled={loading || !query.trim()}
                style={{
                  padding: '0 18px', 
                  cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                  opacity: loading || !query.trim() ? 0.6 : 1
                }}
              >
                <Send size={14} />
              </button>
            </div>
          </div>

        </main>
      </div>
    </div>
  );
}