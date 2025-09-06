export const ChartCard = ({ title, children, className }) => {
  return (
    <div
      className={`bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow ${className}`}
    >
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
      </div>
      <div className="h-64">{children}</div>
    </div>
  )
}
