# { "Depends": "py-genlayer:test" }
"""
GenLayer-Connect Core Library
==============================

Base classes and utilities for integrating external APIs with GenLayer Intelligent Contracts.

Author: GenLayer Community
License: MIT
"""

from genlayer import *
import json


class APIClient(gl.Contract):
    """
    Base class for API integrations.
    Provides common functionality for HTTP requests and response parsing.
    """
    
    def __init__(self):
        self.last_response = ""
        self.last_error = ""
        self.request_count = 0
        
    def _make_api_call(self, prompt: str, parser_instructions: str = "") -> str:
        """
        Make an API call using AI to handle the request and parse response.
        
        Args:
            prompt: Description of what data to fetch
            parser_instructions: Optional instructions for parsing the response
            
        Returns:
            Parsed API response data
        """
        self.request_count += 1
        
        full_prompt = f"""{prompt}

{parser_instructions if parser_instructions else 'Return ONLY the requested data in a clean format.'}

Important: 
- Make the actual API call
- Return real, current data
- Format the response clearly
- If the API call fails, return 'ERROR: [reason]'
"""
        
        def fetch_data():
            return gl.exec_prompt(full_prompt).strip()
        
        try:
            result = gl.eq_principle_strict_eq(fetch_data)
            self.last_response = result
            
            if result.startswith("ERROR:"):
                self.last_error = result
                return ""
            
            self.last_error = ""
            return result
        except Exception as e:
            self.last_error = f"ERROR: {str(e)}"
            return ""
    
    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON response safely"""
        try:
            # Remove markdown code blocks if present
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            return json.loads(response.strip())
        except:
            return {"error": "Failed to parse response", "raw": response}
    
    @gl.public.view
    def get_last_response(self) -> str:
        """Get the last API response"""
        return self.last_response
    
    @gl.public.view
    def get_last_error(self) -> str:
        """Get the last error message"""
        return self.last_error
    
    @gl.public.view
    def get_request_count(self) -> int:
        """Get total number of API requests made"""
        return self.request_count


class WeatherAPI(APIClient):
    """
    Weather data integration using OpenWeatherMap or similar services.
    Provides current weather, forecasts, and AI-powered analysis.
    """
    
    def __init__(self):
        super().__init__()
        self.cache_timeout = 3600  # 1 hour cache
        
    @gl.public.write
    def get_current_weather(self, location: str) -> str:
        """
        Get current weather for a location.
        
        Args:
            location: City name or coordinates
            
        Returns:
            Weather data as formatted string
        """
        prompt = f"""Fetch current weather data for {location} using a weather API (like OpenWeatherMap).

Include:
- Temperature (Celsius)
- Conditions (sunny, cloudy, rainy, etc.)
- Humidity percentage
- Wind speed (km/h)

Return in this format:
Location: [name]
Temperature: [temp]°C
Conditions: [description]
Humidity: [value]%
Wind: [speed] km/h"""
        
        return self._make_api_call(prompt)
    
    @gl.public.write
    def get_weather_forecast(self, location: str, days: int) -> str:
        """
        Get weather forecast for next N days.
        
        Args:
            location: City name
            days: Number of days to forecast (1-7)
            
        Returns:
            Forecast data
        """
        if days < 1 or days > 7:
            return "ERROR: Days must be between 1 and 7"
        
        prompt = f"""Fetch {days}-day weather forecast for {location}.

For each day return:
- Date
- High/Low temperature
- Conditions
- Precipitation chance

Format as a clear daily breakdown."""
        
        return self._make_api_call(prompt)
    
    @gl.public.write
    def analyze_weather_for_activity(self, location: str, activity: str) -> str:
        """
        AI analyzes weather suitability for specific activity.
        
        Args:
            location: City name
            activity: Activity type (e.g., "outdoor wedding", "hiking")
            
        Returns:
            AI analysis and recommendation
        """
        # First get the weather
        weather = self.get_current_weather(location)
        
        if weather.startswith("ERROR"):
            return weather
        
        # Now analyze it with AI
        analysis_prompt = f"""Based on this weather data:

