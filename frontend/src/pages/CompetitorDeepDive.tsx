import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ExternalLink, TrendingUp, Palette, MessageSquare } from 'lucide-react'
import { useStore } from '../store/useStore'
import { api } from '../lib/api'
import { Competitor, Analysis } from '../types'

export default function CompetitorDeepDive() {
  const { id } = useParams<{ id: string }>()
  const { setLoading } = useStore()
  const [competitor, setCompetitor] = useState<Competitor | null>(null)
  const [analyses, setAnalyses] = useState<Analysis[]>([])

  useEffect(() => {
    if (id) {
      loadCompetitorData(id)
    }
  }, [id])

  const loadCompetitorData = async (competitorId: string) => {
    setLoading(true)
    try {
      const [competitorData, analysesData] = await Promise.all([
        api.getCompetitor(competitorId),
        api.getAnalyses(competitorId),
      ])
      setCompetitor(competitorData)
      setAnalyses(analysesData)
    } catch (error) {
      console.error('Failed to load competitor data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!competitor) {
    return (
      <div className="p-8">
        <div className="card text-center py-12">
          <p className="text-gray-600">Loading competitor data...</p>
        </div>
      </div>
    )
  }

  // Aggregate themes and keywords
  const allThemes = analyses.flatMap(a => a.messaging_analysis.themes)
  const allKeywords = analyses.flatMap(a => a.messaging_analysis.keywords)
  const allColors = analyses.flatMap(a => a.creative_analysis.color_palette)
  
  const topThemes = [...new Set(allThemes)].slice(0, 10)
  const topKeywords = [...new Set(allKeywords)].slice(0, 15)
  const topColors = [...new Set(allColors)].slice(0, 8)

  return (
    <div className="p-8">
      {/* Back Button */}
      <Link to="/dashboard" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Dashboard
      </Link>

      {/* Header */}
      <div className="card mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{competitor.name}</h1>
            <p className="text-gray-600 mb-4">{competitor.description}</p>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span className="px-3 py-1 bg-gray-100 rounded-full">{competitor.category}</span>
              {competitor.website && (
                <a
                  href={competitor.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-primary-600 hover:text-primary-700"
                >
                  <ExternalLink className="w-4 h-4 mr-1" />
                  Visit Website
                </a>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Last Updated</p>
            <p className="text-lg font-semibold text-gray-900">
              {new Date(competitor.lastUpdated).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <span className="text-2xl font-bold text-gray-900">{analyses.length}</span>
          </div>
          <p className="text-sm text-gray-600">Total Analyses</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <MessageSquare className="w-5 h-5 text-green-600" />
            <span className="text-2xl font-bold text-gray-900">{topThemes.length}</span>
          </div>
          <p className="text-sm text-gray-600">Messaging Themes</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <Palette className="w-5 h-5 text-purple-600" />
            <span className="text-2xl font-bold text-gray-900">{topColors.length}</span>
          </div>
          <p className="text-sm text-gray-600">Color Palette</p>
        </div>
      </div>

      {/* Messaging Analysis */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Messaging Strategy</h2>
        
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Top Themes</h3>
          <div className="flex flex-wrap gap-2">
            {topThemes.map((theme, idx) => (
              <span key={idx} className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm">
                {theme}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {topKeywords.map((keyword, idx) => (
              <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                {keyword}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Creative Analysis */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Creative Strategy</h2>
        
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Color Palette</h3>
          <div className="flex flex-wrap gap-3">
            {topColors.map((color, idx) => (
              <div key={idx} className="flex items-center space-x-2">
                <div
                  className="w-8 h-8 rounded border border-gray-300"
                  style={{ backgroundColor: color }}
                />
                <span className="text-sm text-gray-600">{color}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Analyses */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Analyses</h2>
        <div className="space-y-4">
          {analyses.slice(0, 5).map((analysis) => (
            <div key={analysis.analysis_id} className="border-b border-gray-100 pb-4 last:border-0">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {new Date(analysis.timestamp).toLocaleDateString()}
                  </p>
                  <p className="text-xs text-gray-500">
                    Format: {analysis.creative_analysis.format}
                  </p>
                </div>
                <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded">
                  {Math.round(analysis.confidence * 100)}% confidence
                </span>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {analysis.messaging_analysis.themes.slice(0, 3).map((theme, idx) => (
                  <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                    {theme}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
