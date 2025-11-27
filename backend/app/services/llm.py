"""
LLM Service for handling AI interactions using LangChain
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.embeddings import OpenAIEmbeddings
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

from app.core.config import settings
from app.services.market_data import MarketDataService
from app.services.portfolio_analyzer import PortfolioAnalyzer

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for managing LLM interactions for financial advisory
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
        """Setup LLM models and tools"""
        # Initialize primary LLM
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model_name=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                openai_api_key=settings.OPENAI_API_KEY,
            )
        elif settings.ANTHROPIC_API_KEY:
            self.llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
            )
        else:
            raise ValueError("No LLM API key configured")

        # Initialize embeddings for knowledge base
        if settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

        # Setup system prompt for financial advisor
        self.system_prompt = self._get_system_prompt()

        # Initialize tools
        self.tools = self._setup_tools()

        # Memory management
        self.memories = {}  # User-specific conversation memories

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

        Current date: {current_date}
        """

    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the agent"""
        tools = []

        # Market data tool
        market_service = MarketDataService()
        tools.append(
            Tool(
                name="GetMarketData",
                func=market_service.get_stock_price,
                description="Get current market price and data for a stock symbol",
            )
        )

        # Portfolio analysis tool
        portfolio_analyzer = PortfolioAnalyzer()
        tools.append(
            Tool(
                name="AnalyzePortfolio",
                func=portfolio_analyzer.analyze,
                description="Analyze a portfolio's performance, risk metrics, and allocation",
            )
        )

        # Market news tool
        tools.append(
            Tool(
                name="GetMarketNews",
                func=market_service.get_market_news,
                description="Get latest financial market news and updates",
            )
        )

        return tools

    def get_or_create_memory(self, user_id: str) -> ConversationBufferMemory:
        """Get or create conversation memory for a user"""
        if user_id not in self.memories:
            self.memories[user_id] = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
        return self.memories[user_id]

    async def process_message(
        self, user_id: str, message: str, context: Optional[Dict[str, Any]] = None
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
            # Get user's conversation memory
            memory = self.get_or_create_memory(user_id)

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=self.system_prompt.format(current_date=datetime.now().strftime("%Y-%m-%d"))),
                    MessagesPlaceholder(variable_name="chat_history"),
                    HumanMessage(content=message),
                ]
            )

            # Create agent with tools if needed
            if self._needs_tools(message):
                agent = initialize_agent(
                    tools=self.tools,
                    llm=self.llm,
                    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                    memory=memory,
                    verbose=settings.DEBUG,
                )
                response = await agent.arun(message)
            else:
                # Simple conversation without tools
                chain = LLMChain(llm=self.llm, prompt=prompt, memory=memory)
                response = await chain.arun(message=message)

            # Log the interaction
            logger.info(f"Processed message for user {user_id}")

            return {
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "tools_used": self._needs_tools(message),
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

    def _needs_tools(self, message: str) -> bool:
        """Determine if the message requires tool usage"""
        tool_keywords = [
            "price",
            "stock",
            "market",
            "portfolio",
            "analyze",
            "news",
            "performance",
            "risk",
            "allocation",
            "return",
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in tool_keywords)

    async def generate_portfolio_report(self, user_id: str, portfolio_data: Dict[str, Any]) -> str:
        """Generate a comprehensive portfolio analysis report"""
        prompt = f"""
        Generate a comprehensive portfolio analysis report for the following portfolio:

        Portfolio Data:
        {json.dumps(portfolio_data, indent=2)}

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

        response = await self.llm.apredict(prompt)
        return response

    async def get_investment_recommendation(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
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

        Consider Indian market conditions and tax benefits.
        """

        response = await self.llm.apredict(prompt)

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
            return cls._initialized and cls._instance is not None
        except Exception:
            return False


# Create singleton instance
llm_service = LLMService()