{weather}

Analyze if conditions are suitable for: {activity}

Provide:
1. Suitability rating (1-10)
2. Key concerns or benefits
3. Recommendation (Go ahead / Postpone / Take precautions)
4. Specific advice

Be practical and helpful."""
        
        def analyze():
            return gl.exec_prompt(analysis_prompt).strip()
        
        return gl.eq_principle_strict_eq(analyze)


class CryptoPriceAPI(APIClient):
    """
    Cryptocurrency price data integration.
    Supports multiple tokens and AI-powered market analysis.
    """
    
    def __init__(self):
        super().__init__()
        
    @gl.public.write
    def get_token_price(self, token_symbol: str) -> str:
        """
        Get current price for a cryptocurrency.
        
        Args:
            token_symbol: Token symbol (BTC, ETH, etc.)
            
        Returns:
            Price data with 24h change
        """
        prompt = f"""Fetch current price data for {token_symbol.upper()} cryptocurrency using CoinGecko or similar API.

Return in this format:
Token: {token_symbol.upper()}
Price (USD): $[price]
24h Change: [percentage]%
24h High: $[high]
24h Low: $[low]
Market Cap: $[marketcap]

Use real, current data."""
        
        return self._make_api_call(prompt)
    
    @gl.public.write
    def get_multiple_prices(self, tokens: str) -> str:
        """
        Get prices for multiple tokens at once.
        
        Args:
            tokens: Comma-separated token symbols (e.g., "BTC,ETH,SOL")
            
        Returns:
            Price data for all tokens
        """
        token_list = [t.strip().upper() for t in tokens.split(",")]
        
        if len(token_list) > 10:
            return "ERROR: Maximum 10 tokens allowed"
        
        prompt = f"""Fetch current prices for these cryptocurrencies: {', '.join(token_list)}

For each token return:
Token | Price (USD) | 24h Change

Format as a clean table."""
        
        return self._make_api_call(prompt)
    
    @gl.public.write
    def analyze_price_trend(self, token_symbol: str) -> str:
        """
        AI analyzes price trend and provides insights.
        
        Args:
            token_symbol: Token symbol
            
        Returns:
            AI market analysis
        """
        # Get current price data
        price_data = self.get_token_price(token_symbol)
        
        if price_data.startswith("ERROR"):
            return price_data
        
        # AI analysis
        analysis_prompt = f"""Based on this cryptocurrency data:

{price_data}

Provide a brief market analysis:
1. Current trend (Bullish/Bearish/Neutral)
2. Key observation about 24h movement
3. Short-term outlook
4. Risk level (Low/Medium/High)

Be objective and data-driven. This is NOT financial advice."""
        
        def analyze():
            return gl.exec_prompt(analysis_prompt).strip()
        
        return gl.eq_principle_strict_eq(analyze)
    
    @gl.public.write
    def compare_tokens(self, token1: str, token2: str) -> str:
        """
        Compare two cryptocurrencies with AI analysis.
        
        Args:
            token1: First token symbol
            token2: Second token symbol
            
        Returns:
            Comparative analysis
        """
        prices = self.get_multiple_prices(f"{token1},{token2}")
        
        if prices.startswith("ERROR"):
            return prices
        
        comparison_prompt = f"""Compare these two cryptocurrencies:

{prices}

Provide:
1. Which has better 24h performance
2. Price difference analysis
3. Market cap comparison
4. Key differentiator

Be factual and balanced."""
        
        def compare():
            return gl.exec_prompt(comparison_prompt).strip()
        
        return gl.eq_principle_strict_eq(compare)


class NewsAPI(APIClient):
    """
    News and current events integration.
    Fetches headlines and provides AI-powered summaries.
    """
    
    def __init__(self):
        super().__init__()
        
    @gl.public.write
    def get_top_headlines(self, topic: str, count: int = 5) -> str:
        """
        Get top news headlines for a topic.
        
        Args:
            topic: News topic or keyword
            count: Number of headlines (1-10)
            
        Returns:
            News headlines with sources
        """
        if count < 1 or count > 10:
            return "ERROR: Count must be between 1 and 10"
        
        prompt = f"""Fetch the top {count} news headlines about "{topic}" from recent news APIs.

