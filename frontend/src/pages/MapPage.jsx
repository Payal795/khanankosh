import { useEffect, useMemo, useState } from "react";
import MapView from "./MapView.jsx";
import { api } from "./api.js";

const LAYERS = [["zone", "Suitability zones"], ["score", "Suitability score"], ["ndvi", "NDVI"], ["bsi", "Bare soil index"], ["slope", "Slope (SRTM)"], ["elev", "Elevation (SRTM)"], ["rgb", "Sentinel-2 true colour"]];

export default function App() {
  const [fields, setFields] = useState(null);
  const [meth, setMeth] = useState(null);
  const [q, setQ] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [active, setActive] = useState(["zone"]);
  const [opacity, setOpacity] = useState(0.8);
  const [water, setWater] = useState(null);
  const [waterOn, setWaterOn] = useState(false);
  const [waterErr, setWaterErr] = useState("");

  useEffect(() => {
    api.coalfields().then(setFields).catch((e) => setErr(`Cannot reach backend: ${e.message}`));
    api.methodology().then(setMeth).catch(() => {});
  }, []);

  const list = useMemo(() => {
    if (!fields) return [];
    const s = q.trim().toLowerCase();
    return fields.features.map((f) => f.properties)
      .filter((p) => !s || `${p.name} ${p.state}`.toLowerCase().includes(s))
      .sort((a, b) => b.featured - a.featured || a.name.localeCompare(b.name));
  }, [fields, q]);

  const sel = fields?.features.find((f) => f.properties.id === selectedId)?.properties;
  const select = (id) => { setSelectedId(id); setResult(null); setWater(null); setWaterOn(false); setWaterErr(""); setErr(""); };
  const run = async (fieldId = selectedId) => {
    if (!fieldId) return;
    setBusy(true); setErr(""); setResult(null);
    try { setResult(await api.analyze(fieldId)); } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };
  const runWater = async () => {
    setBusy(true); setWaterErr("");
    try {
      const r = await api.water(selectedId);
      if (!r.water_analysis) throw new Error(r.message || "No water data returned");
      setWater(r.water_analysis); setWaterOn(true);
    } catch (e) { setWaterErr(e.message); } finally { setBusy(false); }
  };
  const toggle = (k) => setActive((a) => (a.includes(k) ? a.filter((x) => x !== k) : [...a, k]));
  const zones = meth ? [...meth.zones].sort((a, b) => b.value - a.value) : [];
  const A = result?.assessment;

  return (
    <div className="gis-page">
    <style>{`
      @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Roboto:wght@400;500;700&display=swap');

      .mi-condensed {
        font-family: 'Oswald', 'Arial Narrow', sans-serif;
        letter-spacing: 0.02em;
        text-transform: uppercase;
      }
    `}</style>
      <div className="gis-layout">
        <aside className="gis-sidebar">
          <header className="gis-intro">
            <p className="gis-eyebrow">Spatial planning</p>
            <h1 className="mi-condensed"
            style={{ fontSize: '2.8rem', fontWeight: 700, margin: '0 0 16px', lineHeight: 1.1 }}
          >GIS Feasibility Engine</h1>
            <p>Choose a coalfield to explore its landscape and get a clear, preliminary view of its suitability for reclamation.</p>
          </header>

          <div className="gis-search-wrap">
            <label className="gis-label" htmlFor="coalfield-search">Coalfields</label>
            <input id="coalfield-search" className="gis-search" placeholder="Search coalfield or state" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>

          <ul className="gis-list">
            {list.slice(0, 80).map((p) => (
              <li key={p.id} className={`gis-field${p.id === selectedId ? " is-selected" : ""}`}>
                <button className="gis-field-select" onClick={() => select(p.id)} aria-pressed={p.id === selectedId}>
                  <span>{p.name}{p.featured && <em> (Featured)</em>}</span>
                  <small>{p.state} · {p.area_km2} km²</small>
                </button>
                {p.id === selectedId && (
                  <button className="gis-primary" disabled={busy} onClick={() => run(p.id)}>
                    {busy ? "Running analysis…" : "Run suitability analysis"}
                  </button>
                )}
              </li>
            ))}
          </ul>

          {err && <div className="gis-error" role="alert">{err}</div>}

          {result && (
            <div className="gis-results">
              <section className="gis-section">
                <p className="gis-eyebrow">Preliminary assessment</p>
                <div className={`gis-badge ${A.tone}`}>{A.rating}</div>
                <p className="gis-summary">{A.summary}</p>
                <div className="gis-bar">{zones.map((z) => <i key={z.value} title={`${z.label}: ${A.zone_pct[z.label]}%`} style={{ width: `${A.zone_pct[z.label]}%`, background: z.color }} />)}</div>
                <ul className="gis-legend">{zones.map((z) => <li key={z.value}><b style={{ background: z.color }} />{z.label}<span>{A.zone_pct[z.label]}% · {Math.round(result.stats.zone_area_ha[z.label]).toLocaleString()} ha</span></li>)}</ul>
              </section>

              <section className="gis-section">
                <h2>Map layers</h2>
                {LAYERS.map(([k, label]) => <label key={k} className="gis-check"><input type="checkbox" checked={active.includes(k)} onChange={() => toggle(k)} />{label}</label>)}
                <label className="gis-slider"><span>Opacity</span><input type="range" min="0.2" max="1" step="0.05" value={opacity} onChange={(e) => setOpacity(+e.target.value)} /></label>
              </section>

              <section className="gis-section">
                <h2>Area indicators</h2>
                <dl className="gis-metrics">
                  <div><dt>Suitability score</dt><dd>{result.stats.mean.score}</dd></div>
                  <div><dt>NDVI</dt><dd>{result.stats.mean.ndvi}</dd></div>
                  <div><dt>Bare soil index</dt><dd>{result.stats.mean.bsi}</dd></div>
                  <div><dt>Slope</dt><dd>{result.stats.mean.slope}°</dd></div>
                  <div><dt>Elevation</dt><dd>{Math.round(result.stats.mean.elevation)} m</dd></div>
                  <div><dt>Sentinel-2 scenes</dt><dd>{result.stats.n_scenes}</dd></div>
                </dl>
                {meth && <details><summary>How the score is built</summary>
                  <ul className="gis-notes">{Object.entries(meth.weights).map(([k, w]) => <li key={k}><b>{k} · {Math.round(w * 100)}%</b> {meth.method[k]}</li>)}<li>{meth.method.rule}</li></ul></details>}
              </section>

              <section className="gis-section">
                <h2>Recommendations</h2>
                <ul className="gis-notes">{A.recommendations.map((r, i) => <li key={i}>{r}</li>)}</ul>
                <details><summary>Limitations</summary><ul className="gis-notes">{A.caveats.map((r, i) => <li key={i}>{r}</li>)}</ul></details>
              </section>

              {result.water_available && (
                <section className="gis-section">
                  <h2>Water analysis</h2>
                  <p className="gis-note">This analysis is not included in the suitability score.</p>
                  {!water ? (<><button className="gis-secondary" disabled={busy} onClick={runWater}>{busy ? "Running analysis…" : "Analyse water bodies"}</button>{waterErr && <div className="gis-error" role="alert">{waterErr}</div>}</>) : (<>
                    <label className="gis-check"><input type="checkbox" checked={waterOn} onChange={(e) => setWaterOn(e.target.checked)} />Show water overlay</label>
                    <dl className="gis-metrics">
                      <div><dt>Water area</dt><dd>{water.water_area_km2} km²</dd></div>
                      <div><dt>Water cover</dt><dd>{water.water_cover_percent}%</dd></div>
                      <div><dt>Mean NDWI</dt><dd>{water.mean_ndwi}</dd></div>
                    </dl>
                  </>)}
                </section>
              )}
            </div>
          )}
        </aside>
        <MapView fields={fields} selectedId={selectedId} onSelect={select} layers={result?.layers} active={active} opacity={opacity} water={waterOn ? water?.water_tile_url : null} />
      </div>
    </div>
  );
}
