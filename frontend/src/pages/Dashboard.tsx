import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, Users, Target, AlertCircle } from 'lucide-react'
import { useStore } from '../store/useStore'
import { api } from '../lib/api'
import MetricCard from '../components/MetricCard'

export default function Dashboard() {
  const { competitors, gapAnalysis, setCompetitors, setGapAnalysis, setLoading } = useStore()
  const [topOpportunities, setTopOpportunities] = useState<any[]>([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [competitorsData, gapData] = await Promise.all([
        api.getCompetitors(),
        api.getGapAnalyses(),
      ])
      
      setCompetitors(competitorsData)
      
      if (gapData.length > 0) {
        const latest = gapData[0]
        setGapAnalysis(latest)
        setTopOpportunities(latest.opportunities.slice(0, 3))
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Competitive Intelligence Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Track and analyze your competitors in the Indian D2C beauty market
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Competitors Tracked"
          value={competitors.length}
          icon={Users}
          trend="+2 this month"
          trendUp={true}
        />
        <MetricCard
          title="Active Campaigns"
          value="47"
          icon={TrendingUp}
          trend="+12% vs last month"
          trendUp={true}
        />
        <MetricCard
          title="Opportunities"
          value={gapAnalysis?.opportunities.length || 0}
          icon={Target}
          trend="3 high priority"
          trendUp={true}
        />
        <MetricCard
          title="Confidence Score"
          value={gapAnalysis ? `${Math.round(gapAnalysis.confidence * 100)}%` : 'N/A'}
          icon={AlertCircle}
          trend="Based on latest analysis"
          trendUp={true}
        />
      </div>

      {/* Top Opportunities */}
      {topOpportunities.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Top Opportunities</h2>
            <Link to="/gaps" className="text-sm text-primary-600 hover:text-primary-700">
              View all →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {topOpportunities.map((opp, idx) => (
              <div key={idx} className="card">
                <div className="flex items-start justify-between mb-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    opp.priority === 'high' ? 'bg-red-100 text-red-700' :
                    opp.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {opp.priority.toUpperCase()}
                  </span>
                  <span className="text-sm font-semibold text-gray-900">
                    {Math.round(opp.score * 100)}%
                  </span>
                </div>
                <h3 className="font-medium text-gray-900 mb-1">{opp.type}</h3>
                <p className="text-sm text-gray-600">{opp.description}</p>
                <div className="mt-3">
                  <span className="text-xs text-gray-500">{opp.category}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
