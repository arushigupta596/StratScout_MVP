# Scout AI - Now LLM-Powered! 🚀

## What Changed

Scout AI now uses **Claude 3 Sonnet** (via AWS Bedrock) to intelligently answer questions using your scraped data!

### Before (Rule-Based)
- Simple keyword matching
- Fixed response templates
- Limited understanding of questions
- Basic data formatting

### After (LLM-Powered)
- Natural language understanding
- Intelligent data analysis
- Context-aware responses
- Conversational follow-ups

## How It Works

### 1. Intent Detection
Detects what you're asking about:
- Competitor campaigns
- Market gaps
- Predictions
- Comparisons

### 2. Context Gathering
Pulls relevant data from DynamoDB:
- **Competitor-specific**: If you mention "Mamaearth", gets their 51 ads
- **General**: Gets sample data from all competitors
- **Predictions**: Includes forecast data when relevant
- **Gaps**: Includes market opportunities when relevant

### 3. LLM Generation
Sends to Claude 3 Sonnet with:
- **System Prompt**: "You are Scout, an AI assistant for competitive intelligence..."
- **User Query**: Your question
- **Context Data**: Up to 20 relevant campaigns, predictions, gaps
- **Conversation History**: Last 2 exchanges for context

### 4. Intelligent Response
Claude analyzes the data and provides:
- Specific insights from the campaigns
- Data-driven recommendations
- Clear, actionable answers
- Follow-up suggestions

## Example Queries

### Competitor Campaigns
**Q:** "What are Mamaearth's top performing campaigns?"

**A:** Claude will analyze Mamaearth's 51 campaigns and provide insights like:
- Most common messaging themes
- Platform distribution
- Active vs inactive campaigns
- Notable creative approaches

### Market Analysis
**Q:** "What gaps exist in the market?"

**A:** Claude will review the gap analysis data and explain:
- Top opportunities (sustainability, video content, etc.)
- Priority levels and why
- Actionable recommendations

### Comparisons
**Q:** "How does Minimalist compare to The Derma Co?"

**A:** Claude will compare their campaigns:
- Number of active campaigns
- Messaging differences
- Platform strategies
- Predicted performance

### Strategic Questions
**Q:** "What should I focus on for my next campaign?"

**A:** Claude will synthesize all data:
- Market gaps
- Competitor weaknesses
- Trending themes
- Specific recommendations

## Technical Details

### Data Provided to LLM

For each query, Claude receives:
```
Competitors (5):
  - Mamaearth (ID: comp-mamaearth)
  - The Derma Co (ID: comp-the-derma-co)
  ...

Recent Campaigns (up to 20):
  1. Mamaearth
     Text: [First 150 chars of ad text]
     Platforms: Facebook, Instagram
     Status: Active
  ...

Predictions (5):
  - comp-mamaearth: Avg reach 125000, Confidence 0.82
  ...

Market Opportunities (6):
  - messaging_gap: Sustainability messaging is underutilized (Priority: high)
  ...
```

### LLM Configuration
- **Model**: Claude 3 Sonnet (anthropic.claude-3-sonnet-20240229-v1:0)
- **Max Tokens**: 1000
- **Temperature**: 0.7 (balanced creativity/accuracy)
- **Region**: us-east-1

### Fallback Handling
If Bedrock fails:
- Returns simple data summary
- Suggests rephrasing question
- Maintains conversation flow

## Cost Impact

Claude 3 Sonnet pricing:
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

Estimated usage:
- ~500 tokens per query (input)
- ~300 tokens per response (output)
- Cost per query: ~$0.006

**Monthly estimate** (100 queries/month):
- Scout AI: ~$0.60/month
- Total platform: ~$25/month

Still well under budget!

## After Deployment

Once deployment completes (5-10 minutes):

1. Go to https://dh9mb4macowil.cloudfront.net
2. Sign in
3. Click "Scout AI"
4. Try these questions:
   - "What are Mamaearth's top performing campaigns?"
   - "What market gaps should I focus on?"
   - "How does Minimalist compare to competitors?"
   - "What messaging themes are working well?"

Scout AI will now provide intelligent, data-driven answers using Claude 3 Sonnet!

## Benefits

✅ **Natural Conversations** - Ask questions naturally
✅ **Data-Driven Insights** - Answers based on real scraped data
✅ **Context Aware** - Remembers conversation history
✅ **Actionable** - Provides specific recommendations
✅ **Scalable** - Can handle complex multi-part questions

Your competitive intelligence assistant just got a major upgrade! 🎉