For each headline return:
- Title
- Source
- Brief summary (1 sentence)
- Published time (relative, like "2 hours ago")

Format clearly."""
        
        return self._make_api_call(prompt)
    
    @gl.public.write
    def summarize_news(self, topic: str) -> str:
        """
        Get AI-powered summary of recent news on a topic.
        
        Args:
            topic: News topic
            
        Returns:
            Comprehensive news summary
        """
        # Get headlines first
        headlines = self.get_top_headlines(topic, 5)
        
        if headlines.startswith("ERROR"):
            return headlines
        
        # AI summarization
        summary_prompt = f"""Based on these recent news headlines about {topic}:

{headlines}

Provide a comprehensive summary:
1. Main story/development
2. Key facts
3. Different perspectives if any
4. Current status

Be objective and factual."""
        
        def summarize():
            return gl.exec_prompt(summary_prompt).strip()
        
        return gl.eq_principle_strict_eq(summarize)
    
    @gl.public.write
    def analyze_sentiment(self, topic: str) -> str:
        """
        Analyze news sentiment about a topic.
        
        Args:
            topic: Topic to analyze
            
        Returns:
            Sentiment analysis
        """
        headlines = self.get_top_headlines(topic, 5)
        
        if headlines.startswith("ERROR"):
            return headlines
        
        sentiment_prompt = f"""Analyze the overall sentiment in these headlines about {topic}:

{headlines}

Provide:
1. Overall sentiment (Positive/Negative/Neutral/Mixed)
2. Sentiment score (1-10, where 1=very negative, 10=very positive)
3. Key themes
4. Tone analysis

Be objective."""
        
        def analyze():
            return gl.exec_prompt(sentiment_prompt).strip()
        
        return gl.eq_principle_strict_eq(analyze)


class SocialMediaAPI(APIClient):
    """
    Social media data integration.
    Tracks trending topics and sentiment analysis.
    """
    
    def __init__(self):
        super().__init__()
        
    @gl.public.write
    def get_trending_topics(self, platform: str = "twitter") -> str:
        """
        Get current trending topics on a platform.
        
        Args:
            platform: Social platform (twitter, reddit, etc.)
            
        Returns:
            List of trending topics
        """
        prompt = f"""Fetch current trending topics on {platform}.

Return the top 10 trending topics/hashtags with:
- Topic name
- Brief description (why it's trending)
- Estimated discussion volume (High/Medium/Low)

Format as a numbered list."""
        
        return self._make_api_call(prompt)
    
    @gl.public.write
    def analyze_topic_sentiment(self, topic: str, platform: str = "twitter") -> str:
        """
        Analyze social media sentiment about a topic.
        
        Args:
            topic: Topic or hashtag to analyze
            platform: Social platform
            
        Returns:
            Sentiment analysis
        """
        prompt = f"""Analyze social media sentiment about "{topic}" on {platform}.

Sample recent posts/tweets and provide:
1. Overall sentiment (Positive/Negative/Neutral/Mixed)
2. Sentiment breakdown (% positive, % negative, % neutral)
3. Common themes in discussions
4. Notable opinions or perspectives
5. Controversy level (Low/Medium/High)

Be objective and balanced."""
        
        return self._make_api_call(prompt)
    
    @gl.public.write
    def get_topic_engagement(self, topic: str) -> str:
        """
        Get engagement metrics for a topic across platforms.
        
        Args:
            topic: Topic to analyze
            
        Returns:
            Engagement data
        """
        prompt = f"""Fetch engagement metrics for "{topic}" across social media platforms.

Provide:
- Twitter: Tweets per hour, engagement rate
- Reddit: Active discussions, upvote ratio
- Overall: Trending direction (Rising/Stable/Declining)
- Peak activity time

Estimate if exact numbers aren't available."""
        
        return self._make_api_call(prompt)
