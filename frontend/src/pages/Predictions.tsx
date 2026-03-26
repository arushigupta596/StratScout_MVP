import { useEffect } from 'react'
import { TrendingUp, Users, Clock, Target } from 'lucide-react'
import { useStore } from '../store/useStore'
import { api } from '../lib/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Predictions() {
  const { predictions, competitors, setPredictions, setCompetitors, setLoading } = useStore()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [predictionsData, competitorsData] = await Promise.all([
        api.getPredictions(),
        api.getCompetitors(),
      ])
      setPredictions(predictionsData)
      setCompetitors(competitorsData)
    } catch (error) {
      console.error('Failed to load predictions:', error)
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data
  const chartData = predictions.map((pred) => {
    const competitor = competitors.find(c => c.competitorId === pred.competitor_id)
    return {
      name: competitor?.name || 'Unknown',
      reach: pred.reach_prediction.avg_reach,
      engagement: pred.engagement_prediction.score * 100,
    }
  })

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Campaign Predictions</h1>
        <p className="mt-2 text-gray-600">
          AI-powered predictions for competitor campaign performance
        </p>
      </div>

      {predictions.length > 0 ? (
        <>
          {/* Chart */}
          <div className="card mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Predicted Reach Comparison</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="reach" fill="#0ea5e9" name="Avg Reach" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Predictions List */}
          <div className="space-y-4">
            {predictions.map((prediction) => {
              const competitor = competitors.find(c => c.competitorId === prediction.competitor_id)
              return (
                <div key={prediction.prediction_id} className="card">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {competitor?.name || 'Unknown Competitor'}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Predicted on {new Date(prediction.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                    <span className="px-3 py-1 text-xs font-semibold bg-primary-100 text-primary-700 rounded-full">
                      {Math.round(prediction.confidence * 100)}% Confidence
                    </span>
                  </div>

                  {/* LLM Explanation */}
                  {prediction.llm_explanation && (
                    <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        <span className="font-semibold text-blue-900">AI Insight: </span>
                        {prediction.llm_explanation}
                      </p>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-blue-50 rounded-lg">
                        <Users className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Reach Range</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {prediction.reach_prediction.min_reach.toLocaleString()} - {prediction.reach_prediction.max_reach.toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">
                          Avg: {prediction.reach_prediction.avg_reach.toLocaleString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-green-50 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Engagement Rate</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {(prediction.engagement_prediction.rate * 100).toFixed(2)}%
                        </p>
                        <p className="text-xs text-gray-500">
                          Score: {prediction.engagement_prediction.score.toFixed(2)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-purple-50 rounded-lg">
                        <Clock className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Duration</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {prediction.duration_prediction.days} days
                        </p>
                        <p className="text-xs text-gray-500">
                          Estimated campaign length
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-orange-50 rounded-lg">
                        <Target className="w-5 h-5 text-orange-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Confidence</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {Math.round(prediction.confidence * 100)}%
                        </p>
                        <p className="text-xs text-gray-500">
                          Prediction accuracy
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </>
      ) : (
        <div className="card text-center py-12">
          <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No predictions available
          </h3>
          <p className="text-gray-600 mb-4">
            Generate predictions to forecast campaign performance
          </p>
          <button className="btn-primary">
            Generate Predictions
          </button>
        </div>
      )}
    </div>
  )
}
