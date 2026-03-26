export interface Competitor {
  competitorId: string
  name: string
  website?: string
  description?: string
  category: string
  lastUpdated: string
}

export interface Ad {
  ad_id: string
  page_name: string
  ad_text?: string
  start_date?: string
  stop_date?: string
  platforms: string[]
  is_active: boolean
  creative_type: string
  scraped_at: string
}

export interface Analysis {
  analysis_id: string
  ad_id: string
  competitor_id: string
  timestamp: string
  creative_analysis: {
    visual_themes: string[]
    color_palette: string[]
    format: string
  }
  messaging_analysis: {
    themes: string[]
    keywords: string[]
    hooks: string[]
    ctas: string[]
  }
  confidence: number
}

export interface Prediction {
  prediction_id: string
  competitor_id: string
  timestamp: string
  reach_prediction: {
    min_reach: number
    max_reach: number
    avg_reach: number
  }
  engagement_prediction: {
    rate: number
    score: number
  }
  duration_prediction: {
    days: number
  }
  confidence: number
  llm_explanation?: string
}

export interface GapAnalysis {
  gap_analysis_id: string
  timestamp: string
  competitors_analyzed: string[]
  messaging_gaps: {
    common_themes: string[]
    underutilized_themes: string[]
    gaps: Array<{
      type: string
      description: string
      opportunity: string
    }>
  }
  creative_gaps: {
    overused_themes: string[]
    underused_themes: string[]
    gaps: Array<{
      type: string
      description: string
      opportunity: string
    }>
  }
  opportunities: Array<{
    type: string
    category: string
    description: string
    score: number
    priority: string
  }>
  confidence: number
  llm_explanation?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface Conversation {
  conversation_id: string
  user_id: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}
