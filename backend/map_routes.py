import time
from fastapi import APIRouter, HTTPException
import data, scoring

router = APIRouter(tags=["Map & Reclamation Engine"])

_cache: dict = {}  # Earth Engine tile URLs expire, so cache for 6 hours only
TTL = 6 * 3600


def _key(k):
    try:
        return data.resolve(k)
    except KeyError:
        raise HTTPException(404, f"Unknown coalfield '{k}'")


def _cached(name, fid, fn):
    hit = _cache.get((name, fid))
    if hit and time.time() - hit[0] < TTL:
        return hit[1]
    try:
        val = fn()
    except Exception as e:
        raise HTTPException(
            502, f"Earth Engine error: {e}. Check GEE_PROJECT / authentication."
        )
    _cache[(name, fid)] = (time.time(), val)
    return val


@router.get("/api/health")
def health():
    return {"status": "ok", "coalfields": len(data.load())}


@router.get("/api/coalfields")
def coalfields():
    return data.all_fields()


@router.get("/api/coalfields/{key}")
def coalfield(key: str):
    return data.one(_key(key))


@router.get("/api/methodology")
def methodology():
    return {
        "weights": scoring.WEIGHTS,
        "zones": [
            {"value": v, "label": l, "color": c, "min": m}
            for v, l, c, m in scoring.ZONES
        ],
        "method": scoring.METHOD,
    }


@router.get("/api/analyze/{key}")
def analyze(key: str):
    fid = _key(key)
    f = data.one(fid)  # validate before touching Earth Engine
    import gee_engine

    res = _cached(
        "suit",
        fid,
        lambda: gee_engine.analyse(
            data.aoi_geometry(fid), f["properties"]["area_km2"]
        ),
    )
    return {
        "id": fid,
        "name": f["properties"]["name"],
        "state": f["properties"]["state"],
        "layers": res["layers"],
        "stats": res["stats"],
        "assessment": scoring.assess(res["stats"]),
        "water_available": fid in data.FEATURED.values(),
    }


# ---- Backwards-compatible endpoints from original Jharia/Korba app -------------------------
def _featured(mine_id: str) -> str:
    """Accepts 'jharia'/'korba' or the shapefile ID; only those two coalfields are allowed."""
    fid = _key(mine_id)
    if fid not in data.FEATURED.values():
        raise HTTPException(
            404, "Water analysis is only available for Jharia and Korba"
        )
    return fid


@router.get("/gis/boundary/{mine_id}")
def legacy_boundary(mine_id: str):
    f = data.one(_featured(mine_id))
    return {
        "mine_id": mine_id,
        "mine_name": f["properties"]["name"] + " Coalfield",
        "geometry": f["geometry"],
    }


@router.get("/gis/water/{mine_id}")
def legacy_water(mine_id: str):
    """Original NDWI water analysis, kept for Jharia and Korba only."""
    fid = _featured(mine_id)
    import gee_engine

    w = _cached(
        "water", fid, lambda: gee_engine.water_ndwi(data.aoi_geometry(fid))
    )
    return {
        "mine_id": mine_id,
        "mine_name": data.one(fid)["properties"]["name"] + " Coalfield",
        "status": "success",
        "water_analysis": w,
    }