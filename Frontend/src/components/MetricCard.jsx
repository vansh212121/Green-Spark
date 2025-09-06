import { TrendingUp, TrendingDown } from "lucide-react"
import { cn } from "@/lib/utils"

export const MetricCard = ({ title, value, change, changeType, subtitle }) => {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-all duration-200 hover:-translate-y-1">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        {change && changeType !== "neutral" && (
          <div
            className={cn(
              "flex items-center text-xs font-medium",
              changeType === "increase" ? "text-danger-400" : "text-success-400"
            )}
          >
            {changeType === "increase" ? (
              <TrendingUp className="w-3 h-3 mr-1" />
            ) : (
              <TrendingDown className="w-3 h-3 mr-1" />
            )}
            {change}
          </div>
        )}
      </div>
      <div className="mb-2">
        <span className="text-2xl font-semibold text-gray-900 font-mono">
          {value}
        </span>
      </div>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
      {change && changeType === "neutral" && (
        <p className="text-sm text-gray-500">{change}</p>
      )}
    </div>
  )
}
