# { "Depends": "py-genlayer:test" }
"""
AI News Aggregator & Sentiment Analyzer
========================================

Example contract showing how to use GenLayer-Connect's News API.

This contract provides:
- Real-time news aggregation
- AI-powered summarization
- Sentiment analysis
- Topic tracking
"""

from genlayer import *


class NewsAggregator(gl.Contract):
    """
    AI-powered news aggregator with sentiment analysis.
    
    Use Case: Stay informed on topics with AI-curated summaries.
    """
    
    def __init__(self):
        self.tracked_topics = []
        self.news_cache = {}
        
    @gl.public.write
    def get_news_brief(self, topic: str, article_count: int = 5) -> str:
        """
        Get a brief news summary on any topic.
        
        Args:
            topic: Topic to search for
            article_count: Number of articles to include (1-10)
            
        Returns:
            Curated news brief with AI summary
        """
        if article_count < 1 or article_count > 10:
            return "ERROR: Article count must be between 1 and 10"
        
        # Fetch headlines
        headlines_prompt = f"""Fetch the top {article_count} recent news headlines about "{topic}".

For each headline return:
📰 Title: [headline]
   Source: [news source]
   Summary: [1 sentence summary]
   Time: [how long ago]

Use NewsAPI or similar service. Get real, current news."""
        
        def get_headlines():
            return gl.exec_prompt(headlines_prompt).strip()
        
        headlines = gl.eq_principle_strict_eq(get_headlines)
        
        if "ERROR" in headlines:
            return headlines
        
        # AI creates comprehensive brief
        brief_prompt = f"""Create a news brief about "{topic}" from these headlines:

{headlines}

Format as:

📋 NEWS BRIEF: {topic.upper()}
{'='*50}

QUICK SUMMARY:
[2-3 sentence overview of main developments]

KEY STORIES:
{headlines}

BOTTOM LINE:
[1-2 sentence takeaway]

LAST UPDATED: [current time]

Be clear and informative."""
        
        def create_brief():
            return gl.exec_prompt(brief_prompt).strip()
        
        brief = gl.eq_principle_strict_eq(create_brief)
        
        # Cache for later reference
        self.news_cache[topic] = {
            "timestamp": gl.block_timestamp,
            "brief": brief
        }
        
        return brief
    
    @gl.public.write
    def analyze_topic_sentiment(self, topic: str) -> str:
        """
        Analyze news sentiment about a topic.
        
        Args:
            topic: Topic to analyze
            
        Returns:
            Sentiment analysis report
        """
        # Get recent headlines
        headlines_prompt = f"""Fetch 10 recent news headlines about "{topic}".

List each headline with its source."""
        
        def get_headlines():
            return gl.exec_prompt(headlines_prompt).strip()
        
        headlines = gl.eq_principle_strict_eq(get_headlines)
        
        # AI sentiment analysis
        sentiment_prompt = f"""Analyze the sentiment in these news headlines about "{topic}":

{headlines}

Provide a sentiment analysis report:

OVERALL SENTIMENT: [Positive / Negative / Neutral / Mixed]
SENTIMENT SCORE: [1-10, where 1=very negative, 10=very positive]

BREAKDOWN:
- Positive articles: [count & %]
- Negative articles: [count & %]
- Neutral articles: [count & %]

TONE ANALYSIS:
[Describe the overall tone - optimistic, cautious, critical, etc.]

KEY THEMES:
- [Theme 1]
- [Theme 2]
- [Theme 3]

SENTIMENT TREND: [Improving / Declining / Stable]

NOTABLE POINTS:
[Any particularly strong positive or negative coverage]

Be objective and evidence-based."""
        
        def analyze_sentiment():
            return gl.exec_prompt(sentiment_prompt).strip()
        
        sentiment = gl.eq_principle_strict_eq(analyze_sentiment)
        
        return f"""
🎭 SENTIMENT ANALYSIS REPORT
═══════════════════════════════

Topic: {topic}

{sentiment}

📊 Analysis Date: Block {gl.block_timestamp}

Note: Sentiment analysis based on headline data. 
Full article context may provide additional nuance.
"""
    
    @gl.public.write
    def compare_coverage(self, topic: str, sources: str) -> str:
        """
        Compare how different news sources cover the same topic.
        
        Args:
            topic: Topic to compare
            sources: Comma-separated news sources (e.g., "CNN,BBC,Reuters")
            
        Returns:
            Coverage comparison analysis
        """
        source_list = [s.strip() for s in sources.split(",")]
        
        if len(source_list) < 2:
            return "ERROR: Need at least 2 sources to compare"
        
        if len(source_list) > 5:
            return "ERROR: Maximum 5 sources allowed"
        
        # Fetch coverage from each source
        coverage_prompt = f"""For the topic "{topic}", fetch recent headlines from these news sources:
{', '.join(source_list)}

For each source, provide:
- Source name
- 2-3 recent headlines about this topic
- Overall tone (positive/negative/neutral)

Format clearly by source."""
        
        def get_coverage():
            return gl.exec_prompt(coverage_prompt).strip()
        
        coverage = gl.eq_principle_strict_eq(get_coverage)
        
        # AI compares coverage
        comparison_prompt = f"""Compare how these news sources cover "{topic}":

{coverage}

Analyze:

1. COVERAGE DIFFERENCES:
   - Which sources emphasize what aspects?
   - Any notably different perspectives?

2. BIAS ANALYSIS:
   - Which source seems most neutral?
   - Any apparent editorial slant?

3. COMPLETENESS:
   - Which provides most comprehensive coverage?
   - Any missing important angles?

4. TONE COMPARISON:
   - Sentiment differences between sources

5. RECOMMENDATION:
   - Best source for balanced coverage
   - Should readers consult multiple sources?

Be fair and objective. Note: Brief headline analysis only."""
        
        def compare():
            return gl.exec_prompt(comparison_prompt).strip()
        
        comparison = gl.eq_principle_strict_eq(compare)
        
        return f"""
📊 MEDIA COVERAGE COMPARISON
═══════════════════════════════

Topic: {topic}
Sources: {', '.join(source_list)}

📰 COVERAGE DATA:
{coverage}

🔍 AI ANALYSIS:
{comparison}

Note: Analysis based on headlines. Full articles may show additional nuance.
"""
    
    @gl.public.write
    def track_story_development(self, story_keyword: str) -> str:
        """
        Track how a story develops over time.
        
        Args:
            story_keyword: Key term to track
            
        Returns:
            Story development analysis
        """
        # Get timeline of coverage
        timeline_prompt = f"""Search for news about "{story_keyword}" and create a timeline.

Provide:
- Initial reports (when story broke)
- Major developments
- Latest updates
- Current status

Format chronologically with dates/times."""
        
        def get_timeline():
            return gl.exec_prompt(timeline_prompt).strip()
        
        timeline = gl.eq_principle_strict_eq(get_timeline)
        
        # AI analyzes development
        development_prompt = f"""Analyze how this story has developed:

{timeline}

Provide:

STORY ARC:
- How it started
- Key turning points
- Current state

NARRATIVE SHIFTS:
- How has the story changed?
- What new information emerged?

MOMENTUM:
- Is coverage increasing or decreasing?
- Still developing or concluded?

WHAT TO WATCH:
- What might happen next?
- Key questions remaining?

Be analytical and forward-looking."""
        
        def analyze_development():
            return gl.exec_prompt(development_prompt).strip()
        
        development = gl.eq_principle_strict_eq(analyze_development)
        
        return f"""
📈 STORY DEVELOPMENT TRACKER
═══════════════════════════════

Story: {story_keyword}

⏱️ TIMELINE:
{timeline}

🔍 DEVELOPMENT ANALYSIS:
{development}

Last Updated: Block {gl.block_timestamp}
"""
    
    @gl.public.write
    def daily_news_digest(self, topics: str) -> str:
        """
        Get a daily digest covering multiple topics.
        
        Args:
            topics: Comma-separated topics (e.g., "Tech,Politics,Economy")
            
        Returns:
            Multi-topic daily digest
        """
        topic_list = [t.strip() for t in topics.split(",")]
        
        if len(topic_list) > 5:
            return "ERROR: Maximum 5 topics allowed"
        
        # Get headlines for all topics
        digest_prompt = f"""Create a daily news digest for these topics: {', '.join(topic_list)}

For each topic, provide:
- 2-3 top headlines
- Brief summary
- Why it matters

Format as a clean, readable digest."""
        
        def create_digest():
            return gl.exec_prompt(digest_prompt).strip()
        
        digest = gl.eq_principle_strict_eq(create_digest)
        
        return f"""
📰 DAILY NEWS DIGEST
{'='*50}

Topics: {', '.join(topic_list)}
Date: Block {gl.block_timestamp}

{digest}

{'='*50}
End of digest. Stay informed! 📱
"""
    
    @gl.public.view
    def get_cached_topics(self) -> str:
        """View recently cached news topics"""
        if not self.news_cache:
            return "No cached news yet"
        
        result = "📚 CACHED NEWS TOPICS:\n\n"
        for topic, data in self.news_cache.items():
            result += f"- {topic} (Block {data['timestamp']})\n"
        
        return result
