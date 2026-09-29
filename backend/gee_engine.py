"""Google Earth Engine: Sentinel-2 SR composite + SRTM -> suitability score, zones, statistics, tiles."""
import datetime as dt, os, ee
from scoring import WEIGHTS, ZONES, SLOPE_HARD_LIMIT_DEG

_ready = False
def init():
    global _ready
    if _ready: return
    proj, sa, key = os.getenv("GEE_PROJECT"), os.getenv("GEE_SERVICE_ACCOUNT"), os.getenv("GEE_KEY_FILE")
    if sa and key: ee.Initialize(ee.ServiceAccountCredentials(sa, key), project=proj)
    else: ee.Initialize(project=proj)          # after a one-time `earthengine authenticate`
    _ready = True


def _s2(geom, days=365, cloud=30):
    end = ee.Date(dt.date.today().isoformat())
    def clean(im):
        scl = im.select("SCL")
        ok = scl.neq(1).And(scl.neq(3)).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10))
        return im.updateMask(ok).select(["B2", "B3", "B4", "B8", "B11"]).divide(10000)
    col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(geom)
           .filterDate(end.advance(-days, "day"), end).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud)))
    return col.map(clean).median(), col.size()


def _tiles(img, vis):
    return img.visualize(**vis).getMapId()["tile_fetcher"].url_format


def analyse(aoi_geojson: dict, area_km2: float) -> dict:
    init()
    geom = ee.Geometry(aoi_geojson, None, False)
    s2, n = _s2(geom)
    ndvi = s2.normalizedDifference(["B8", "B4"]).rename("ndvi")
    bsi = s2.expression("((sw+r)-(n+b))/((sw+r)+(n+b))", {"sw": s2.select("B11"), "r": s2.select("B4"),
                        "n": s2.select("B8"), "b": s2.select("B2")}).rename("bsi")
    dem = ee.Image("USGS/SRTMGL1_003").select("elevation")
    slope = ee.Terrain.slope(dem).rename("slope")
    tpi = dem.subtract(dem.focalMean(300, "circle", "meters")).rename("tpi")

    s_slope = ee.Image(0.1).where(slope.lte(25), 0.4).where(slope.lte(15), 0.75).where(slope.lte(8), 1.0)
    s_ndvi = ndvi.divide(0.6).clamp(0, 1)
    s_bsi = ee.Image(1).subtract(bsi.add(0.1).divide(0.4)).clamp(0, 1)
    s_tpi = ee.Image(1).subtract(tpi.divide(15)).clamp(0, 1)
    score = (s_slope.multiply(WEIGHTS["slope"]).add(s_ndvi.multiply(WEIGHTS["ndvi"]))
             .add(s_bsi.multiply(WEIGHTS["bsi"])).add(s_tpi.multiply(WEIGHTS["tpi"]))).rename("score")

    zone = ee.Image(1)
    for val, _, _, lo in sorted(ZONES, key=lambda z: z[3]):
        if lo > 0: zone = zone.where(score.gte(lo), val)
    zone = zone.where(slope.gt(SLOPE_HARD_LIMIT_DEG), 1).rename("zone")

    stack = ee.Image.cat([score, ndvi, bsi, slope, dem.rename("elev"), zone]).clip(geom)
    stack = stack.updateMask(s2.select("B4").mask().Or(dem.mask()))
    zone_area = (ee.Image.pixelArea().divide(1e4).addBands(stack.select("zone"))
                 .reduceRegion(ee.Reducer.sum().group(1, "zone"), geom, 30, maxPixels=1e10, tileScale=4, bestEffort=True))
    means = stack.select(["score", "ndvi", "bsi", "slope", "elev"]).reduceRegion(
        ee.Reducer.mean(), geom, 30, maxPixels=1e10, tileScale=4, bestEffort=True)
    out = ee.Dictionary({"zones": zone_area.get("groups"), "mean": means, "n_scenes": n}).getInfo()

    label = {v: name for v, name, _, _ in ZONES}
    area = {name: 0.0 for _, name, _, _ in ZONES}
    for g in out["zones"] or []: area[label[int(g["zone"])]] = round(g["sum"], 1)
    m = {k: round(v or 0, 3) for k, v in out["mean"].items()}
    pal = lambda *c: list(c)
    vis = {"score": dict(min=0, max=1, palette=pal("a5472f", "d9a441", "a8b545", "2f6b3a")),
           "zone": dict(min=1, max=4, palette=[z[2].lstrip("#") for z in sorted(ZONES, key=lambda z: z[0])]),
           "ndvi": dict(min=0, max=0.8, palette=pal("8c5a3c", "e6d9a0", "7fb85a", "1d5a2a")),
           "bsi": dict(min=-0.2, max=0.4, palette=pal("2f6b3a", "e6d9a0", "a5472f")),
           "slope": dict(min=0, max=35, palette=pal("f4efe1", "d9a441", "8c3b23", "3b1a12")),
           "elev": dict(min=float(m["elev"]) - 80, max=float(m["elev"]) + 120, palette=pal("2b4a3a", "c9c08a", "ffffff"))}
    layers = {k: _tiles(stack.select(k), v) for k, v in vis.items()}
    layers["rgb"] = _tiles(s2.clip(geom), dict(bands=["B4", "B3", "B2"], min=0.02, max=0.3))
    stats = {"zone_area_ha": area, "mean": {"score": m["score"], "ndvi": m["ndvi"], "bsi": m["bsi"],
             "slope": m["slope"], "elevation": m["elev"]}, "area_km2": area_km2, "n_scenes": out["n_scenes"]}
    return {"layers": layers, "stats": stats}


def water_ndwi(aoi_geojson: dict) -> dict:
    """Legacy Jharia/Korba water layer (same response shape as the original /gis/water endpoint).
    Informational only: never used in the suitability score."""
    init()
    geom = ee.Geometry(aoi_geojson, None, False)
    s2, _ = _s2(geom)
    ndwi = s2.normalizedDifference(["B3", "B8"]).rename("ndwi").clip(geom)
    water = ndwi.gt(0)
    r = ee.Dictionary({
        "area": ee.Image.pixelArea().updateMask(water).reduceRegion(ee.Reducer.sum(), geom, 30, maxPixels=1e10, tileScale=4, bestEffort=True).get("area"),
        "total": ee.Image.pixelArea().clip(geom).reduceRegion(ee.Reducer.sum(), geom, 30, maxPixels=1e10, tileScale=4, bestEffort=True).get("area"),
        "mean": ndwi.reduceRegion(ee.Reducer.mean(), geom, 30, maxPixels=1e10, tileScale=4, bestEffort=True).get("ndwi")}).getInfo()
    a, t = (r["area"] or 0), (r["total"] or 1)
    return {"water_tile_url": _tiles(water.selfMask(), dict(palette=["1e6fd9"])), "water_area_km2": round(a / 1e6, 2),
            "water_cover_percent": round(100 * a / t, 2), "mean_ndwi": round(r["mean"] or 0, 3)}
