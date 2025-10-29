# TODO: Import Connection, select, insert, update, delete, desc from sqlalchemy
# TODO: Import table definitions from .schema
# TODO: Import time module

# TODO: Define upsert_assets(conn: Connection, assets: list[dict]) -> int
# TODO: Define insert_prices(conn: Connection, prices: list[dict]) -> int
# TODO: Define get_latest_prices(conn: Connection, asset_ids: list[str]) -> dict[str, dict]
# TODO: Define get_prices_for_asset(conn: Connection, asset_id: str, limit: int = 100) -> list[dict]
# TODO: Define get_all_assets(conn: Connection) -> list[dict]
# TODO: Define get_all_holdings(conn: Connection) -> list[dict]
# TODO: Define insert_holding(conn: Connection, asset_id: str, amount: float, avg_buy_price: float) -> int
# TODO: Define get_active_alerts(conn: Connection) -> list[dict]
# TODO: Define get_all_alerts(conn: Connection) -> list[dict]
# TODO: Define insert_alert(conn: Connection, alert: dict) -> int
# TODO: Define update_alert_fired(conn: Connection, alert_id: int, ts: int) -> None
# TODO: Define toggle_alert(conn: Connection, alert_id: int, active: bool) -> None
# TODO: Define asset_exists(conn: Connection, asset_id: str) -> bool

from sqlalchemy import Connection, select, insert, update, desc, func
from sqlalchemy.exc import IntegrityError
import time

from .schema import assets_table, prices_table, holdings_table, alerts_table

def upsert_assets(conn: Connection, assets: list[dict]) -> int:
    if assets:
        stmt = insert(assets_table).prefix_with("OR REPLACE")
        conn.execute(stmt, assets)
        return len(assets)
    else:
        return 0

def insert_prices(conn: Connection, prices: list[dict]) -> int:
    if prices:
        stmt = insert(prices_table).prefix_with("OR IGNORE")
        conn.execute(stmt, prices)
        return len(prices)
    else:
        return 0

def insert_holding(conn: Connection, asset_id: str, amount: float, avg_buy_price: float) -> int:
    created_at = int(time.time())
    stmt = insert(holdings_table).values(asset_id=asset_id, amount=amount, avg_buy_price=avg_buy_price, created_at=created_at)
    result = conn.execute(stmt)
    return result.lastrowid

def insert_alert(conn: Connection, alert: dict) -> int:
    created_at = int(time.time())
    stmt = insert(alerts_table).values(asset_id=alert["asset_id"], type=alert["type"], op=alert["op"], threshold=alert["threshold"], created_at=created_at)
    result = conn.execute(stmt)
    return result.lastrowid

def update_alert_fired(conn: Connection, alert_id: int, ts: int):
    stmt = update(alerts_table).where(alerts_table.c.id == alert_id).values(last_fired_ts=ts)
    conn.execute(stmt)

def toggle_alert(conn: Connection, alert_id: int, active: bool):
    active_int = 1 if active else 0
    stmt = update(alerts_table).where(alerts_table.c.id == alert_id).values(active=active_int)
    conn.execute(stmt)
