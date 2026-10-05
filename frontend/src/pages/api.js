const configuredBase = import.meta.env.VITE_API_URL || "";
const BASE = configuredBase
  ? `${configuredBase.startsWith("http") ? "" : "https://"}${configuredBase}`.replace(/\/+$/, "")
  : "";

export const apiUrl = (path) => `${BASE}${path.startsWith("/") ? path : `/${path}`}`;

async function get(path) {
  const r = await fetch(apiUrl(path));
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `Request failed (${r.status})`);
  return r.json();
}

export const api = {
  coalfields: () => get("/api/coalfields"),
  methodology: () => get("/api/methodology"),
  analyze: (id) => get(`/api/analyze/${id}`),
  water: (id) => get(`/gis/water/${id}`),
};