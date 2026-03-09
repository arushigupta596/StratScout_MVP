import { create } from 'zustand'
import { Competitor, Analysis, Prediction, GapAnalysis, Conversation } from '../types'

interface AppState {
  // Data
  competitors: Competitor[]
  analyses: Analysis[]
  predictions: Prediction[]
  gapAnalysis: GapAnalysis | null
  conversations: Conversation[]
  
  // UI State
  selectedCompetitor: string | null
  isLoading: boolean
  error: string | null
  
  // Actions
  setCompetitors: (competitors: Competitor[]) => void
  setAnalyses: (analyses: Analysis[]) => void
  setPredictions: (predictions: Prediction[]) => void
  setGapAnalysis: (gapAnalysis: GapAnalysis) => void
  setConversations: (conversations: Conversation[]) => void
  setSelectedCompetitor: (id: string | null) => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void
}

export const useStore = create<AppState>((set) => ({
  // Initial state
  competitors: [],
  analyses: [],
  predictions: [],
  gapAnalysis: null,
  conversations: [],
  selectedCompetitor: null,
  isLoading: false,
  error: null,
  
  // Actions
  setCompetitors: (competitors) => set({ competitors }),
  setAnalyses: (analyses) => set({ analyses }),
  setPredictions: (predictions) => set({ predictions }),
  setGapAnalysis: (gapAnalysis) => set({ gapAnalysis }),
  setConversations: (conversations) => set({ conversations }),
  setSelectedCompetitor: (id) => set({ selectedCompetitor: id }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}))
