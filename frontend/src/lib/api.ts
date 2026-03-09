import { Competitor, Analysis, Prediction, GapAnalysis, Conversation } from '../types'
import { auth } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const token = await auth.getIdToken()
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // Competitors
  async getCompetitors(): Promise<Competitor[]> {
    return this.request<Competitor[]>('/competitors')
  }

  async getCompetitor(id: string): Promise<Competitor> {
    return this.request<Competitor>(`/competitors/${id}`)
  }

  // Analyses
  async getAnalyses(competitorId?: string): Promise<Analysis[]> {
    const query = competitorId ? `?competitor_id=${competitorId}` : ''
    return this.request<Analysis[]>(`/analyses${query}`)
  }

  async getAnalysis(id: string): Promise<Analysis> {
    return this.request<Analysis>(`/analyses/${id}`)
  }

  // Predictions
  async getPredictions(competitorId?: string): Promise<Prediction[]> {
    const query = competitorId ? `?competitor_id=${competitorId}` : ''
    return this.request<Prediction[]>(`/predictions${query}`)
  }

  async createPrediction(competitorId: string): Promise<Prediction> {
    return this.request<Prediction>('/predictions', {
      method: 'POST',
      body: JSON.stringify({ competitor_id: competitorId }),
    })
  }

  // Gap Analysis
  async getGapAnalyses(): Promise<GapAnalysis[]> {
    return this.request<GapAnalysis[]>('/gaps')
  }

  async createGapAnalysis(competitorIds?: string[]): Promise<GapAnalysis> {
    return this.request<GapAnalysis>('/gaps', {
      method: 'POST',
      body: JSON.stringify({ competitor_ids: competitorIds }),
    })
  }

  // Scout Chatbot
  async sendMessage(message: string, conversationId?: string): Promise<{
    conversation_id: string
    answer: string
    intent: string
    data: any
    charts: any[]
    confidence: number
  }> {
    return this.request('/scout', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    })
  }

  async getConversations(): Promise<Conversation[]> {
    return this.request<Conversation[]>('/scout')
  }

  async getConversation(id: string): Promise<Conversation> {
    return this.request<Conversation>(`/scout?conversation_id=${id}`)
  }

  // Reports
  async getReport(): Promise<any> {
    return this.request('/report')
  }

  async regenerateReport(): Promise<any> {
    return this.request('/report?regenerate=true')
  }
}

export const api = new ApiClient()
