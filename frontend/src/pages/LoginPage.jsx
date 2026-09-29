import { useState } from 'react';

export function LoginPage({ onLogin }) {
  const [empId, setEmpId] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);

  const handleLogin = () => {
    onLogin();
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: '#f5f7fa' }}>
      {/* Left panel */}
      <div style={{ flex: '0 0 55%', background: '#0f2167', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: '60px' }}>
        <img
          src="https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1200&h=900&fit=crop&auto=format"
          alt="Coal mining operations"
          style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.18 }}
        />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(160deg, #0f2167 40%, #14532d 100%)', opacity: 0.88 }} />
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

        <div style={{ position: 'absolute', top: 40, left: 60, display: 'flex', gap: 20, alignItems: 'center' }}>
          {['CMPDI', 'CIL'].map(name => (
            <div key={name} style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 4, padding: '8px 16px', color: 'rgba(255,255,255,0.8)', fontSize: '0.8rem', fontWeight: 700, letterSpacing: '0.1em' }}>{name}</div>
          ))}
          <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.75rem', letterSpacing: '0.05em' }}>Government of India — Ministry of Coal</div>
        </div>

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', gap: 32, marginBottom: 48 }}>
            {[
              { val: '380+', label: 'Active Mines' },
              { val: '700M+', label: 'Tonnes Annual Production' },
              { val: '50+ Yrs', label: 'Data Archive' },
              { val: '8 States', label: 'Operational Regions' },
            ].map(stat => (
              <div key={stat.val} style={{ borderTop: '2px solid #4ade80', paddingTop: 12 }}>
                <div style={{ color: '#fff', fontFamily: "'Barlow Condensed', sans-serif", fontSize: '1.6rem', fontWeight: 700 }}>{stat.val}</div>
                <div style={{ color: 'rgba(255,255,255,0.55)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{stat.label}</div>
              </div>
            ))}
          </div>

          <div className="section-label" style={{ color: '#4ade80', marginBottom: 16 }}>Secure Government Portal</div>
          <h1 style={{ color: '#fff', fontSize: '2.6rem', fontWeight: 700, lineHeight: 1.15, marginBottom: 16, fontFamily: "'Barlow Condensed', sans-serif", maxWidth: 520 }}>
            AI-Assisted Mining Intelligence &amp; Reporting Platform
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.68)', fontSize: '1.05rem', maxWidth: 480, lineHeight: 1.65 }}>
            Integrated Decision Support for Geological, Mining and Administrative Intelligence — powered by verified organisational documents and spatial data.
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40 }}>
        <div style={{ width: '100%', maxWidth: 420 }}>
          <div style={{ textAlign: 'center', marginBottom: 36 }}>
            <div style={{ width: 56, height: 56, background: '#0f2167', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="1.5">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#0f2167', marginBottom: 4 }}>CMPDI Mining Intelligence</h2>
            <p style={{ color: 'var(--muted-foreground)', fontSize: '0.875rem' }}>Please sign in with your employee credentials</p>
          </div>

          <div className="card" style={{ padding: 32 }}>
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--foreground)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Employee ID / Email</label>
              <input type="text" placeholder="e.g. EMP-2024-0483 or user@cmpdi.gov.in" value={empId} onChange={e => setEmpId(e.target.value)} />
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--foreground)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Password</label>
              <input type="password" placeholder="Enter your password" value={password} onChange={e => setPassword(e.target.value)} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: '0.875rem', color: 'var(--muted-foreground)' }}>
                <input type="checkbox" checked={remember} onChange={e => setRemember(e.target.checked)} style={{ width: 'auto' }} />
                Remember Me
              </label>
              <button style={{ background: 'none', border: 'none', color: '#0f2167', fontSize: '0.875rem', cursor: 'pointer', fontWeight: 500, fontFamily: "'Source Sans 3', sans-serif" }}>Forgot Password?</button>
            </div>
            <button className="btn-primary" style={{ width: '100%', padding: '12px', fontSize: '0.9rem' }} onClick={handleLogin}>
              Sign In to Platform
            </button>
          </div>

          <div style={{ marginTop: 24, textAlign: 'center' }}>
            <p style={{ fontSize: '0.75rem', color: 'var(--muted-foreground)', lineHeight: 1.7 }}>
              For access issues, contact your System Administrator<br />
              or the IT Helpdesk at <span style={{ color: '#0f2167', fontWeight: 600 }}>helpdesk@cmpdi.gov.in</span>
            </p>
          </div>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 20, alignItems: 'center' }}>
            <div style={{ background: '#eef1f7', borderRadius: 3, padding: '4px 10px', fontSize: '0.7rem', fontWeight: 700, color: '#0f2167', letterSpacing: '0.06em' }}>CMPDI</div>
            <div style={{ width: 1, height: 16, background: 'var(--border)' }} />
            <div style={{ background: '#eef1f7', borderRadius: 3, padding: '4px 10px', fontSize: '0.7rem', fontWeight: 700, color: '#0f2167', letterSpacing: '0.06em' }}>Coal India Limited</div>
            <div style={{ width: 1, height: 16, background: 'var(--border)' }} />
            <div style={{ fontSize: '0.68rem', color: 'var(--muted-foreground)' }}>Ministry of Coal, GoI</div>
          </div>
        </div>
      </div>
    </div>
  );
}