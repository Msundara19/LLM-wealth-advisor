# Free API Services Guide for Wallet Wealth LLM Advisor

## 🆓 Free LLM Providers

### 1. **Groq** (RECOMMENDED - Fastest & Most Generous)
- **Website**: https://console.groq.com/
- **Free Tier**: Very generous, thousands of requests
- **Speed**: Ultra-fast inference (10x faster than others)
- **Models Available**:
  - `mixtral-8x7b-32768` - Best for complex financial analysis
  - `llama2-70b-4096` - Great for general conversation
  - `gemma-7b-it` - Good for quick responses
- **How to Get API Key**:
  1. Sign up at https://console.groq.com/
  2. Go to API Keys section
  3. Create new API key
  4. Add to `.env`: `GROQ_API_KEY=your-key-here`

### 2. **Together AI**
- **Website**: https://api.together.xyz/
- **Free Credits**: $25 on signup
- **Models**: Llama 2, Mixtral, CodeLlama
- **Best For**: High-quality responses
- **Get API Key**: Sign up and get key from dashboard

### 3. **Anyscale Endpoints**
- **Website**: https://www.anyscale.com/endpoints
- **Free Tier**: Available with rate limits
- **Models**: Llama 2, Mistral
- **Best For**: Production workloads

### 4. **HuggingFace**
- **Website**: https://huggingface.co/
- **Free Tier**: Inference API with rate limits
- **Models**: Thousands of open-source models
- **Get API Key**: 
  1. Create account at huggingface.co
  2. Go to Settings → Access Tokens
  3. Create new token

### 5. **Replicate**
- **Website**: https://replicate.com/
- **Pricing**: Pay-per-use (very cheap, ~$0.0002 per request)
- **Models**: All open-source models
- **Best For**: Testing different models

## 📈 Free Market Data APIs

### 1. **Yahoo Finance** (No API Key Needed!)
- **Library**: `yfinance`
- **Data**: Real-time stock prices, historical data
- **Usage**: Already integrated, just works!
```python
import yfinance as yf
stock = yf.Ticker("RELIANCE.NS")
info = stock.info
```

### 2. **Alpha Vantage**
- **Website**: https://www.alphavantage.co/
- **Free Tier**: 500 requests/day
- **Get Key**: Sign up for free API key
- **Data**: Stocks, forex, crypto, technical indicators

### 3. **Twelve Data**
- **Website**: https://twelvedata.com/
- **Free Tier**: 800 requests/day
- **Get Key**: Sign up at twelvedata.com
- **Data**: Real-time and historical market data

### 4. **Financial Modeling Prep (FMP)**
- **Website**: https://site.financialmodelingprep.com/
- **Free Tier**: 250 requests/day
- **Data**: Financial statements, market data, news

### 5. **Finnhub**
- **Website**: https://finnhub.io/
- **Free Tier**: 60 requests/minute
- **Data**: Real-time data, news, financials

## 🚀 Quick Setup Guide

### Step 1: Get Groq API Key (5 minutes)
```bash
# 1. Go to https://console.groq.com/
# 2. Sign up with Google/GitHub
# 3. Generate API key
# 4. Copy key
```

### Step 2: Get Free Market Data Keys
```bash
# Alpha Vantage (2 minutes)
# 1. Visit https://www.alphavantage.co/support/#api-key
# 2. Enter email
# 3. Get key instantly

# Twelve Data (3 minutes)
# 1. Sign up at https://twelvedata.com/signup
# 2. Verify email
# 3. Get API key from dashboard
```

### Step 3: Update .env File
```env
# Primary LLM (FREE)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
LLM_PROVIDER=groq
LLM_MODEL=mixtral-8x7b-32768

# Backup LLM (FREE)
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx

# Market Data (FREE)
ALPHA_VANTAGE_API_KEY=xxxxxxxxxxxxx
TWELVE_DATA_API_KEY=xxxxxxxxxxxxx
YAHOO_FINANCE_ENABLED=true

# Optional - if you have credits
TOGETHER_API_KEY=xxxxxxxxxxxxx  # $25 free credits
```

## 💰 Cost Comparison

| Provider | Free Tier | Speed | Quality | Best For |
|----------|-----------|-------|---------|----------|
| **Groq** | Thousands/day | ⚡⚡⚡ | ⭐⭐⭐⭐ | Production use |
| **HuggingFace** | 1000/day | ⚡⚡ | ⭐⭐⭐ | Development |
| **Together** | $25 credits | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | High quality |
| **Anyscale** | Limited | ⚡⚡ | ⭐⭐⭐⭐ | Scaling |
| **Replicate** | Pay-per-use | ⚡⚡ | ⭐⭐⭐⭐ | Experiments |

## 🎯 Recommended Configuration for Start

```env
# This gives you a fully functional system for FREE
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-key
LLM_MODEL=mixtral-8x7b-32768

# Backup provider
HUGGINGFACE_API_KEY=your-hf-key

# Market data
ALPHA_VANTAGE_API_KEY=your-av-key
YAHOO_FINANCE_ENABLED=true
```

## 📊 Usage Optimization Tips

1. **Cache Responses**: Store common queries to reduce API calls
2. **Use Streaming**: Implement streaming responses for better UX
3. **Fallback Strategy**: Configure multiple providers for reliability
4. **Rate Limiting**: Implement client-side rate limiting
5. **Model Selection**:
   - Use smaller models for simple queries
   - Use larger models only for complex analysis

## 🔄 Fallback Chain Configuration

The system automatically falls back to available providers:
1. Primary: Groq (if configured)
2. Fallback 1: HuggingFace
3. Fallback 2: Together (if credits available)
4. Emergency: Display cached/template response

## 📈 Monitoring Free Tier Usage

### Groq Dashboard
- Check usage: https://console.groq.com/usage
- Monitor: Requests, tokens, latency

### Together AI
- Dashboard: https://api.together.xyz/usage
- Track: Credits remaining, model usage

### Alpha Vantage
- No dashboard, but returns rate limit headers
- Monitor in application logs

## 🛠️ Troubleshooting

### Common Issues

1. **Rate Limit Exceeded**
   - Solution: Implement caching
   - Use fallback providers

2. **Model Not Available**
   - Groq models: Use `mixtral-8x7b-32768`
   - HuggingFace: Use popular models

3. **Slow Response**
   - Switch to Groq for speed
   - Use smaller models

## 📚 Additional Resources

- [Groq Documentation](https://console.groq.com/docs)
- [LangChain Providers](https://python.langchain.com/docs/integrations/llms/)
- [Free API List](https://github.com/public-apis/public-apis)
- [Indian Market Data APIs](https://blog.quantinsti.com/free-data-sources/)

---

**Note**: Free tiers are subject to change. Always check the provider's website for current limits and pricing.

**Pro Tip**: Start with Groq + Yahoo Finance for a completely free, production-ready system!
