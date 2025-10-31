# TODO: Import httpx, time, logging
# TODO: Setup logger

# TODO: Define fetch_markets(asset_ids: list[str], vs_currency: str = "eur", timeout: int = 10, retries: int = 3) -> list[dict]
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
