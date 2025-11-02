from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import time

from app.config import settings
from app.db.connection import get_engine
from app.db.operations import get_all_assets, get_prices_for_asset
from ingest import run_ingest_once

# TODO: Define POST /ingest/trigger endpoint

router = APIRouter(prefix="/api", tags=["assets"])

@router.get("/assets")
def get_assets():
    try:
        engine = get_engine(settings.db_path)
        with engine.begin() as conn:
            all_assets = get_all_assets(conn)
        return all_assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prices/{asset_id}")
def get_prices(asset_id: str, limit: int = Query(default=100, ge=1, le=1000)):
    try:
        engine = get_engine(settings.db_path)
        with engine.begin() as conn:
            prices = get_prices_for_asset(conn, asset_id, limit)
        if not prices:
            raise HTTPException(status_code=404, detail=f"No prices found for asset {asset_id}")
        return prices
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))     

@router.post("/ingest")
def trigger_ingest(ids: Optional[str] = Query(default=None)):
    try:
        if ids:
            asset_ids = ids.split(",")
        else:
            asset_ids = settings.asset_ids.split(",")
        summary = run_ingest_once(asset_ids)
        return {
            "status": "success",
            "assets_count": summary["assets_count"],
            "prices_count": summary["prices_count"],
            "timestamp": int(time.time())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))     