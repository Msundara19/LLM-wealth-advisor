"""
Market Data Service for fetching real-time stock and market information
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from app.core.config import settings
from app.core.redis import cache

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service for fetching market data from various free APIs
    Supports: Yahoo Finance (yfinance), Alpha Vantage, and fallbacks
    """
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes cache for price data
        self._yf_available = self._check_yfinance()
    
    def _check_yfinance(self) -> bool:
        """Check if yfinance is available"""
        try:
            import yfinance
            return True
        except ImportError:
            logger.warning("yfinance not installed - using mock data")
            return False
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price and basic info
        
        Args:
            symbol: Stock symbol (e.g., RELIANCE.NS for NSE, AAPL for US)
            
        Returns:
            Dictionary with price and stock info
        """
        # Normalize symbol
        symbol = symbol.upper().strip()
        
        # Try cache first
        cache_key = f"stock:{symbol}"
        
        try:
            if self._yf_available:
                return self._get_price_yfinance(symbol)
            else:
                return self._get_mock_price(symbol)
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return self._get_error_response(symbol, str(e))
    
    def _get_price_yfinance(self, symbol: str) -> Dict[str, Any]:
        """Fetch price using yfinance"""
        import yfinance as yf
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            
            # Get historical data for change calculation
            hist = ticker.history(period="2d")
            
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close else 0
            else:
                prev_close = info.get('previousClose', current_price)
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close else 0
            
            return {
                "symbol": symbol,
                "name": info.get('longName', info.get('shortName', symbol)),
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_pct, 2),
                "currency": info.get('currency', 'INR'),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "volume": info.get('volume'),
                "avg_volume": info.get('averageVolume'),
                "dividend_yield": info.get('dividendYield'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "yfinance"
            }
            
        except Exception as e:
            logger.error(f"yfinance error for {symbol}: {str(e)}")
            raise
    
    def _get_mock_price(self, symbol: str) -> Dict[str, Any]:
        """Return mock price data for testing"""
        import random
        
        # Mock data for common Indian stocks
        mock_stocks = {
            "RELIANCE.NS": {"name": "Reliance Industries", "base_price": 2450},
            "TCS.NS": {"name": "Tata Consultancy Services", "base_price": 3800},
            "HDFCBANK.NS": {"name": "HDFC Bank", "base_price": 1650},
            "INFY.NS": {"name": "Infosys", "base_price": 1450},
            "ICICIBANK.NS": {"name": "ICICI Bank", "base_price": 1050},
            "SBIN.NS": {"name": "State Bank of India", "base_price": 620},
            "BHARTIARTL.NS": {"name": "Bharti Airtel", "base_price": 1180},
            "ITC.NS": {"name": "ITC Limited", "base_price": 450},
            "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "base_price": 1750},
            "LT.NS": {"name": "Larsen & Toubro", "base_price": 3200},
        }
        
        # Get base data or generate random
        if symbol in mock_stocks:
            base = mock_stocks[symbol]
            name = base["name"]
            base_price = base["base_price"]
        else:
            name = symbol.replace(".NS", "").replace(".BO", "")
            base_price = random.uniform(100, 5000)
        
        # Add some randomness
        variation = random.uniform(-0.03, 0.03)
        price = base_price * (1 + variation)
        change = price - base_price
        change_pct = variation * 100
        
        return {
            "symbol": symbol,
            "name": name,
            "price": round(price, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "currency": "INR",
            "market_cap": int(base_price * 1000000000),
            "pe_ratio": round(random.uniform(15, 35), 2),
            "52_week_high": round(base_price * 1.2, 2),
            "52_week_low": round(base_price * 0.8, 2),
            "volume": random.randint(1000000, 50000000),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "mock_data",
            "note": "Using simulated data - install yfinance for real prices"
        }
    
    def _get_error_response(self, symbol: str, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "symbol": symbol,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_market_news(self, query: str = "indian stock market") -> List[Dict[str, Any]]:
        """
        Get market news (mock implementation)
        For production, integrate with news APIs
        """
        # Mock news data
        mock_news = [
            {
                "title": "Sensex, Nifty end higher amid global cues",
                "summary": "Indian benchmark indices closed higher on positive global market sentiment.",
                "source": "Economic Times",
                "timestamp": datetime.utcnow().isoformat(),
                "url": "https://economictimes.com"
            },
            {
                "title": "RBI keeps repo rate unchanged at 6.5%",
                "summary": "The Reserve Bank of India maintained the repo rate, focusing on inflation management.",
                "source": "Business Standard",
                "timestamp": datetime.utcnow().isoformat(),
                "url": "https://business-standard.com"
            },
            {
                "title": "IT stocks rally on strong Q3 expectations",
                "summary": "Technology sector stocks gained as analysts predict strong quarterly results.",
                "source": "Mint",
                "timestamp": datetime.utcnow().isoformat(),
                "url": "https://livemint.com"
            },
        ]
        
        return mock_news
    
    def get_index_data(self, index: str = "^NSEI") -> Dict[str, Any]:
        """
        Get index data (NIFTY 50, SENSEX, etc.)
        """
        return self.get_stock_price(index)
    
    def get_multiple_prices(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Get prices for multiple symbols
        """
        results = []
        for symbol in symbols:
            results.append(self.get_stock_price(symbol))
        return results
    
    def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1mo"
    ) -> Dict[str, Any]:
        """
        Get historical price data
        
        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        """
        if not self._yf_available:
            return {
                "symbol": symbol,
                "error": "Historical data requires yfinance",
                "note": "Install yfinance: pip install yfinance"
            }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            # Convert to list of dicts
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"])
                })
            
            return {
                "symbol": symbol,
                "period": period,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return {
                "symbol": symbol,
                "error": str(e)
            }
