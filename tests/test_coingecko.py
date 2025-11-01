import pytest
from unittest.mock import Mock, patch
import httpx
from app.services.coingecko import fetch_markets, normalize_market_data

# TODO: Define test_normalize_market_data()
# TODO: Define test_normalize_skip_invalid_records()

@pytest.fixture
def mock_coingecko_response():
    return [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 10000.0, "market_cap": 200000.0, "total_volume": 10000.0},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 5000.0, "market_cap": 50000.0, "total_volume": 2000.0}
        ]

def test_normalize_market_data(mock_coingecko_response):
    result_tuple = normalize_market_data(mock_coingecko_response, 1000)
    assets = result_tuple[0]
    prices = result_tuple[1]
    assert len(assets) == 2
    assert len(prices) == 2
    assert assets[0]["id"] == "bitcoin"
    assert assets[0]["symbol"] == "btc"
    assert prices[0]["asset_id"] == "bitcoin"
    assert prices[0]["price"] == 10000.0

def test_normalize_skip_invalid_records():
    raw = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 10000.0, "market_cap": 200000.0, "total_volume": 10000.0},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": None, "market_cap": 50000.0, "total_volume": 2000.0}
    ]
    ts = 1234567890
    assets_data, prices_data = normalize_market_data(raw, ts)
    
    assert len(assets_data) == 2
    assert len(prices_data) == 1
    assert prices_data[0]["asset_id"] == "bitcoin"
    assert prices_data[0]["price"] == 10000.0