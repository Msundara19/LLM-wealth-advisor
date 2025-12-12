"""
LLM Service for handling AI interactions
Supports multiple providers: Groq (free), OpenAI, Anthropic
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.core.config import settings
from app.services.market_data import MarketDataService
from app.services.portfolio_analyzer import PortfolioAnalyzer

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for managing LLM interactions for financial advisory
    Supports Groq (free), OpenAI, and Anthropic
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls):
        """Initialize the LLM service"""
        if not cls._initialized:
            instance = cls()
            instance._setup()
            cls._initialized = True
            logger.info("LLM Service initialized successfully")

    def _setup(self):
        """Setup LLM client and tools"""
        self.client = None
        self.provider = settings.LLM_PROVIDER.lower()
        
        # Initialize client based on provider
        if self.provider == "groq" and settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                self.model = "llama-3.3-70b-versatile"
                logger.info("Initialized Groq LLM client")
            except ImportError:
                logger.warning("Groq package not installed")
        elif self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.model = settings.LLM_MODEL or "gpt-4-turbo-preview"
                logger.info("Initialized OpenAI LLM client")
            except ImportError:
                logger.warning("OpenAI package not installed")
        elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.model = "claude-3-sonnet-20240229"
                logger.info("Initialized Anthropic LLM client")
            except ImportError:
                logger.warning("Anthropic package not installed")
        
        if not self.client:
            logger.warning("No LLM provider configured - service will return mock responses")
        
        # Setup system prompt
        self.system_prompt = self._get_system_prompt()
        
        # Initialize services for tools
        self.market_service = MarketDataService()
        self.portfolio_analyzer = PortfolioAnalyzer()
        
        # Simple conversation memory (in-memory, per user)
        self.memories: Dict[str, List[Dict[str, str]]] = {}

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the financial advisor"""
        return """You are an expert financial advisor AI assistant for Wallet Wealth LLP,
a premier wealth management firm in India. Your role is to provide personalized,
professional financial advice while maintaining the highest standards of accuracy
and compliance.

Key Responsibilities:
1. Provide investment guidance tailored to Indian markets
2. Analyze portfolios and suggest optimizations
3. Explain complex financial concepts clearly
4. Consider tax implications under Indian tax laws
5. Recommend suitable mutual funds, stocks, and other investment vehicles
6. Assess risk tolerance and investment goals

Guidelines:
- Always maintain a professional, helpful tone
- Provide data-driven insights when possible
- Clearly state any assumptions or limitations
- Never guarantee returns or make unrealistic promises
- Emphasize the importance of diversification
- Consider the client's risk profile and investment horizon
- Mention regulatory compliance (SEBI guidelines) when relevant

Important: You must always remind users that while you provide guidance,
final investment decisions should be made after consulting with a certified
financial advisor at Wallet Wealth.

Current date: """ + datetime.now().strftime("%Y-%m-%d")

    def get_or_create_memory(self, user_id: str) -> List[Dict[str, str]]:
        """Get or create conversation memory for a user"""
        if user_id not in self.memories:
            self.memories[user_id] = []
        return self.memories[user_id]

    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response

        Args:
            user_id: Unique identifier for the user
            message: The user's message
            context: Additional context (user profile, portfolio data, etc.)

        Returns:
            Response dictionary with AI message and metadata
        """
        try:
            # Get conversation history
            history = self.get_or_create_memory(user_id)
            
            # Check if message needs tool usage (market data, portfolio analysis)
            tool_response = await self._check_and_use_tools(message)
            
            # Build messages list
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history (last 10 exchanges)
            for entry in history[-20:]:
                messages.append(entry)
            
            # Add tool context if available
            if tool_response:
                enhanced_message = f"{message}\n\n[Tool Data]:\n{tool_response}"
            else:
                enhanced_message = message
            
            messages.append({"role": "user", "content": enhanced_message})
            
            # Generate response
            response_text = await self._generate_response(messages)
            
            # Update memory
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response_text})
            
            # Keep memory bounded
            if len(history) > 40:
                self.memories[user_id] = history[-40:]
            
            logger.info(f"Processed message for user {user_id}")
            
            return {
                "response": response_text,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "tools_used": bool(tool_response),
                "model": getattr(self, 'model', 'unknown'),
                "provider": self.provider
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return {
                "response": (
                    "I apologize, but I encountered an error processing your request. "
                    "Please try again or contact support."
                ),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using configured LLM provider"""
        
        if not self.client:
            return self._get_mock_response(messages[-1]["content"])
        
        try:
            if self.provider == "groq":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                )
                return completion.choices[0].message.content
            
            elif self.provider == "openai":
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                )
                return completion.choices[0].message.content
            
            elif self.provider == "anthropic":
                # Anthropic has different message format
                system_msg = messages[0]["content"] if messages[0]["role"] == "system" else ""
                chat_messages = [m for m in messages if m["role"] != "system"]
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=settings.LLM_MAX_TOKENS,
                    system=system_msg,
                    messages=chat_messages
                )
                return response.content[0].text
            
            else:
                return self._get_mock_response(messages[-1]["content"])
                
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            raise

    async def _check_and_use_tools(self, message: str) -> Optional[str]:
        """Check if message needs tool usage and return tool data"""
        message_lower = message.lower()
        results = []
        
        # Check for stock price queries
        stock_keywords = ["price", "stock", "share", "quote", "trading"]
        if any(kw in message_lower for kw in stock_keywords):
            # Try to extract stock symbol
            symbols = self._extract_stock_symbols(message)
            for symbol in symbols[:3]:  # Limit to 3 stocks
                data = self.market_service.get_stock_price(symbol)
                results.append(f"Stock {symbol}: ₹{data.get('price', 'N/A')} ({data.get('change_percent', 0):.2f}%)")
        
        # Check for portfolio analysis
        if "portfolio" in message_lower and any(kw in message_lower for kw in ["analyze", "analysis", "review"]):
            results.append("Portfolio analysis tool available - please share your holdings for detailed analysis.")
        
        # Check for market/index queries
        if any(kw in message_lower for kw in ["nifty", "sensex", "market", "index"]):
            nifty = self.market_service.get_stock_price("^NSEI")
            sensex = self.market_service.get_stock_price("^BSESN")
            results.append(f"NIFTY 50: {nifty.get('price', 'N/A')}")
            results.append(f"SENSEX: {sensex.get('price', 'N/A')}")
        
        return "\n".join(results) if results else None

    def _extract_stock_symbols(self, message: str) -> List[str]:
        """Extract stock symbols from message"""
        # Common Indian stock mapping
        stock_mapping = {
            "reliance": "RELIANCE.NS",
            "tcs": "TCS.NS",
            "infosys": "INFY.NS",
            "hdfc": "HDFCBANK.NS",
            "icici": "ICICIBANK.NS",
            "sbi": "SBIN.NS",
            "airtel": "BHARTIARTL.NS",
            "itc": "ITC.NS",
            "kotak": "KOTAKBANK.NS",
            "wipro": "WIPRO.NS",
            "hcl": "HCLTECH.NS",
            "maruti": "MARUTI.NS",
            "tata motors": "TATAMOTORS.NS",
            "tata steel": "TATASTEEL.NS",
            "bajaj": "BAJFINANCE.NS",
        }
        
        symbols = []
        message_lower = message.lower()
        
        for name, symbol in stock_mapping.items():
            if name in message_lower:
                symbols.append(symbol)
        
        # Also check for .NS or .BO suffixed symbols
        import re
        pattern = r'\b([A-Z]{2,}(?:\.NS|\.BO)?)\b'
        matches = re.findall(pattern, message.upper())
        for match in matches:
            if not match.endswith(('.NS', '.BO')):
                match = f"{match}.NS"
            if match not in symbols:
                symbols.append(match)
        
        return symbols

    def _get_mock_response(self, message: str) -> str:
        """Return a mock response when no LLM is configured"""
        return (
            "Thank you for your question. I'm currently running in demo mode without "
            "an LLM backend configured. To enable full AI capabilities, please configure "
            "a GROQ_API_KEY (free), OPENAI_API_KEY, or ANTHROPIC_API_KEY in your environment.\n\n"
            "In the meantime, I can still help you with:\n"
            "- Market data (stock prices, indices)\n"
            "- Portfolio tracking\n"
            "- Basic financial information\n\n"
            "For personalized AI-powered advice, please contact Wallet Wealth support."
        )

    async def generate_portfolio_report(
        self, 
        user_id: str, 
        portfolio_data: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive portfolio analysis report"""
        analysis = self.portfolio_analyzer.analyze_portfolio(portfolio_data)
        
        if not self.client:
            return self.portfolio_analyzer._format_analysis(analysis)
        
        prompt = f"""
Generate a comprehensive portfolio analysis report based on this data:

{json.dumps(analysis, indent=2)}

Include:
1. Executive Summary
2. Asset Allocation Analysis
3. Performance Metrics
4. Risk Assessment
5. Recommendations for Optimization
6. Tax Considerations (Indian context)
7. Rebalancing Suggestions

Format the report professionally with clear sections and actionable insights.
"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        return await self._generate_response(messages)

    async def get_investment_recommendation(
        self, 
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get personalized investment recommendations"""
        prompt = f"""
Based on the following user profile, provide personalized investment recommendations:

User Profile:
- Age: {user_profile.get('age')}
- Risk Tolerance: {user_profile.get('risk_tolerance')}
- Investment Horizon: {user_profile.get('investment_horizon')}
- Monthly Income: ₹{user_profile.get('monthly_income')}
- Financial Goals: {user_profile.get('goals')}
- Current Investments: {user_profile.get('current_investments')}

Provide:
1. Recommended asset allocation
2. Specific investment options (mutual funds, stocks, bonds)
3. Monthly investment amount (SIP)
4. Expected returns range
5. Risk mitigation strategies

Consider Indian market conditions and tax benefits (80C, 80D, etc.).
"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self._generate_response(messages)
        
        return {
            "recommendations": response,
            "generated_at": datetime.utcnow().isoformat(),
            "profile_summary": user_profile,
        }

    def clear_user_memory(self, user_id: str):
        """Clear conversation memory for a user"""
        if user_id in self.memories:
            del self.memories[user_id]
            logger.info(f"Cleared memory for user {user_id}")

    @classmethod
    def health_check(cls) -> bool:
        """Check if the LLM service is healthy"""
        try:
            instance = cls()
            return cls._initialized or instance.client is not None
        except Exception:
            return False


# Create singleton instance
llm_service = LLMService()
