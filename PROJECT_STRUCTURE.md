# StratScout Project Structure

## Directory Layout

```
stratscout-competitive-intelligence/
│
├── infrastructure/                    # AWS CDK Infrastructure as Code
│   ├── bin/
│   │   └── stratscout.ts             # CDK app entry point
│   ├── lib/
│   │   ├── stratscout-stack.ts       # Main stack
│   │   ├── data-layer-stack.ts       # DynamoDB, Aurora, S3
│   │   ├── compute-layer-stack.ts    # Lambda functions
│   │   ├── api-layer-stack.ts        # API Gateway, Cognito
│   │   └── frontend-stack.ts         # CloudFront, S3 hosting
│   ├── package.json
│   ├── tsconfig.json
│   └── cdk.json
│
├── backend/                           # Python Lambda Functions
│   ├── layers/                        # Lambda layers for shared dependencies
│   │   ├── common/                    # Common utilities
│   │   └── ai/                        # AI/ML libraries
│   │
│   ├── data_ingestion/                # Layer 1: Data Ingestion
│   │   ├── meta_ads/
│   │   │   ├── handler.py            # Meta Ads Library collector
│   │   │   ├── client.py             # Meta API client
│   │   │   └── models.py             # Data models
│   │   ├── google_trends/
│   │   │   ├── handler.py            # Google Trends collector
│   │   │   └── pytrends_client.py    # Pytrends wrapper
│   │   └── web_scraper/
│   │       ├── handler.py            # Web scraping service
│   │       └── playwright_scraper.py # Playwright implementation
│   │
│   ├── etl_processing/                # Layer 2: ETL Processing
│   │   ├── normalizer.py             # Data normalization
│   │   ├── deduplicator.py           # SHA-256 deduplication
│   │   ├── enricher.py               # Metadata enrichment
│   │   └── handler.py                # ETL orchestrator
│   │
│   ├── ai_analysis/                   # Layer 3: AI Intelligence
│   │   ├── bedrock_client.py         # Amazon Bedrock integration
│   │   ├── creative_analyzer.py      # Ad creative analysis
│   │   ├── messaging_decoder.py      # Messaging strategy extraction
│   │   ├── visual_analyzer.py        # Visual theme analysis
│   │   ├── prompts/                  # Bedrock prompt templates
│   │   │   ├── creative_analysis.txt
│   │   │   ├── messaging_analysis.txt
│   │   │   └── gap_analysis.txt
│   │   └── handler.py                # AI analysis orchestrator
│   │
│   ├── analytics/                     # Layer 4: Comparative Analytics
│   │   ├── postgres_queries.py       # PostgreSQL queries
│   │   ├── redis_cache.py            # Redis caching layer
│   │   ├── kpi_calculator.py         # KPI aggregation
│   │   ├── porter_analyzer.py        # Porter's Five Forces
│   │   └── handler.py                # Analytics API
│   │
│   ├── predictions/                   # Layer 5: Pattern Recognition & Predictions
│   │   ├── campaign_predictor.py     # Campaign predictions
│   │   ├── reach_model.py            # Reach prediction
│   │   ├── engagement_model.py       # Engagement prediction
│   │   ├── duration_model.py         # Duration forecasting
│   │   ├── pattern_detector.py       # Trend detection
│   │   ├── clustering.py             # ML clustering
│   │   └── handler.py                # Prediction API
│   │
│   ├── gap_analysis/                  # Layer 5: Gap Analysis
│   │   ├── messaging_gaps.py         # Messaging gap analysis
│   │   ├── creative_gaps.py          # Creative theme gaps
│   │   ├── timing_gaps.py            # Timing opportunity detection
│   │   ├── positioning_gaps.py       # Positioning analysis
│   │   ├── opportunity_scorer.py     # Opportunity prioritization
│   │   └── handler.py                # Gap analysis API
│   │
│   ├── scout_chatbot/                 # Layer 6: Scout Chatbot
│   │   ├── query_processor.py        # NLP query processing
│   │   ├── intent_classifier.py      # Intent detection
│   │   ├── data_retriever.py         # Data fetching
│   │   ├── response_generator.py     # Response formatting
│   │   ├── chart_generator.py        # Chart generation
│   │   ├── conversation_manager.py   # Context management
│   │   └── handler.py                # Chatbot API
│   │
│   ├── api/                           # API Gateway Handlers
│   │   ├── auth.py                   # Authentication middleware
│   │   ├── dashboard.py              # Dashboard endpoints
│   │   ├── competitors.py            # Competitor endpoints
│   │   ├── predictions.py            # Prediction endpoints
│   │   ├── gaps.py                   # Gap analysis endpoints
│   │   └── scout.py                  # Scout chatbot endpoints
│   │
│   ├── common/                        # Shared utilities
│   │   ├── config.py                 # Configuration
│   │   ├── logger.py                 # Logging setup
│   │   ├── errors.py                 # Error handling
│   │   ├── validators.py             # Data validation
│   │   └── utils.py                  # Helper functions
│   │
│   ├── requirements.txt               # Python dependencies
│   └── requirements-dev.txt           # Development dependencies
│
├── frontend/                          # React TypeScript Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── OverviewDashboard.tsx
│   │   │   │   ├── AlertCards.tsx
│   │   │   │   ├── MarketPositionChart.tsx
│   │   │   │   ├── PorterRadarChart.tsx
│   │   │   │   └── MessagingMixChart.tsx
│   │   │   ├── competitor/
│   │   │   │   ├── CompetitorDeepDive.tsx
│   │   │   │   ├── CreativeTimeline.tsx
│   │   │   │   └── VisualThemeAnalyzer.tsx
│   │   │   ├── predictions/
│   │   │   │   ├── CampaignPredictions.tsx
│   │   │   │   ├── ReachPredictionChart.tsx
│   │   │   │   └── EngagementForecast.tsx
│   │   │   ├── gaps/
│   │   │   │   ├── GapAnalysisDashboard.tsx
│   │   │   │   ├── OpportunityCards.tsx
│   │   │   │   └── PositioningMap.tsx
│   │   │   ├── scout/
│   │   │   │   ├── ScoutChatbot.tsx
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── QueryInput.tsx
│   │   │   │   └── ChartRenderer.tsx
│   │   │   └── common/
│   │   │       ├── Layout.tsx
│   │   │       ├── Navigation.tsx
│   │   │       └── Loading.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useCompetitors.ts
│   │   │   ├── usePredictions.ts
│   │   │   └── useScout.ts
│   │   ├── services/
│   │   │   ├── api.ts                # API client
│   │   │   ├── auth.ts               # Authentication
│   │   │   └── websocket.ts          # WebSocket client
│   │   ├── store/
│   │   │   ├── authStore.ts          # Auth state
│   │   │   ├── competitorStore.ts    # Competitor state
│   │   │   └── scoutStore.ts         # Scout state
│   │   ├── types/
│   │   │   ├── competitor.ts
│   │   │   ├── prediction.ts
│   │   │   ├── gap.ts
│   │   │   └── scout.ts
│   │   ├── utils/
│   │   │   ├── formatters.ts
│   │   │   └── validators.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── scripts/                           # Utility scripts
│   ├── deploy.sh                     # Deployment script
│   ├── seed_demo_data.py             # Demo data generator
│   └── test_apis.py                  # API testing script
│
├── tests/                             # Tests
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── e2e/                          # End-to-end tests
│
├── docs/                              # Documentation
│   ├── api/                          # API documentation
│   ├── architecture/                 # Architecture diagrams
│   └── deployment/                   # Deployment guides
│
├── .gitignore
├── README.md
├── MVP_PLAN.md
├── design.md
├── requirements.md
├── tasks.md
└── PROJECT_STRUCTURE.md
```

## Key Components

### Infrastructure (AWS CDK)
- Defines all AWS resources as code
- Separate stacks for data, compute, API, and frontend
- Enables reproducible deployments

### Backend (Python Lambda)
- Serverless functions for each service
- Event-driven architecture
- Shared layers for common dependencies

### Frontend (React + TypeScript)
- Modern React 18 with hooks
- TypeScript for type safety
- Tailwind CSS for styling
- Zustand for state management

## Data Flow

1. **Ingestion**: EventBridge triggers Lambda → Meta Ads API → DynamoDB/S3
2. **Processing**: DynamoDB Stream → ETL Lambda → Normalized data
3. **Analysis**: SQS → AI Analysis Lambda → Bedrock → Insights
4. **Predictions**: Analytics Lambda → ML models → Predictions
5. **Gap Analysis**: Gap Analysis Lambda → Opportunity scoring
6. **API**: API Gateway → Lambda handlers → Frontend
7. **Scout**: User query → Scout Lambda → Bedrock → Response

## Next Steps

1. Set up infrastructure with CDK
2. Implement data ingestion services
3. Build AI analysis engine
4. Create prediction models
5. Develop gap analysis
6. Build Scout chatbot
7. Create frontend dashboard
