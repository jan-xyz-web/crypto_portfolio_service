
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

def asset_exists(conn: Connection, asset_id: str) -> bool:
    stmt = select(assets_table).where(assets_table.c.id == asset_id)
    result = conn.execute(stmt)
    return bool(result.fetchone())

def get_all_assets(conn: Connection) -> list[dict]:
    stmt = select(assets_table)
    result = conn.execute(stmt)
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

def get_all_holdings(conn: Connection) -> list[dict]:
    stmt = select(holdings_table)
    result = conn.execute(stmt)
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

def get_all_alerts(conn: Connection) -> list[dict]:
    stmt = select(alerts_table)
    result = conn.execute(stmt)
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

def get_all_active_alerts(conn: Connection) -> list[dict]:
    stmt = select(alerts_table).where(alerts_table.c.active == 1)
    result = conn.execute(stmt)
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

def get_prices_for_asset(conn: Connection, asset_id: str, limit: int = 100) -> list[dict]:
    stmt = select(prices_table).where(prices_table.c.asset_id == asset_id).order_by(desc(prices_table.c.ts)).limit(limit)
    result = conn.execute(stmt)
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

def get_latest_prices(conn: Connection, asset_ids: list[str]) -> dict[str, dict]:
    subq = (
        select(
            prices_table.c.asset_id,
            func.max(prices_table.c.ts).label("max_ts"),
        )
        .where(prices_table.c.asset_id.in_(asset_ids))
        .group_by(prices_table.c.asset_id)
        .subquery()
    )

    stmt = (
        select(prices_table)
        .join(
            subq,
            (prices_table.c.asset_id == subq.c.asset_id)
            & (prices_table.c.ts == subq.c.max_ts),
        )
        .where(prices_table.c.asset_id.in_(asset_ids))
    )

    result = conn.execute(stmt)
    rows = result.fetchall()

    latest_by_asset: dict[str, dict] = {}
    for row in rows:
        row_dict = dict(row._mapping)
        latest_by_asset[row_dict["asset_id"]] = row_dict
    return latest_by_asset
    
