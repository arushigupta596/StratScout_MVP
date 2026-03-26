import { LucideIcon } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: string
  trendUp?: boolean
}

export default function MetricCard({ title, value, icon: Icon, trend, trendUp }: MetricCardProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
          {trend && (
            <p className={`mt-2 text-sm ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
              {trend}
            </p>
          )}
        </div>
        <div className="p-3 bg-primary-50 rounded-lg">
          <Icon className="w-6 h-6 text-primary-600" />
        </div>
      </div>
    </div>
  )
}
