import React, { useState, useRef } from "react";
import { Icon } from "../components/Icon";
import { apiUrl } from "./api";

export default function ReportPage() {
  const [file, setFile] = useState(null);
  const [topic, setTopic] = useState("");
  const [description, setDescription] = useState("");
  
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0); // 1: Converting, 2: Indexing, 3: Rewriting, 4: Done
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef(null);

  const pipelineSteps = [
    { title: "Convert PDF", desc: "Preserving layout, spatial coordinates & structural elements" },
    { title: "RAG Indexing", desc: "Extracting tables, vectorizing & embedding document chunks" },
    { title: "AI Rewriting", desc: "LLM synthesis over verified knowledge chunks" },
    { title: "Complete", desc: "Polished DOCX administrative report generated" },
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    if (selectedFile.type !== "application/pdf") {
      setErrorMessage("Please select a valid PDF document.");
      return;
    }
    setErrorMessage("");
    setFile(selectedFile);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !topic.trim() || !description.trim()) {
      setErrorMessage("Please upload a PDF document and fill in all required fields.");
      return;
    }

    setErrorMessage("");
    setLoading(true);
    setDownloadUrl(null);
    setCurrentStep(1);

    // Animated step progression during generation
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev < 3 ? prev + 1 : prev));
    }, 4500);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("topic", topic);
    formData.append("description", description);

    try {
      const response = await fetch(apiUrl("/api/report"), {
        method: "POST",
        body: formData,
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Pipeline processing failed.");
      }

      const data = await response.json();
      setCurrentStep(4);
      setDownloadUrl(apiUrl(`/api/report/download/${data.job_id}`));
    } catch (err) {
      clearInterval(stepInterval);
      setCurrentStep(0);
      setErrorMessage(err.message || "An unexpected error occurred during processing.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setTopic("");
    setDescription("");
    setCurrentStep(0);
    setDownloadUrl(null);
    setErrorMessage("");
  };

  return (
    <div
      style={{
        fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif',
        color: '#1f2937',
        background: '#f8fafc',
        minHeight: '100vh',
        width: '100%',
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

        .mi-btn-navy {
          background-color: #0d2247;
          color: #ffffff;
          border: none;
          font-family: 'Oswald', sans-serif;
          font-weight: 600;
          font-size: 0.85rem;
          letter-spacing: 0.08em;
          padding: 12px 20px;
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: background 0.15s ease;
        }
        .mi-btn-navy:hover {
          background-color: #081733;
        }

        .mi-input:focus, .mi-textarea:focus {
          border-color: #0d2247 !important;
          box-shadow: 0 0 0 2px rgba(13, 34, 71, 0.1);
        }

        /* Animated Step Transitions */
        @keyframes miPulseGlow {
          0% {
            box-shadow: 0 0 0 0 rgba(13, 34, 71, 0.4);
            transform: scale(1);
          }
          50% {
            box-shadow: 0 0 0 6px rgba(13, 34, 71, 0);
            transform: scale(1.08);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(13, 34, 71, 0);
            transform: scale(1);
          }
        }

        .mi-step-indicator {
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .mi-step-active {
          animation: miPulseGlow 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
        }

        .mi-step-text {
          transition: color 0.3s ease;
        }
      `}</style>

      {/* Main Wrapper */}
      <main style={{ maxWidth: 1300, margin: '0 auto', padding: '36px 48px' }}>
        
        {/* Header Section */}
        <div style={{ marginBottom: 28 }}>
          <div
            className="mi-condensed"
            style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 6 }}
          >
            AUTOMATED REPORT GENERATION ENGINE
          </div>
          <h1
            className="mi-condensed"
            style={{ fontSize: '1.8rem', color: '#0d2247', margin: '0 0 8px', fontWeight: 700 }}
          >
            Smart Mining Report Generator
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0, maxWidth: 680, lineHeight: 1.6 }}>
            Upload source PDFs and guide the AI synthesis engine. The layout-preserving RAG pipeline reconstructs verified institutional documents into structured DOCX reports.
          </p>
        </div>

        {errorMessage && (
          <div
            style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fee2e2',
              borderLeft: '4px solid #dc2626',
              color: '#991b1b',
              padding: '12px 16px',
              borderRadius: '4px',
              marginBottom: '24px',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span style={{ fontWeight: 700 }}>⚠️</span> {errorMessage}
          </div>
        )}

        {/* Grid Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 28, alignItems: 'start' }}>
          
          {/* Left Panel: Inputs */}
          <section
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: 6,
              padding: 28,
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
            }}
          >
            <form onSubmit={handleSubmit}>
              
              {/* File Dropzone */}
              <div style={{ marginBottom: 20 }}>
                <label className="mi-condensed" style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#0d2247', marginBottom: 6 }}>
                  Source Document (PDF)
                </label>
                <div
                  style={{
                    border: '2px dashed',
                    borderColor: dragActive ? '#0d2247' : file ? '#1e7e34' : '#cbd5e1',
                    borderRadius: 4,
                    padding: '24px 16px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    backgroundColor: dragActive ? '#e8f0fe' : file ? '#f0fdf4' : '#f8fafc',
                    transition: 'all 0.2s ease',
                  }}
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="application/pdf"
                    style={{ display: 'none' }}
                    onChange={(e) => e.target.files?.[0] && validateAndSetFile(e.target.files[0])}
                  />

                  {file ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', textAlign: 'left' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{ color: '#1e7e34', display: 'flex', alignItems: 'center' }}>
                          <Icon.FileText />
                        </div>
                        <div>
                          <p style={{ fontSize: '0.875rem', fontWeight: 700, color: '#0d2247', margin: 0 }}>
                            {file.name}
                          </p>
                          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                            {(file.size / (1024 * 1024)).toFixed(2)} MB
                          </span>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setFile(null);
                        }}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#dc2626',
                          cursor: 'pointer',
                          fontSize: '1rem',
                          fontWeight: 700,
                          padding: '4px 8px',
                        }}
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <div>
                      <div style={{ color: '#0d2247', display: 'flex', justifyContent: 'center', marginBottom: 8 }}>
                        <Icon.Layers />
                      </div>
                      <p style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0d2247', margin: '0 0 4px' }}>
                        Click or drag PDF document here
                      </p>
                      <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                        Standard layout geological/statutory PDF (Up to 50MB)
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Topic Input */}
              <div style={{ marginBottom: 20 }}>
                <label className="mi-condensed" style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#0d2247', marginBottom: 6 }}>
                  Report Focus / Topic
                </label>
                <input
                  className="mi-input"
                  type="text"
                  placeholder="e.g. Environmental Impact Assessment & Safety Measures"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: 4,
                    border: '1px solid #cbd5e1',
                    fontSize: '0.85rem',
                    outline: 'none',
                    boxSizing: 'border-box',
                    transition: 'all 0.15s ease',
                  }}
                  disabled={loading}
                  required
                />
              </div>

              {/* Description Input */}
              <div style={{ marginBottom: 20 }}>
                <label className="mi-condensed" style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#0d2247', marginBottom: 6 }}>
                  Detailed Instructions
                </label>
                <textarea
                  className="mi-textarea"
                  rows={4}
                  placeholder="Provide explicit context, compliance directives, or focus metrics for the final document..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: 4,
                    border: '1px solid #cbd5e1',
                    fontSize: '0.85rem',
                    outline: 'none',
                    resize: 'vertical',
                    boxSizing: 'border-box',
                    fontFamily: 'inherit',
                    transition: 'all 0.15s ease',
                  }}
                  disabled={loading}
                  required
                />
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
                <button
                  type="submit"
                  className="mi-btn-navy"
                  disabled={loading || !file}
                  style={{
                    flex: 1,
                    opacity: loading || !file ? 0.6 : 1,
                    cursor: loading || !file ? 'not-allowed' : 'pointer',
                  }}
                >
                  {loading ? 'Processing Pipeline...' : 'Start Generation'}
                </button>
                {downloadUrl && (
                  <button
                    type="button"
                    onClick={handleReset}
                    className="mi-condensed"
                    style={{
                      backgroundColor: '#f1f5f9',
                      color: '#475569',
                      border: '1px solid #cbd5e1',
                      padding: '10px 16px',
                      borderRadius: 4,
                      fontSize: '0.825rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                  >
                    Start New
                  </button>
                )}
              </div>
            </form>
          </section>

          {/* Right Panel: Pipeline Progress */}
          <section
            style={{
              background: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: 6,
              padding: 28,
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
            }}
          >
            <div className="mi-condensed" style={{ color: '#1e7e34', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 4 }}>
              PIPELINE WORKFLOW
            </div>
            <h2 className="mi-condensed" style={{ fontSize: '1.4rem', color: '#0d2247', margin: '0 0 24px', fontWeight: 700 }}>
              Synthesis Status
            </h2>

            {/* Pipeline Steps */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              {pipelineSteps.map((step, idx) => {
                const stepNum = idx + 1;
                const isPassed = currentStep > stepNum || currentStep === 4;
                const isCurrent = currentStep === stepNum && loading;

                return (
                  <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
                    <div
                      className={`mi-step-indicator ${isCurrent ? 'mi-step-active' : ''}`}
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: 4,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.85rem',
                        fontWeight: 700,
                        flexShrink: 0,
                        backgroundColor: isPassed
                          ? '#1e7e34'
                          : isCurrent
                          ? '#0d2247'
                          : '#f1f5f9',
                        color: isPassed || isCurrent ? '#ffffff' : '#64748b',
                        border: isPassed || isCurrent ? 'none' : '1px solid #e2e8f0',
                      }}
                    >
                      {isPassed ? '✓' : String(stepNum).padStart(2, '0')}
                    </div>

                    <div style={{ flex: 1, paddingTop: 2 }}>
                      <h4
                        className="mi-condensed mi-step-text"
                        style={{
                          fontSize: '0.95rem',
                          fontWeight: 700,
                          margin: '0 0 2px',
                          color: isCurrent || isPassed ? '#0d2247' : '#94a3b8',
                        }}
                      >
                        {step.title}
                      </h4>
                      <p style={{ fontSize: '0.78rem', color: '#64748b', margin: 0, lineHeight: 1.4 }}>
                        {step.desc}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Download Export Box */}
            {downloadUrl && (
              <div
                style={{
                  marginTop: 32,
                  padding: 20,
                  borderRadius: 4,
                  backgroundColor: '#e6f4ea',
                  border: '1px solid #a7f3d0',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 14,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ color: '#137333', display: 'flex', alignItems: 'center' }}>
                    <Icon.CheckCircle />
                  </div>
                  <div>
                    <h4 className="mi-condensed" style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: '#137333' }}>
                      Report Export Ready
                    </h4>
                    <p style={{ margin: 0, fontSize: '0.78rem', color: '#15803d' }}>
                      Layout preserved and structured for administrative submission
                    </p>
                  </div>
                </div>
                <a
                  href={downloadUrl}
                  download
                  className="mi-condensed"
                  style={{
                    display: 'block',
                    textAlign: 'center',
                    backgroundColor: '#137333',
                    color: '#ffffff',
                    padding: '10px 16px',
                    borderRadius: 4,
                    textDecoration: 'none',
                    fontSize: '0.85rem',
                    fontWeight: 700,
                    letterSpacing: '0.06em',
                  }}
                >
                  📥 Download DOCX Report
                </a>
              </div>
            )}
          </section>

        </div>
      </main>
    </div>
  );
}