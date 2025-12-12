"""
Market Data API endpoints
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.market_data import MarketDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])

# Initialize service
market_service = MarketDataService()


# Response Models
class StockPriceResponse(BaseModel):
    """Stock price response"""
    symbol: str
    name: Optional[str] = None
    price: float
    change: Optional[float] = None
    change_percent: Optional[float] = None
    currency: Optional[str] = None
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None
    volume: Optional[int] = None
    timestamp: str
    source: Optional[str] = None


class MarketNewsItem(BaseModel):
    """Market news item"""
    title: str
    summary: str
    source: str
    timestamp: str
    url: Optional[str] = None


# Endpoints
@router.get("/quote/{symbol}", response_model=StockPriceResponse)
async def get_stock_quote(symbol: str):
    """
    Get current stock quote
    
    Args:
        symbol: Stock symbol (e.g., RELIANCE.NS, TCS.NS, AAPL)
    """
    data = market_service.get_stock_price(symbol)
    
    return StockPriceResponse(
        symbol=data.get("symbol", symbol),
        name=data.get("name"),
        price=data.get("price", 0),
        change=data.get("change"),
        change_percent=data.get("change_percent"),
        currency=data.get("currency"),
        market_cap=data.get("market_cap"),
        pe_ratio=data.get("pe_ratio"),
        volume=data.get("volume"),
        timestamp=data.get("timestamp", ""),
        source=data.get("source")
    )


@router.get("/quotes")
async def get_multiple_quotes(
    symbols: str = Query(..., description="Comma-separated list of symbols")
):
    """
    Get quotes for multiple stocks
    
    Args:
        symbols: Comma-separated list of stock symbols
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    results = market_service.get_multiple_prices(symbol_list)
    
    return {
        "quotes": results,
        "count": len(results)
    }


@router.get("/index/{index_symbol}")
async def get_index_data(index_symbol: str):
    """
    Get market index data
    
    Common indices:
    - ^NSEI: NIFTY 50
    - ^BSESN: SENSEX
    - ^NSEBANK: Bank Nifty
    """
    data = market_service.get_index_data(index_symbol)
    return data


@router.get("/news", response_model=List[MarketNewsItem])
async def get_market_news(
    query: str = Query("indian stock market", description="Search query for news")
):
    """
    Get latest market news
    """
    news = market_service.get_market_news(query)
    
    return [
        MarketNewsItem(
            title=item["title"],
            summary=item["summary"],
            source=item["source"],
            timestamp=item["timestamp"],
            url=item.get("url")
        )
        for item in news
    ]


@router.get("/history/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query("1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max")
):
    """
    Get historical price data for a stock
    """
    data = market_service.get_historical_data(symbol, period)
    return data


@router.get("/popular")
async def get_popular_stocks():
    """
    Get data for popular Indian stocks
    """
    popular_symbols = [
        "RELIANCE.NS",
        "TCS.NS",
        "HDFCBANK.NS",
        "INFY.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "BHARTIARTL.NS",
        "ITC.NS",
        "KOTAKBANK.NS",
        "LT.NS"
    ]
    
    results = market_service.get_multiple_prices(popular_symbols)
    
    return {
        "stocks": results,
        "count": len(results)
    }


@router.get("/indices")
async def get_major_indices():
    """
    Get data for major Indian indices
    """
    indices = {
        "nifty50": "^NSEI",
        "sensex": "^BSESN",
        "banknifty": "^NSEBANK"
    }
    
    results = {}
    for name, symbol in indices.items():
        results[name] = market_service.get_index_data(symbol)
    
    return results


@router.get("/search")
async def search_stocks(
    q: str = Query(..., min_length=1, description="Search query")
):
    """
    Search for stocks by name or symbol
    """
    all_stocks = [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited"},
        {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited"},
        {"symbol": "INFY.NS", "name": "Infosys Limited"},
        {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited"},
        {"symbol": "SBIN.NS", "name": "State Bank of India"},
        {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Limited"},
        {"symbol": "ITC.NS", "name": "ITC Limited"},
        {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank"},
        {"symbol": "LT.NS", "name": "Larsen & Toubro Limited"},
        {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever"},
        {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited"},
        {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India"},
        {"symbol": "WIPRO.NS", "name": "Wipro Limited"},
        {"symbol": "HCLTECH.NS", "name": "HCL Technologies"},
        {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Limited"},
        {"symbol": "TATASTEEL.NS", "name": "Tata Steel Limited"},
        {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical"},
        {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Limited"},
        {"symbol": "ADANIENT.NS", "name": "Adani Enterprises"},
        {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation"},
        {"symbol": "NTPC.NS", "name": "NTPC Limited"},
        {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corporation"},
    ]
    
    q_lower = q.lower()
    
    matches = [
        stock for stock in all_stocks
        if q_lower in stock["symbol"].lower() or q_lower in stock["name"].lower()
    ]
    
    return {
        "query": q,
        "results": matches[:10],
        "count": len(matches)
    }
