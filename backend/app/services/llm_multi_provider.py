"""
Multi-Provider LLM Service with support for free/affordable providers
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.memory import ConversationBufferMemory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.tools import Tool

from app.core.config import settings
from app.services.market_data import MarketDataService
from app.services.portfolio_analyzer import PortfolioAnalyzer

logger = logging.getLogger(__name__)


class MultiProviderLLMService:
    """
    Service for managing LLM interactions with multiple provider support
    Prioritizes free/affordable providers like Groq
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
            logger.info("Multi-Provider LLM Service initialized successfully")

    def _setup(self):
        """Setup LLM models and tools"""
        # Initialize LLM based on provider
        self.llm = self._initialize_llm()

        # Initialize embeddings (using free HuggingFace embeddings)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # Setup system prompt
        self.system__prompt = self._get_system_prompt()

        # Initialize tools
        self.tools = self._setup_tools()

        # Memory management
        self.memories = {}

    def _initialize_llm(self):
        """Initialize LLM based on configured provider"""
        provider = settings.LLM_PROVIDER.lower()

        if provider == "groq":
            return self._setup_groq()
        elif provider == "together":
            return self._setup_together()
        elif provider == "anyscale":
            return self._setup_anyscale()
        elif provider == "replicate":
            return self._setup_replicate()
        elif provider == "huggingface":
            return self._setup_huggingface()
        elif provider == "openai":
            return self._setup_openai()
        elif provider == "anthropic":
            return self._setup_anthropic()
        else:
            # Default to Groq if available
            if settings.GROQ_API_KEY:
                logger.info("Defaulting to Groq LLM provider")
                return self._setup_groq()
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

    def _setup_groq(self):
        """Setup Groq LLM (FREE with generous limits)"""
        try:
            from groq import Groq
            from langchain.llms.base import LLM
            from typing import Optional, List, Any

            class GroqLLM(LLM):
                """Custom Groq LLM wrapper for LangChain"""

                client: Any = None
                model: str = "mixtral-8x7b-32768"
                temperature: float = 0.7
                max_tokens: int = 2000

                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
                    self.client = Groq(api_key=settings.GROQ_API_KEY)

                @property
                def _llm_type(self) -> str:
                    return "groq"

                def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
                    response = self.client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=self.model,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        stop=stop,
                    )
                    return response.choices[0].message.content

            logger.info(f"Using Groq with model: {settings.LLM_MODEL}")
            return GroqLLM(
                model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, max_tokens=settings.LLM_MAX_TOKENS
            )
        except Exception as e:
            logger.error(f"Failed to setup Groq: {str(e)}")
            raise

    def _setup_together(self):
        """Setup Together AI (Free credits available)"""
        try:
            from langchain_community.llms import Together

            logger.info(f"Using Together AI with model: {settings.LLM_MODEL}")
            return Together(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                together_api_key=settings.TOGETHER_API_KEY,
            )
        except Exception as e:
            logger.error(f"Failed to setup Together: {str(e)}")
            raise

    def _setup_anyscale(self):
        """Setup Anyscale Endpoints (Free tier available)"""
        try:
            from langchain_community.llms import Anyscale

            logger.info(f"Using Anyscale with model: {settings.LLM_MODEL}")
            return Anyscale(
                model_name=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                anyscale_api_key=settings.ANYSCALE_API_KEY,
            )
        except Exception as e:
            logger.error(f"Failed to setup Anyscale: {str(e)}")
            raise

    def _setup_replicate(self):
        """Setup Replicate (Pay per use, very affordable)"""
        try:
            from langchain_community.llms import Replicate

            logger.info(f"Using Replicate with model: {settings.LLM_MODEL}")
            return Replicate(
                model=settings.LLM_MODEL,
                model_kwargs={"temperature": settings.LLM_TEMPERATURE, "max_new_tokens": settings.LLM_MAX_TOKENS},
            )
        except Exception as e:
            logger.error(f"Failed to setup Replicate: {str(e)}")
            raise

    def _setup_huggingface(self):
        """Setup HuggingFace Inference API (Free tier)"""
        try:
            from langchain_community.llms import HuggingFaceHub

            logger.info(f"Using HuggingFace with model: {settings.LLM_MODEL}")
            return HuggingFaceHub(
                repo_id=settings.LLM_MODEL,
                model_kwargs={"temperature": settings.LLM_TEMPERATURE, "max_new_tokens": settings.LLM_MAX_TOKENS},
                huggingfacehub_api_token=settings.HUGGINGFACE_API_KEY,
            )
        except Exception as e:
            logger.error(f"Failed to setup HuggingFace: {str(e)}")
            raise

    def _setup_openai(self):
        """Setup OpenAI (Paid only)"""
        from langchain.chat_models import ChatOpenAI

        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")

        logger.info(f"Using OpenAI with model: {settings.LLM_MODEL}")
        return ChatOpenAI(
            model_name=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY,
        )

    def _setup_anthropic(self):
        """Setup Anthropic Claude (Paid only)"""
        from langchain.chat_models import ChatAnthropic

        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API key not configured")

        logger.info("Using Anthropic Claude")
        return ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
        )

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
        """
        try:
            self.get_or_create_memory(user_id)

            # For completion models (Groq, Together, etc), use simple prompt
            if settings.LLM_PROVIDER in ["openai", "anthropic"]:
                system_msg = self.systemprompt.format(current_date=datetime.now().strftime("%Y-%m-%d"))
                prompt_str = f"{system_msg}\n\nUser: {message}\nAssistant:"
                response = await self.llm.apredict(prompt_str)

            # Log the interaction
            logger.info(
                f"Processed message for user {user_id} using {settings.LLM_PROVIDER}"
            )

            return {
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "provider": settings.LLM_PROVIDER,
                "model": settings.LLM_MODEL,
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)

            # Try fallback to a different provider if available
            fallback_response = await self._try_fallback_provider(user_id, message)
            if fallback_response:
                return fallback_response

            return {
                "response": (
                    "I apologize, but I encountered an error processing your request. "
                    "Please try again or contact support."
                ),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _try_fallback_provider(self, user_id: str, message: str) -> Optional[Dict[str, Any]]:
        """Try fallback to another provider if primary fails"""
        fallback_providers = ["groq", "huggingface", "together"]

        for provider in fallback_providers:
            if provider == settings.LLM_PROVIDER:
                continue

            try:
                logger.info(f"Attempting fallback to {provider}")
                # Temporarily switch provider
                original_provider = settings.LLM_PROVIDER
                settings.LLM_PROVIDER = provider

                # Re-initialize LLM
                self.llm = self._initialize_llm()

                # Try again
                response = await self.process_message(user_id, message)

                # Restore original provider
                settings.LLM_PROVIDER = original_provider

                return response
            except Exception as e:
                logger.error(f"Fallback to {provider} failed: {str(e)}")
                continue

        return None

    @classmethod
    def health_check(cls) -> bool:
        """Check if the LLM service is healthy"""
        try:
            return cls._initialized and cls._instance is not None
        except Exception:
            return False


# Create singleton instance
llm_service = MultiProviderLLMService()
