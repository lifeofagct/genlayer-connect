# { "Depends": "py-genlayer:test" }
"""
AI Trading Signal Generator
============================

Example contract showing how to use GenLayer-Connect's Crypto Price API.

This contract provides AI-powered trading signals:
- Monitors cryptocurrency prices
- AI analyzes market conditions
- Generates buy/sell/hold signals
- Tracks performance
"""

from genlayer import *


class TradingSignalBot(gl.Contract):
    """
    AI-powered trading signal generator using real crypto price data.
    
    Use Case: Traders can get AI analysis and signals for crypto investments.
    Note: This is for educational purposes, not financial advice.
    """
    
    def __init__(self):
        self.signals_history = []
        self.signal_count = 0
        
    @gl.public.write
    def analyze_token(self, token_symbol: str) -> str:
        """
        Get AI analysis and trading signal for a cryptocurrency.
        
        Args:
            token_symbol: Token to analyze (BTC, ETH, etc.)
            
        Returns:
            Comprehensive AI analysis with signal
        """
        # Fetch current price data
        price_prompt = f"""Fetch current price data for {token_symbol.upper()} using CoinGecko API.

Return in this exact format:
Price: $[price]
24h Change: [percentage]%
24h High: $[high]
24h Low: $[low]
Volume: $[volume]
Market Cap: $[marketcap]

Use real, current data."""
        
        def get_price():
            return gl.exec_prompt(price_prompt).strip()
        
        price_data = gl.eq_principle_strict_eq(get_price)
        
        if "ERROR" in price_data:
            return price_data
        
        # AI analyzes and generates signal
        analysis_prompt = f"""You are an AI trading analyst. Analyze this cryptocurrency data:

{price_data}

Token: {token_symbol.upper()}

Provide analysis in this EXACT format:

SIGNAL: [BUY / SELL / HOLD]
CONFIDENCE: [1-10 score]
TREND: [Bullish / Bearish / Neutral]
KEY POINTS:
- [Point 1]
- [Point 2]
- [Point 3]
REASONING: [2-3 sentence explanation]
RISK LEVEL: [Low / Medium / High]
TIMEFRAME: [Short-term / Medium-term / Long-term]

IMPORTANT DISCLAIMER: This is AI analysis, not financial advice. Always do your own research.

Be objective and data-driven."""
        
        def analyze():
            return gl.exec_prompt(analysis_prompt).strip()
        
        analysis = gl.eq_principle_strict_eq(analyze)
        
        # Save to history
        self.signal_count += 1
        self.signals_history.append({
            "token": token_symbol.upper(),
            "timestamp": gl.block_timestamp,
            "analysis": analysis
        })
        
        # Keep only last 50 signals
        if len(self.signals_history) > 50:
            self.signals_history.pop(0)
        
        return f"""
🤖 AI TRADING SIGNAL ANALYSIS
═══════════════════════════════

Token: {token_symbol.upper()}

📊 MARKET DATA:
{price_data}

🎯 AI ANALYSIS:
{analysis}

⚠️ DISCLAIMER: This is automated AI analysis for educational purposes only.
Not financial advice. Always DYOR (Do Your Own Research).
"""
    
    @gl.public.write
    def compare_tokens_for_investment(self, token1: str, token2: str) -> str:
        """
        Compare two tokens and get AI recommendation.
        
        Args:
            token1: First token symbol
            token2: Second token symbol
            
        Returns:
            Comparative analysis
        """
        # Get both prices
        prices_prompt = f"""Fetch current prices for {token1.upper()} and {token2.upper()}.

For each return:
Token | Price | 24h Change | Market Cap

Use CoinGecko or similar API."""
        
        def get_prices():
            return gl.exec_prompt(prices_prompt).strip()
        
        prices = gl.eq_principle_strict_eq(get_prices)
        
        # AI comparison
        comparison_prompt = f"""Compare these two cryptocurrencies for investment:

{prices}

Provide:
1. Which has better recent performance?
2. Which has more growth potential?
3. Risk comparison
4. Recommendation: Which to choose and why?
5. Portfolio suggestion: Should investor hold both?

Format clearly with reasoning.
Note: This is analysis, not financial advice."""
        
        def compare():
            return gl.exec_prompt(comparison_prompt).strip()
        
        comparison = gl.eq_principle_strict_eq(compare)
        
        return f"""
⚖️ TOKEN COMPARISON
═══════════════════

{token1.upper()} vs {token2.upper()}

📊 PRICE DATA:
{prices}

🤖 AI COMPARISON:
{comparison}

⚠️ Educational analysis only, not financial advice.
"""
    
    @gl.public.write
    def portfolio_health_check(self, tokens: str) -> str:
        """
        Analyze a portfolio of tokens and provide health report.
        
        Args:
            tokens: Comma-separated token symbols (e.g., "BTC,ETH,SOL")
            
        Returns:
            Portfolio health analysis
        """
        token_list = [t.strip().upper() for t in tokens.split(",")]
        
        if len(token_list) > 10:
            return "ERROR: Maximum 10 tokens allowed"
        
        # Get all prices
        prices_prompt = f"""Fetch current prices and 24h performance for: {', '.join(token_list)}

For each token return:
- Symbol
- Current Price
- 24h Change %
- Trend (Up/Down/Stable)

Use a table format."""
        
        def get_prices():
            return gl.exec_prompt(prices_prompt).strip()
        
        portfolio_data = gl.eq_principle_strict_eq(get_prices)
        
        # AI portfolio analysis
        analysis_prompt = f"""Analyze this cryptocurrency portfolio:

{portfolio_data}

Provide a portfolio health report:

1. OVERALL HEALTH SCORE: [1-10]

2. DIVERSIFICATION: [Good / Needs Improvement]
   - Analysis of portfolio balance

3. RISK ASSESSMENT: [Low / Medium / High]
   - Key risk factors

4. PERFORMANCE SUMMARY:
   - Best performers
   - Underperformers
   - Overall trend

5. RECOMMENDATIONS:
   - Should they rebalance?
   - Any concerning holdings?
   - Suggestions for improvement

Be specific and actionable.
Disclaimer: Educational analysis only."""
        
        def analyze():
            return gl.exec_prompt(analysis_prompt).strip()
        
        analysis = gl.eq_principle_strict_eq(analyze)
        
        return f"""
💼 PORTFOLIO HEALTH REPORT
═══════════════════════════

Holdings: {', '.join(token_list)}

📊 CURRENT DATA:
{portfolio_data}

🤖 AI ANALYSIS:
{analysis}

⚠️ This is automated analysis for educational purposes.
Not financial advice. Market conditions change rapidly.
"""
    
    @gl.public.view
    def get_signal_history(self, count: int = 10) -> str:
        """
        Get recent signal history.
        
        Args:
            count: Number of recent signals to retrieve
            
        Returns:
            Signal history
        """
        if not self.signals_history:
            return "No signals generated yet"
        
        recent = self.signals_history[-count:]
        
        result = "📜 RECENT SIGNALS:\n\n"
        for i, signal in enumerate(reversed(recent), 1):
            result += f"{i}. {signal['token']} - Timestamp: {signal['timestamp']}\n"
            result += f"   {signal['analysis'][:200]}...\n\n"
        
        return result
    
    @gl.public.write
    def market_sentiment_scan(self) -> str:
        """
        Scan overall crypto market sentiment.
        
        Returns:
            Market-wide sentiment analysis
        """
        sentiment_prompt = """Analyze current overall cryptocurrency market sentiment.

Check major tokens (BTC, ETH, etc.) and recent market news.

Provide:
1. MARKET MOOD: [Fear / Greed / Neutral]
2. TREND: [Bullish / Bearish / Sideways]
3. KEY FACTORS:
   - Major news or events
   - Notable price movements
   - Market drivers
4. SHORT-TERM OUTLOOK:
   - Next 24-48 hours prediction
5. INVESTOR ADVICE:
   - What should investors watch?

Base on real current data."""
        
        def scan():
            return gl.exec_prompt(sentiment_prompt).strip()
        
        sentiment = gl.eq_principle_strict_eq(scan)
        
        return f"""
🌍 CRYPTO MARKET SENTIMENT SCAN
═══════════════════════════════

{sentiment}

📊 Generated at block: {gl.block_timestamp}

⚠️ Market conditions are volatile. This is analysis, not advice.
"""
