import { useEffect, useState } from 'react'
import { Target, TrendingUp, Palette, Clock, MapPin } from 'lucide-react'
import { useStore } from '../store/useStore'
import { api } from '../lib/api'

export default function GapAnalysis() {
  const { gapAnalysis, setGapAnalysis, setLoading } = useStore()
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  useEffect(() => {
    loadGapAnalysis()
  }, [])

  const loadGapAnalysis = async () => {
    setLoading(true)
    try {
      const data = await api.getGapAnalyses()
      if (data.length > 0) {
        setGapAnalysis(data[0])
      }
    } catch (error) {
      console.error('Failed to load gap analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredOpportunities = gapAnalysis?.opportunities.filter(
    (opp) => selectedCategory === 'all' || opp.category === selectedCategory
  ) || []

  const categories = ['all', 'messaging', 'creative', 'timing', 'positioning']

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Gap Analysis</h1>
        <p className="mt-2 text-gray-600">
          Identify market opportunities and competitive gaps
        </p>
      </div>

      {gapAnalysis ? (
        <>
          {/* LLM Explanation */}
          {gapAnalysis.llm_explanation && (
            <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <Target className="w-5 h-5 text-primary-600 mr-2" />
                Strategic Insights
              </h2>
              <p className="text-gray-700 leading-relaxed">
                {gapAnalysis.llm_explanation}
              </p>
            </div>
          )}

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <Target className="w-5 h-5 text-primary-600" />
                <span className="text-2xl font-bold text-gray-900">
                  {gapAnalysis.opportunities.length}
                </span>
              </div>
              <p className="text-sm text-gray-600">Total Opportunities</p>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="w-5 h-5 text-red-600" />
                <span className="text-2xl font-bold text-gray-900">
                  {gapAnalysis.opportunities.filter(o => o.priority === 'high').length}
                </span>
              </div>
              <p className="text-sm text-gray-600">High Priority</p>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <Palette className="w-5 h-5 text-yellow-600" />
                <span className="text-2xl font-bold text-gray-900">
                  {gapAnalysis.creative_gaps.gaps.length}
                </span>
              </div>
              <p className="text-sm text-gray-600">Creative Gaps</p>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <Clock className="w-5 h-5 text-green-600" />
                <span className="text-2xl font-bold text-gray-900">
                  {Math.round(gapAnalysis.confidence * 100)}%
                </span>
              </div>
              <p className="text-sm text-gray-600">Confidence Score</p>
            </div>
          </div>

          {/* Category Filter */}
          <div className="mb-6">
            <div className="flex space-x-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category
                      ? 'bg-primary-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Opportunities List */}
          <div className="space-y-4">
            {filteredOpportunities.map((opportunity, idx) => (
              <div key={idx} className="card hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                        opportunity.priority === 'high' ? 'bg-red-100 text-red-700' :
                        opportunity.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {opportunity.priority.toUpperCase()}
                      </span>
                      <span className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">
                        {opportunity.category}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {opportunity.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h3>
                    <p className="text-gray-600 mb-4">{opportunity.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>Score: {Math.round(opportunity.score * 100)}%</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    {opportunity.category === 'messaging' && <Target className="w-6 h-6 text-primary-600" />}
                    {opportunity.category === 'creative' && <Palette className="w-6 h-6 text-purple-600" />}
                    {opportunity.category === 'timing' && <Clock className="w-6 h-6 text-green-600" />}
                    {opportunity.category === 'positioning' && <MapPin className="w-6 h-6 text-orange-600" />}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredOpportunities.length === 0 && (
            <div className="card text-center py-12">
              <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No opportunities in this category
              </h3>
              <p className="text-gray-600">
                Try selecting a different category to see more opportunities
              </p>
            </div>
          )}
        </>
      ) : (
        <div className="card text-center py-12">
          <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No gap analysis available
          </h3>
          <p className="text-gray-600 mb-4">
            Run a gap analysis to identify market opportunities
          </p>
          <button className="btn-primary">
            Run Gap Analysis
          </button>
        </div>
      )}
    </div>
  )
}
