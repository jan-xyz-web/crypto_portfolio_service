
from sqlalchemy import MetaData, Table, Column, String, Integer, Float, ForeignKey, Index, event
from sqlalchemy.engine import Engine

metadata = MetaData()

assets_table = Table(
    "assets",
    metadata,
    Column("id", String, primary_key=True),
    Column("symbol", String, nullable=False),
    Column("name", String, nullable=False),
)

prices_table = Table(
    "prices",
    metadata,
    Column("asset_id", String, ForeignKey("assets.id")),
    Column("ts", Integer, nullable=False),
    Column("price", Float, nullable=False),
    Column("mcap", Float),
    Column("vol", Float)
)

holdings_table = Table(
    "holdings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("asset_id", String, ForeignKey("assets.id")),
    Column("amount", Float, nullable=False),
    Column("avg_buy_price", Float, nullable=False),
    Column("created_at", Integer, nullable=False)
)

alerts_table = Table(
    "alerts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("asset_id", String, ForeignKey("assets.id")),
    Column("type", String, nullable=False),
    Column("op", String, nullable=False),
    Column("threshold", Float, nullable=False),
    Column("active", Integer, nullable=False, server_default="1"),
    Column("created_at", Integer, nullable=False),
    Column("last_fired_ts", Integer)
)


Index("idx_prices_lookup", prices_table.c.asset_id, prices_table.c.ts, unique=True)
Index("idx_holdings_asset", holdings_table.c.asset_id)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def create_tables(engine: Engine) -> None:
    """Create all tables and indexes if not exist."""
    metadata.create_all(engine)