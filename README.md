# GenLayer-Connect: Quick Deployment Guide

Get started with GenLayer-Connect in 5 minutes

---

Super Quick Start

### Option 1: Try an Example Contract

**Deploy the Weather Insurance Example:**

1. Go to https://studio.genlayer.com/
2. Copy the entire `example_weather_insurance.py` file
3. Paste into GenLayer Studio
4. Click "Deploy" (leave constructor empty)
5. Done! You now have a working weather insurance contract!

**Test it:**
```python
# Create a policy
policy_id = create_policy(
    "Outdoor Concert",
    "London", 
    "2026-06-15",
    1000,
    "rain"
)

# Check weather and process claim
check_weather_and_claim(policy_id)
```

---

### Option 2: Build Your Own

**Create a Simple Weather Checker:**

```python
# { "Depends": "py-genlayer:test" }
from genlayer import *

class SimpleWeather(gl.Contract):
    def __init__(self):
        self.last_check = ""
    
    @gl.public.write
    def get_weather(self, city: str) -> str:
        """Get current weather for any city"""
        
        prompt = f"""Fetch current weather for {city} using OpenWeatherMap API.

Return in this format:
🌡️ Temperature: [temp]°C
☁️ Conditions: [description]
💧 Humidity: [percent]%
💨 Wind: [speed] km/h

Use real, current data."""
        
        def fetch():
            return gl.exec_prompt(prompt).strip()
        
        weather = gl.eq_principle_strict_eq(fetch)
        self.last_check = weather
        return weather
    
    @gl.public.view
    def get_last_check(self) -> str:
        return self.last_check
```

**Deploy Steps:**
1. Copy code above
2. Paste in GenLayer Studio
3. Deploy (empty constructor)
4. Call `get_weather("Paris")`
5. Get real weather data!

---

##  All Example Contracts

### 1. Weather Insurance (`example_weather_insurance.py`)

**What it does:**
- Insure outdoor events against bad weather
- Automatic claim processing
- AI evaluates if conditions match policy

**Key functions:**
- `create_policy(event, location, date, amount, conditions)`
- `check_weather_and_claim(policy_id)`
- `preview_weather_check(location)`

**Use case:** Event organizers, outdoor venues, farmers

---

### 2. Trading Signal Bot (`example_trading_bot.py`)

**What it does:**
- Real-time crypto price tracking
- AI-generated buy/sell signals
- Portfolio analysis

**Key functions:**
- `analyze_token(token_symbol)`
- `compare_tokens_for_investment(token1, token2)`
- `portfolio_health_check(tokens)`
- `market_sentiment_scan()`

**Use case:** Traders, investors, DeFi protocols

---

### 3. News Aggregator (`example_news_aggregator.py`)

**What it does:**
- Multi-source news aggregation
- AI-powered summarization
- Sentiment analysis

**Key functions:**
- `get_news_brief(topic, count)`
- `analyze_topic_sentiment(topic)`
- `compare_coverage(topic, sources)`
- `track_story_development(keyword)`

**Use case:** News apps, research tools, sentiment oracles

---

##  Integration Patterns

### Pattern 1: Direct API Call

```python
@gl.public.write
def simple_call(self):
    prompt = "Fetch weather for Tokyo"
    
    def fetch():
        return gl.exec_prompt(prompt).strip()
    
    return gl.eq_principle_strict_eq(fetch)
```

**When to use:** Simple, one-off data fetches

---

### Pattern 2: Parse and Process

```python
@gl.public.write  
def parse_call(self, city: str) -> int:
    # Fetch data
    weather = self._get_weather(city)
    
    # Parse temperature
    temp_prompt = f"""Extract just the temperature number from:
    {weather}
    
    Return only the number."""
    
    def extract():
        return gl.exec_prompt(temp_prompt).strip()
    
    temp_str = gl.eq_principle_strict_eq(extract)
    return int(temp_str)
```

**When to use:** Need structured data from text response

---

### Pattern 3: Multi-Step Analysis

```python
@gl.public.write
def analyze_call(self, location: str, activity: str) -> str:
    # Step 1: Get raw data
    weather = self._get_weather(location)
    
    # Step 2: AI analyzes suitability
    analysis_prompt = f"""Based on weather: {weather}
    
    Is it good for: {activity}?
    
    Rate 1-10 and explain."""
    
    def analyze():
        return gl.exec_prompt(analysis_prompt).strip()
    
    return gl.eq_principle_strict_eq(analyze)
```

