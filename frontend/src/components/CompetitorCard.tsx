import { Link } from 'react-router-dom'
import { ExternalLink, TrendingUp } from 'lucide-react'
import { Competitor } from '../types'

interface CompetitorCardProps {
  competitor: Competitor
}

export default function CompetitorCard({ competitor }: CompetitorCardProps) {
  return (
    <Link to={`/competitor/${competitor.competitorId}`} className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{competitor.name}</h3>
          <p className="text-sm text-gray-500">{competitor.category}</p>
        </div>
        {competitor.website && (
          <a
            href={competitor.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 hover:text-gray-600"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
      
      {competitor.description && (
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">{competitor.description}</p>
      )}
      
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <span className="text-xs text-gray-500">
          Updated {new Date(competitor.lastUpdated).toLocaleDateString()}
        </span>
        <div className="flex items-center text-sm text-primary-600">
          <TrendingUp className="w-4 h-4 mr-1" />
          View Details
        </div>
      </div>
    </Link>
  )
}
