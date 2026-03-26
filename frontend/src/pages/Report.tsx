import { useEffect, useState } from 'react'
import { FileText, TrendingUp, Lightbulb, Calendar, DollarSign, Target, Download } from 'lucide-react'
import { api } from '../lib/api'

interface Report {
  report_id: string
  timestamp: string
  executive_summary: string
  market_insights: {
    total_competitors: number
    total_campaigns_analyzed: number
    high_priority_opportunities: number
  }
  strategic_recommendations: Array<{
    title: string
    description: string
    priority: string
  }>
  campaign_ideas: Array<{
    title: string
    description: string
    target_audience: string
    estimated_reach: string
  }>
  timeline: Array<{
    phase: string
    duration: string
    activities: string
  }>
  budget_allocation: Array<{
    category: string
    percentage: number
    amount: string
    description: string
  }>
  confidence: number
}

export default function Report() {
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadReport()
  }, [])

  const loadReport = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getReport()
      setReport(data)
    } catch (err: any) {
      console.error('Failed to load report:', err)
      setError(err.message || 'Failed to generate report')
    } finally {
      setLoading(false)
    }
  }

  const regenerateReport = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.regenerateReport()
      setReport(data)
    } catch (err: any) {
      console.error('Failed to regenerate report:', err)
      setError(err.message || 'Failed to regenerate report')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Generating campaign report...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="card text-center py-12">
          <FileText className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Failed to Generate Report
          </h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button onClick={loadReport} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!report) {
    return null
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campaign Plan Report</h1>
          <p className="mt-2 text-gray-600">
            Data-driven campaign strategy based on competitive intelligence
          </p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={regenerateReport}
            disabled={loading}
            className="btn-secondary flex items-center space-x-2"
          >
            <TrendingUp className="w-4 h-4" />
            <span>Regenerate</span>
          </button>
          <button className="btn-primary flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="card mb-8 bg-gradient-to-r from-primary-50 to-purple-50 border-primary-200">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-primary-100 rounded-lg">
            <FileText className="w-6 h-6 text-primary-600" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">Executive Summary</h2>
            <p className="text-gray-700 leading-relaxed">{report.executive_summary}</p>
            <div className="mt-4 flex items-center space-x-6 text-sm">
              <span className="text-gray-600">
                Generated: {new Date(report.timestamp).toLocaleDateString()}
              </span>
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full font-medium">
                {Math.round(report.confidence * 100)}% Confidence
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Market Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <Target className="w-5 h-5 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">
              {report.market_insights.total_competitors}
            </span>
          </div>
          <p className="text-sm text-gray-600">Competitors Analyzed</p>
        </div>
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <span className="text-2xl font-bold text-gray-900">
              {report.market_insights.total_campaigns_analyzed}
            </span>
          </div>
          <p className="text-sm text-gray-600">Campaigns Reviewed</p>
        </div>
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <Lightbulb className="w-5 h-5 text-yellow-600" />
            <span className="text-2xl font-bold text-gray-900">
              {report.market_insights.high_priority_opportunities}
            </span>
          </div>
          <p className="text-sm text-gray-600">High Priority Opportunities</p>
        </div>
      </div>

      {/* Strategic Recommendations */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
          <Target className="w-5 h-5 text-primary-600 mr-2" />
          Strategic Recommendations
        </h2>
        <div className="space-y-4">
          {report.strategic_recommendations.map((rec, idx) => (
            <div key={idx} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                <span className={`px-2 py-1 text-xs font-medium rounded ${
                  rec.priority === 'high' ? 'bg-red-100 text-red-700' :
                  rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {rec.priority.toUpperCase()}
                </span>
              </div>
              <p className="text-sm text-gray-600">{rec.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Campaign Ideas */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
          <Lightbulb className="w-5 h-5 text-primary-600 mr-2" />
          Campaign Ideas
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {report.campaign_ideas.map((campaign, idx) => (
            <div key={idx} className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200">
              <h3 className="font-semibold text-gray-900 mb-3">{campaign.title}</h3>
              <p className="text-sm text-gray-600 mb-4">{campaign.description}</p>
              <div className="space-y-2 text-sm">
                <div className="flex items-center text-gray-700">
                  <Target className="w-4 h-4 mr-2 text-blue-600" />
                  <span>{campaign.target_audience}</span>
                </div>
                <div className="flex items-center text-gray-700">
                  <TrendingUp className="w-4 h-4 mr-2 text-green-600" />
                  <span>{campaign.estimated_reach}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
          <Calendar className="w-5 h-5 text-primary-600 mr-2" />
          Implementation Timeline
        </h2>
        <div className="space-y-4">
          {report.timeline.map((phase, idx) => (
            <div key={idx} className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-primary-700 font-semibold">{idx + 1}</span>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-semibold text-gray-900">{phase.phase}</h3>
                  <span className="text-sm text-gray-500">{phase.duration}</span>
                </div>
                <p className="text-sm text-gray-600">{phase.activities}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Budget Allocation */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
          <DollarSign className="w-5 h-5 text-primary-600 mr-2" />
          Budget Allocation
        </h2>
        <div className="space-y-4">
          {report.budget_allocation.map((item, idx) => (
            <div key={idx} className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{item.category}</span>
                  <span className="font-semibold text-primary-600">{item.percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
