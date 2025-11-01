# TODO: Import httpx, time, logging
# TODO: Setup logger

# TODO: Define normalize_market_data(raw: list[dict], ts: int) -> tuple[list[dict], list[dict]]

import httpx
import time
import logging
from app.config import settings

logger = logging.getLogger(__name__)

def fetch_markets(asset_ids: list[str], vs_currency: str = settings.price_currency, timeout: float = settings.http_timeout, 
retries: int = settings.http_retries, backoff: float = settings.http_backoff) -> list[dict]:
    url = f"{settings.coingecko_base_url}/coins/markets"
    params = {"vs_currency": vs_currency, "ids": ",".join(asset_ids)}
    with httpx.Client(timeout=timeout) as client:
        for attempt in range(retries + 1):
            try:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
            except httpx.TimeoutException:
                if attempt == retries:
                    raise
                logger.warning(f"Request failed (attempt {attempt + 1}/{retries + 1}), retrying...")
                time.sleep(backoff * (2 ** attempt))
            except httpx.HTTPStatusError as e:
                if e.response.status_code in {429} or 500 <= e.response.status_code < 600:
                    if attempt == retries:
                        raise
                    logger.warning(f"Request failed (attempt {attempt + 1}/{retries + 1}), retrying...")
                    time.sleep(backoff * (2 ** attempt))
                else:
                    raise

def normalize_market_data(raw: list[dict], ts: int) ->  tuple[list[dict], list[dict]]:
    assets_data = []
    prices_data = []
    for coin in raw:
        assets_data.append({"id": coin["id"], "symbol": coin["symbol"], "name": coin["name"]})
        if coin["current_price"] is not None:
            prices_data.append({"asset_id": coin["id"], "ts": ts, "price": coin["current_price"], "mcap": coin["market_cap"], "vol": coin["total_volume"]})
    return (assets_data, prices_data)