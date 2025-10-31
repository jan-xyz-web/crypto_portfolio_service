import pytest
import time
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.db import schema, operations

# TODO: Define test_get_latest_prices_multi_asset()
# TODO: Define test_holdings_insert_and_fetch()
# TODO: Define test_alerts_toggle_active()

@pytest.fixture
def test_engine():
    engine = create_engine("sqlite:///:memory:", poolclass=StaticPool)
    schema.create_tables(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def test_conn(test_engine):
    conn = test_engine.connect()
    conn.begin()
    yield conn
    conn.rollback()
    conn.close()

def test_create_tables_idempotent(test_engine, test_conn):
    schema.create_tables(test_engine)
    operations.upsert_assets(test_conn, [{"id": "test", "symbol": "TST", "name": "Test"}])
    assert operations.asset_exists(test_conn, "test") == True

def test_upsert_assets_duplicate_id(test_conn):
    operations.upsert_assets(test_conn, [{"id": "test2", "symbol": "ABC", "name": "Test2"}])
    operations.upsert_assets(test_conn, [{"id": "test2", "symbol": "DEF", "name": "Test2"}])

    all_assets = operations.get_all_assets(test_conn)
    test2_assets = [asset for asset in all_assets if asset["id"] == "test2"]
    assert len(test2_assets) == 1
    asset = test2_assets[0]
    assert asset["symbol"] == "DEF"

def test_insert_prices_duplicate_pk(test_conn):
    operations.upsert_assets(test_conn, [{"id": "btc", "symbol": "BTC", "name": "Bitcoin"}])
    price1 = {"asset_id": "btc", "ts": 1000, "price": 50000.0, "mcap": 10000000.0, "vol": 10000.0}
    operations.insert_prices(test_conn, [price1])
    price2 = {"asset_id": "btc", "ts": 1000, "price": 100000.0, "mcap": 10000000.0, "vol": 10000.0}
    operations.insert_prices(test_conn, [price2])
    prices = operations.get_prices_for_asset(test_conn, "btc")
    prices_at_ts = [price for price in prices if price["ts"] == 1000]
    assert len(prices_at_ts) == 1
    assert prices_at_ts[0]["price"] == 50000.0


def test_get_latest_prices_multi_asset(test_conn):
    # Arrange: create assets and multiple prices
    operations.upsert_assets(
        test_conn,
        [
            {"id": "btc", "symbol": "BTC", "name": "Bitcoin"},
            {"id": "eth", "symbol": "ETH", "name": "Ethereum"},
        ],
    )

    operations.insert_prices(
        test_conn,
        [
            {"asset_id": "btc", "ts": 1000, "price": 10.0, "mcap": 1.0, "vol": 1.0},
            {"asset_id": "btc", "ts": 2000, "price": 20.0, "mcap": 2.0, "vol": 2.0},
            {"asset_id": "eth", "ts": 1500, "price": 30.0, "mcap": 3.0, "vol": 3.0},
            {"asset_id": "eth", "ts": 2500, "price": 40.0, "mcap": 4.0, "vol": 4.0},
        ],
    )

    # Act
    latest = operations.get_latest_prices(test_conn, ["btc", "eth"])

    # Assert
    assert set(latest.keys()) == {"btc", "eth"}
    assert latest["btc"]["ts"] == 2000 and latest["btc"]["price"] == 20.0
    assert latest["eth"]["ts"] == 2500 and latest["eth"]["price"] == 40.0


def test_holdings_insert_and_fetch(test_conn):
    # Arrange: create asset and insert a holding
    operations.upsert_assets(test_conn, [{"id": "btc", "symbol": "BTC", "name": "Bitcoin"}])
    holding_id = operations.insert_holding(test_conn, "btc", amount=1.5, avg_buy_price=100.0)

    # Act
    holdings = operations.get_all_holdings(test_conn)

    # Assert
    assert isinstance(holding_id, int)
    assert len(holdings) == 1
    h = holdings[0]
    assert h["asset_id"] == "btc"
    assert h["amount"] == 1.5
    assert h["avg_buy_price"] == 100.0


def test_alerts_toggle_active(test_conn):
    # Arrange: create asset and an alert (defaults to active=1)
    operations.upsert_assets(test_conn, [{"id": "btc", "symbol": "BTC", "name": "Bitcoin"}])
    alert = {"asset_id": "btc", "type": "price", "op": "gt", "threshold": 50000.0}
    alert_id = operations.insert_alert(test_conn, alert)

    # Verify initially active
    alerts = operations.get_all_alerts(test_conn)
    a = next(a for a in alerts if a["id"] == alert_id)
    assert a["active"] == 1

    # Toggle off
    operations.toggle_alert(test_conn, alert_id, False)
    alerts = operations.get_all_alerts(test_conn)
    a = next(a for a in alerts if a["id"] == alert_id)
    assert a["active"] == 0

    # Toggle on
    operations.toggle_alert(test_conn, alert_id, True)
    alerts = operations.get_all_alerts(test_conn)
    a = next(a for a in alerts if a["id"] == alert_id)
    assert a["active"] == 1