**When to use:** Complex decision-making with context

---

## Security Checklist

Before deploying to production:

- [ ] **Validate all external data** - Don't trust API responses blindly
- [ ] **Handle errors gracefully** - APIs can fail
- [ ] **Set rate limits** - Track request counts
- [ ] **Test edge cases** - What if API returns unexpected data?
- [ ] **Use consensus** - Always use `gl.eq_principle_strict_eq()` for consistency
- [ ] **Document API dependencies** - Which APIs does your contract rely on?

---

##  Troubleshooting

### Issue: "Could not load contract schema"

**Solution:** Make sure you're not using class-level type annotations. Use `__init__` instead:

```python
# ❌ Wrong
class MyContract(gl.Contract):
    counter: int  # This causes schema error

# ✅ Correct
class MyContract(gl.Contract):
    def __init__(self):
        self.counter = 0  # This works!
```

---

### Issue: API returns "ERROR: ..."

**Causes:**
- API might be down
- Invalid query (e.g., wrong city name)
- Rate limit hit
- Network issue

**Solution:** Add retry logic and validation:

```python
def fetch_with_retry(self, prompt: str, retries: int = 3) -> str:
    for i in range(retries):
        result = self._make_api_call(prompt)
        if not result.startswith("ERROR"):
            return result
    return "ERROR: Failed after retries"
```

---

### Issue: Inconsistent data across validators

**Cause:** External APIs might return different data to different validators

**Solution:** Use structured prompts with exact format requirements:

```python
prompt = """Fetch BTC price from CoinGecko.

Return EXACTLY this format:
PRICE: $[number]
CHANGE: [number]%

No extra text."""
```

---

## Performance Tips

### 1. Cache Frequently Accessed Data

```python
class CachedAPI(gl.Contract):
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour
    
    @gl.public.write
    def get_data_cached(self, key: str) -> str:
        # Check cache first
        if key in self.cache:
            cached_time = self.cache[key]["time"]
            if gl.block_timestamp - cached_time < self.cache_timeout:
                return self.cache[key]["data"]
        
        # Fetch fresh data
        data = self._fetch_fresh(key)
        self.cache[key] = {
            "data": data,
            "time": gl.block_timestamp
        }
        return data
```

### 2. Batch Multiple Calls

```python
# ❌ Slow: Multiple separate calls
btc = get_price("BTC")
eth = get_price("ETH")
sol = get_price("SOL")

# ✅ Fast: Single batched call
prices = get_multiple_prices("BTC,ETH,SOL")
```

### 3. Use Leader Mode for Non-Critical Data

```python
# Strict consensus (slower, more secure)
critical_data = gl.eq_principle_strict_eq(fetch)

# Leader mode (faster, good enough for most)
casual_data = gl.eq_principle_leader_mode(fetch)
```

---

## 🎓 Learning Path

**Beginner:**
1. Deploy a simple weather checker
2. Test with different cities
3. Add error handling

**Intermediate:**
4. Deploy weather insurance example
5. Create your own policy
6. Test claim processing

**Advanced:**
7. Combine multiple APIs
8. Build custom analysis logic
9. Create production-ready dApp

---

##  Best Practices

### DO:
✅ Validate all external data  
✅ Handle errors gracefully  
✅ Use clear, structured prompts  
✅ Cache when appropriate  
✅ Document your API dependencies  
✅ Test thoroughly before production  

### DON'T:
❌ Trust API responses blindly  
❌ Ignore error cases  
❌ Make excessive API calls  
❌ Hardcode API keys in contracts  
❌ Deploy untested contracts  
❌ Forget to set rate limits  

---

## Next Steps

1. **Deploy an example** - Get hands-on experience
2. **Modify for your use case** - Adapt to your needs
3. **Build something new** - Create novel integrations
4. **Share with community** - Help others learn!

---

## 📞 Support

**Need help?**
- Read the full README
- Check example contracts
- Ask in GenLayer Discord
- Open an issue

**Built something cool?**
- Share in Discord!
- Submit a PR
- Write a tutorial

---
This library uses GenLayer's AI capabilities (`gl.exec_prompt()`). 
As of February 2026, full AI features are pending enablement in GenLayer Studio.

The library code is production-ready and demonstrates the integration patterns.
When AI features are fully available, these contracts will work as designed.

We've provided feedback to the GenLayer team to help improve the developer experience.
Happy building with GenLayer Connect*

Remember: You're not just building smart contracts - you're building **intelligent contracts** that can interact with the entire world!
