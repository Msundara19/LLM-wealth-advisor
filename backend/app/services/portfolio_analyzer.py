"""
Portfolio Analyzer Service for analyzing investment portfolios
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.services.market_data import MarketDataService

logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """
    Service for analyzing investment portfolios
    Provides risk metrics, allocation analysis, and recommendations
    """
    
    def __init__(self):
        self.market_data = MarketDataService()
    
    def analyze(self, portfolio_data: str) -> str:
        """
        Analyze a portfolio (LangChain tool interface - takes string, returns string)
        
        Args:
            portfolio_data: JSON string of portfolio holdings
            
        Returns:
            Analysis results as formatted string
        """
        try:
            # Parse portfolio data
            if isinstance(portfolio_data, str):
                portfolio = json.loads(portfolio_data)
            else:
                portfolio = portfolio_data
            
            # Perform analysis
            analysis = self.analyze_portfolio(portfolio)
            
            # Format as string for LangChain
            return self._format_analysis(analysis)
            
        except json.JSONDecodeError:
            return f"Error: Invalid portfolio data format. Please provide valid JSON."
        except Exception as e:
            logger.error(f"Portfolio analysis error: {str(e)}")
            return f"Error analyzing portfolio: {str(e)}"
    
    def analyze_portfolio(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio analysis
        
        Args:
            portfolio: Dictionary containing portfolio holdings
            
        Returns:
            Analysis results
        """
        holdings = portfolio.get("holdings", [])
        
        if not holdings:
            return {"error": "No holdings found in portfolio"}
        
        # Calculate basic metrics
        total_value = 0
        total_invested = 0
        allocation = {}
        holdings_analysis = []
        
        for holding in holdings:
            symbol = holding.get("symbol", "")
            quantity = holding.get("quantity", 0)
            avg_price = holding.get("average_price", 0)
            asset_type = holding.get("asset_type", "stock")
            
            # Get current price
            price_data = self.market_data.get_stock_price(symbol)
            current_price = price_data.get("price", avg_price)
            
            # Calculate values
            invested = quantity * avg_price
            current = quantity * current_price
            gain = current - invested
            gain_pct = (gain / invested * 100) if invested > 0 else 0
            
            total_invested += invested
            total_value += current
            
            # Track allocation by asset type
            if asset_type not in allocation:
                allocation[asset_type] = 0
            allocation[asset_type] += current
            
            holdings_analysis.append({
                "symbol": symbol,
                "name": price_data.get("name", symbol),
                "quantity": quantity,
                "average_price": avg_price,
                "current_price": current_price,
                "invested_value": round(invested, 2),
                "current_value": round(current, 2),
                "gain_loss": round(gain, 2),
                "gain_loss_percent": round(gain_pct, 2),
                "weight": 0  # Will calculate after total
            })
        
        # Calculate weights
        for holding in holdings_analysis:
            holding["weight"] = round(
                (holding["current_value"] / total_value * 100) if total_value > 0 else 0, 
                2
            )
        
        # Calculate allocation percentages
        allocation_pct = {}
        for asset_type, value in allocation.items():
            allocation_pct[asset_type] = round(
                (value / total_value * 100) if total_value > 0 else 0, 
                2
            )
        
        # Calculate overall returns
        total_gain = total_value - total_invested
        total_gain_pct = (total_gain / total_invested * 100) if total_invested > 0 else 0
        
        # Risk metrics
        risk_metrics = self._calculate_risk_metrics(holdings_analysis)
        
        # Recommendations
        recommendations = self._generate_recommendations(
            holdings_analysis, 
            allocation_pct, 
            risk_metrics
        )
        
        return {
            "summary": {
                "total_invested": round(total_invested, 2),
                "current_value": round(total_value, 2),
                "total_gain_loss": round(total_gain, 2),
                "total_return_percent": round(total_gain_pct, 2),
                "number_of_holdings": len(holdings)
            },
            "allocation": allocation_pct,
            "holdings": holdings_analysis,
            "risk_metrics": risk_metrics,
            "recommendations": recommendations,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_risk_metrics(
        self, 
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        
        if not holdings:
            return {}
        
        # Concentration risk (top holding weight)
        weights = [h["weight"] for h in holdings]
        max_weight = max(weights) if weights else 0
        
        # Diversification score (inverse of concentration)
        # Higher is better, max 10
        if len(holdings) == 1:
            diversification = 1
        else:
            # Based on number of holdings and weight distribution
            diversification = min(10, len(holdings) * (1 - max_weight / 100))
        
        # Simple risk score based on concentration
        # Lower concentration = lower risk
        if max_weight > 50:
            risk_level = "High"
            risk_score = 8
        elif max_weight > 30:
            risk_level = "Medium"
            risk_score = 5
        else:
            risk_level = "Low"
            risk_score = 3
        
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 1),
            "diversification_score": round(diversification, 1),
            "concentration_risk": {
                "top_holding_weight": max_weight,
                "status": "High" if max_weight > 40 else "Acceptable"
            },
            "number_of_positions": len(holdings)
        }
    
    def _generate_recommendations(
        self,
        holdings: List[Dict[str, Any]],
        allocation: Dict[str, float],
        risk_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate portfolio recommendations"""
        
        recommendations = []
        
        # Check diversification
        if len(holdings) < 5:
            recommendations.append(
                "Consider adding more holdings to improve diversification. "
                "A well-diversified portfolio typically has 10-20 positions."
            )
        
        # Check concentration
        top_weight = risk_metrics.get("concentration_risk", {}).get("top_holding_weight", 0)
        if top_weight > 40:
            top_holding = max(holdings, key=lambda x: x["weight"])
            recommendations.append(
                f"High concentration in {top_holding['symbol']} ({top_weight:.1f}%). "
                "Consider rebalancing to reduce single-stock risk."
            )
        
        # Check sector allocation (simplified)
        stock_allocation = allocation.get("stock", 0) + allocation.get("STOCK", 0)
        if stock_allocation > 80:
            recommendations.append(
                "Portfolio is heavily weighted towards stocks. "
                "Consider adding bonds or fixed income for stability."
            )
        
        # Check for losers
        big_losers = [h for h in holdings if h["gain_loss_percent"] < -20]
        if big_losers:
            symbols = ", ".join([h["symbol"] for h in big_losers[:3]])
            recommendations.append(
                f"Review underperforming holdings ({symbols}). "
                "Consider if the investment thesis still holds."
            )
        
        # Check for winners (tax harvesting opportunity)
        big_winners = [h for h in holdings if h["gain_loss_percent"] > 50]
        if big_winners:
            recommendations.append(
                "Some holdings have significant gains. "
                "Consider partial profit booking for risk management."
            )
        
        # Default recommendation
        if not recommendations:
            recommendations.append(
                "Portfolio looks well-structured. "
                "Continue regular monitoring and rebalancing quarterly."
            )
        
        return recommendations
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results as readable string"""
        
        if "error" in analysis:
            return f"Analysis Error: {analysis['error']}"
        
        summary = analysis.get("summary", {})
        risk = analysis.get("risk_metrics", {})
        recommendations = analysis.get("recommendations", [])
        
        output = []
        output.append("=== Portfolio Analysis ===\n")
        
        # Summary
        output.append("📊 SUMMARY")
        output.append(f"  Total Invested: ₹{summary.get('total_invested', 0):,.2f}")
        output.append(f"  Current Value: ₹{summary.get('current_value', 0):,.2f}")
        output.append(f"  Total Return: ₹{summary.get('total_gain_loss', 0):,.2f} ({summary.get('total_return_percent', 0):.2f}%)")
        output.append(f"  Holdings: {summary.get('number_of_holdings', 0)}")
        output.append("")
        
        # Risk
        output.append("⚠️ RISK ASSESSMENT")
        output.append(f"  Risk Level: {risk.get('risk_level', 'Unknown')}")
        output.append(f"  Diversification Score: {risk.get('diversification_score', 0)}/10")
        output.append("")
        
        # Allocation
        output.append("📈 ALLOCATION")
        for asset_type, pct in analysis.get("allocation", {}).items():
            output.append(f"  {asset_type.title()}: {pct:.1f}%")
        output.append("")
        
        # Recommendations
        output.append("💡 RECOMMENDATIONS")
        for i, rec in enumerate(recommendations, 1):
            output.append(f"  {i}. {rec}")
        
        return "\n".join(output)
    
    def get_rebalancing_suggestions(
        self,
        portfolio: Dict[str, Any],
        target_allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Get rebalancing suggestions to match target allocation
        
        Args:
            portfolio: Current portfolio holdings
            target_allocation: Target allocation percentages by asset type
        """
        analysis = self.analyze_portfolio(portfolio)
        current_allocation = analysis.get("allocation", {})
        total_value = analysis.get("summary", {}).get("current_value", 0)
        
        suggestions = []
        
        for asset_type, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_type, 0)
            diff = target_pct - current_pct
            
            if abs(diff) > 2:  # Only suggest if difference is significant
                amount = total_value * (diff / 100)
                action = "Buy" if diff > 0 else "Sell"
                
                suggestions.append({
                    "asset_type": asset_type,
                    "current_percent": current_pct,
                    "target_percent": target_pct,
                    "difference": round(diff, 2),
                    "action": action,
                    "amount": round(abs(amount), 2)
                })
        
        return {
            "current_allocation": current_allocation,
            "target_allocation": target_allocation,
            "suggestions": suggestions,
            "total_portfolio_value": total_value
        }
