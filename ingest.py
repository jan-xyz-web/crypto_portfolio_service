import argparse
import signal
import time
import logging
import sys
from datetime import datetime

from app.config import settings
from app.db.connection import get_engine
from app.db.schema import create_tables
from app.db.operations import upsert_assets, insert_prices
from app.services.coingecko import fetch_markets, normalize_market_data

# TODO: Setup logging
# TODO: Create shutdown_flag global variable

# TODO: Define signal_handler(signum, frame)
# TODO: Define run_ingest_once(asset_ids: list[str]) -> dict
# TODO: Define run_ingest_loop(asset_ids: list[str], interval: int) -> None
# TODO: Define main()

# TODO: Add if __name__ == "__main__": main()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

shutdown_flag = False

def signal_handler(signum, frame):
    global shutdown_flag
    logger.info("Shutdown signal received, finishing current cycle...")
    shutdown_flag = True

def run_ingest_once(asset_ids: list[str]) -> dict:
    try:
        ts = int(time.time())
        raw_data = fetch_markets(asset_ids)
        normalized_data = normalize_market_data(raw_data, ts)
        normalized_assets = normalized_data[0]
        normalized_prices = normalized_data[1]
        engine = get_engine(settings.db_path)
        with engine.begin() as conn:
            assets_count = upsert_assets(conn, normalized_assets)
            prices_count = insert_prices(conn, normalized_prices)

        return {
            "assets_count": assets_count,
            "prices_count": prices_count,
            "errors": 0
        }

    except Exception as e:
        logger.error(f"Unexpected error during ingest: {e}")
        return {"assets_count": 0, "prices_count": 0, "errors": 1}

def run_ingest_loop(asset_ids: list[str], interval: int):
    global shutdown_flag
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    logger.info(f"Starting ingest loop, running every {interval} seconds...")
    while not shutdown_flag:
        summary = run_ingest_once(asset_ids)
        logger.info(f"Ingested {summary['assets_count']} assets, {summary['prices_count']} prices")
        time.sleep(interval)
    logger.info("Shutting down gracefully...")

def main():
    parser = argparse.ArgumentParser(description="Crypto price ingest worker")
    parser.add_argument("--ids", type=str, help="Comma-separated asset IDs")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=settings.ingest_interval, 
                       help="Run every N seconds (default from settings)")
    args = parser.parse_args()
    if args.ids:
        asset_ids = args.ids.split(",")
    else:
        asset_ids = settings.asset_ids.split(",")
    engine = get_engine(settings.db_path)
    create_tables(engine)
    logger.info(f"Database ready at {settings.db_path}")
    if args.once:
        summary = run_ingest_once(asset_ids)
        logger.info(f"Summary: {summary}")
    else:
        run_ingest_loop(asset_ids, args.interval)

if __name__ == "__main__":
    main()