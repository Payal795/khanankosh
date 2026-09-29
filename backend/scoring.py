"""Suitability model definition + rule-based preliminary assessment (no LLM is called)."""
WEIGHTS = {"slope": 0.30, "ndvi": 0.30, "bsi": 0.25, "tpi": 0.15}
ZONES = [  # value, label, colour, min score
    (4, "High", "#2f6b3a", 0.75), (3, "Moderate", "#a8b545", 0.55),
    (2, "Low", "#d9a441", 0.35), (1, "Very low / constrained", "#a5472f", 0.0)]
SLOPE_HARD_LIMIT_DEG = 30
METHOD = {
    "slope": "SRTM 30 m slope: <=8° =1.0, <=15° =0.75, <=25° =0.4, else 0.1",
    "ndvi": "Sentinel-2 median NDVI / 0.6, clamped 0-1 (capacity to carry vegetation)",
    "bsi": "Sentinel-2 Bare Soil Index: -0.1 =1.0 falling linearly to 0 at 0.3 (exposed spoil/soil penalised)",
    "tpi": "SRTM elevation minus 300 m focal mean: <=0 m =1.0 falling to 0 at +15 m (exposed dump crests penalised)",
    "rule": f"Slope > {SLOPE_HARD_LIMIT_DEG}° is forced into the lowest zone regardless of score",
}


def assess(stats: dict) -> dict:
    a = stats["zone_area_ha"]; tot = sum(a.values()) or 1
    pct = {k: round(100 * v / tot, 1) for k, v in a.items()}
    good = pct["High"] + pct["Moderate"]
    m = stats["mean"]
    if good >= 60: rating, tone = "Feasible", "good"
    elif good >= 35: rating, tone = "Conditionally feasible", "warn"
    else: rating, tone = "Constrained", "bad"
    recs = []
    if pct["High"] >= 10: recs.append(f"{pct['High']}% of the area is High suitability: prioritise direct native-species plantation and topsoil placement here.")
    if pct["Moderate"] >= 10: recs.append(f"{pct['Moderate']}% is Moderate: plan soil amelioration (organic matter, nutrient correction) before planting.")
    if pct["Low"] >= 10: recs.append(f"{pct['Low']}% is Low: use terracing or contour trenches, soil cover and hardy grasses/legumes first.")
    if pct["Very low / constrained"] >= 10: recs.append(f"{pct['Very low / constrained']}% is very low or slope-constrained: needs geotechnical regrading, or should be left for natural succession.")
    if m["bsi"] > 0.1: recs.append("High mean bare-soil index suggests widespread exposed spoil; erosion control should come before planting.")
    return {"rating": rating, "tone": tone, "suitable_pct": round(good, 1), "zone_pct": pct,
            "summary": f"{rating}: {good:.0f}% of the {stats['area_km2']:.0f} km² area scores High or Moderate for vegetation-oriented reclamation "
                       f"(mean score {m['score']:.2f}, mean NDVI {m['ndvi']:.2f}, mean slope {m['slope']:.1f}°).",
            "recommendations": recs,
            "caveats": ["Preliminary desk screening from 30 m satellite/DEM data; it is not a substitute for soil sampling, geotechnical or hydrological survey.",
                        "Reflects current conditions only (no temporal analysis). Water, access and coal-quality factors are intentionally excluded.",
                        "Polygons are 2011 USGS/GSI coalfield extents, not current lease or mine-plan boundaries."]}
