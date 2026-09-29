"""AOI source: USGS OFR 2011-1296 IndiaCoalfields.shp (coalfield polygons, EPSG:4240).
IndiaAnalyticalData.shp is coal-sample POINT chemistry and is deliberately not used as AOI."""
import functools, json, os
from pathlib import Path
import geopandas as gpd

SHP = Path(os.getenv("COALFIELD_SHP", Path(__file__).resolve().parent / "data/IndiaCoalfields/IndiaCoalfields.shp"))
FEATURED = {"jharia": "600000", "korba": "303000"}   # slug -> shapefile ID


@functools.lru_cache(maxsize=1)
def load() -> gpd.GeoDataFrame:
    g = gpd.read_file(SHP).to_crs(4326)               # source CRS is Indian 1975 (EPSG:4240)
    g["geometry"] = g.geometry.make_valid()
    g["id"] = g["ID"].astype(str)
    g["area_km2"] = (g.to_crs(6933).area / 1e6).round(1)
    g["featured"] = g["id"].isin(FEATURED.values())
    return g.set_index("id", drop=False)


def resolve(key: str) -> str:
    key = FEATURED.get(key.lower(), key)
    if key not in load().index:
        raise KeyError(key)
    return key


def _fc(g, tol=0.0):
    g = g.copy()
    if tol: g["geometry"] = g.geometry.simplify(tol, preserve_topology=True)
    g = g.rename(columns={"Coalfield": "name", "State": "state"})
    return json.loads(g[["id", "name", "state", "area_km2", "featured", "geometry"]].to_json())


def all_fields(): return _fc(load(), 0.002)
def one(key): return _fc(load().loc[[resolve(key)]])["features"][0]
def aoi_geometry(key, tol=0.0005):
    """Simplified geometry (GeoJSON dict) sent to Earth Engine."""
    g = load().loc[resolve(key)].geometry.simplify(tol, preserve_topology=True)
    return json.loads(gpd.GeoSeries([g]).to_json())["features"][0]["geometry"]
