// import { Button } from "@/components/ui/button";
// import {
//   FileDown,
//   Zap,
//   TrendingUp,
//   Leaf,
//   DollarSign,
//   Gauge,
//   Clock,
//   Sparkles,
// } from "lucide-react";
// import { cn } from "@/lib/utils";
// import { Pagination } from "@/components/Pagination";
// import { useState } from "react";
// import { BillSelector } from "@/components/bills/BillSelector";

// const InsightCard = ({ type, title, value, description, icon }) => (
//   <div
//     className={cn(
//       "bg-card rounded-xl border p-6 hover:shadow-md transition-all duration-200 hover:-translate-y-1 animate-fade-in",
//       type === "savings" &&
//         "border-green-200 bg-gradient-to-br from-green-50 to-emerald-50",
//       type === "trend" &&
//         "border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50",
//       type === "carbon" &&
//         "border-primary/20 bg-gradient-to-br from-primary/5 to-green-50"
//     )}
//   >
//     <div className="flex items-center gap-3 mb-3">
//       {icon}
//       <h3 className="font-semibold text-foreground">{title}</h3>
//     </div>
//     <div className="mb-2">
//       <span className="text-2xl font-bold text-foreground font-mono">
//         {value}
//       </span>
//     </div>
//     <p className="text-sm text-muted-foreground">{description}</p>
//   </div>
// );

// const RecommendationCard = ({
//   priority,
//   title,
//   description,
//   savings,
//   effort,
//   impact,
// }) => (
//   <div
//     className={cn(
//       "bg-card rounded-xl border p-6 hover:shadow-md transition-all duration-200 hover:-translate-y-1 animate-fade-in",
//       priority === "high" && "border-l-4 border-l-red-400",
//       priority === "medium" && "border-l-4 border-l-amber-400",
//       priority === "low" && "border-l-4 border-l-primary"
//     )}
//   >
//     <div className="flex justify-between items-start mb-3">
//       <div className="flex items-center gap-2">
//         <span
//           className={cn(
//             "px-2 py-1 rounded-full text-xs font-medium",
//             priority === "high" && "bg-red-100 text-red-700",
//             priority === "medium" && "bg-amber-100 text-amber-700",
//             priority === "low" && "bg-green-100 text-green-700"
//           )}
//         >
//           {priority.toUpperCase()} PRIORITY
//         </span>
//       </div>
//       <span className="text-lg font-semibold text-green-600 font-mono">
//         {savings}
//       </span>
//     </div>
//     <h4 className="font-semibold text-foreground mb-2">{title}</h4>
//     <p className="text-muted-foreground mb-4">{description}</p>
//     <div className="flex gap-4 text-sm">
//       <div className="flex items-center gap-1">
//         <Clock className="w-3 h-3 text-muted-foreground" />
//         <span className="text-muted-foreground">Effort: {effort}</span>
//       </div>
//       <div className="flex items-center gap-1">
//         <TrendingUp className="w-3 h-3 text-muted-foreground" />
//         <span className="text-muted-foreground">Impact: {impact}</span>
//       </div>
//     </div>
//   </div>
// );

// const ReportMetric = ({ label, value, change }) => (
//   <div className="text-center animate-fade-in">
//     <p className="text-sm text-muted-foreground mb-1">{label}</p>
//     <p className="text-xl font-semibold text-foreground font-mono mb-1">
//       {value}
//     </p>
//     <p className="text-xs text-muted-foreground">{change}</p>
//   </div>
// );

// // Mock data for more recommendations
// const allRecommendations = [
//   {
//     priority: "high",
//     title: "Optimize AC Temperature",
//     description:
//       "Increasing your AC temperature from 22°C to 24°C can reduce consumption by 20-30%",
//     savings: "Save ₹300/month",
//     effort: "Easy",
//     impact: "High",
//   },
//   {
//     priority: "medium",
//     title: "Upgrade Your Refrigerator",
//     description:
//       "Your 8-year-old 3-star fridge consumes 40% more energy than a new 5-star model",
//     savings: "Save ₹150/month",
//     effort: "One-time investment",
//     impact: "Long-term",
//   },
//   {
//     priority: "low",
//     title: "Switch to LED Lighting",
//     description:
//       "Replace remaining CFL/incandescent bulbs with LED for better efficiency",
//     savings: "Save ₹80/month",
//     effort: "Easy",
//     impact: "Medium",
//   },
//   {
//     priority: "medium",
//     title: "Install Smart Power Strips",
//     description:
//       "Prevent phantom power consumption from devices in standby mode",
//     savings: "Save ₹120/month",
//     effort: "Moderate",
//     impact: "Medium",
//   },
//   {
//     priority: "high",
//     title: "Use Timer for Water Heater",
//     description: "Set automated schedules to heat water only when needed",
//     savings: "Save ₹200/month",
//     effort: "Easy",
//     impact: "High",
//   },
//   {
//     priority: "low",
//     title: "Upgrade to Inverter AC",
//     description:
//       "Replace conventional AC with inverter technology for 30% better efficiency",
//     savings: "Save ₹400/month",
//     effort: "High investment",
//     impact: "Long-term",
//   },
// ];

// const Insights = () => {
//   const [currentPage, setCurrentPage] = useState(1);
//   const [isGenerating, setIsGenerating] = useState(false);
//   const [selectedBill, setSelectedBill] = useState(null);

//   const recommendationsPerPage = 3;
//   const totalPages = Math.ceil(
//     allRecommendations.length / recommendationsPerPage
//   );

//   const getCurrentRecommendations = () => {
//     const startIndex = (currentPage - 1) * recommendationsPerPage;
//     const endIndex = startIndex + recommendationsPerPage;
//     return allRecommendations.slice(startIndex, endIndex);
//   };

//   const handleGenerateAnalysis = () => {
//     setIsGenerating(true);
//     // Simulate API call
//     setTimeout(() => {
//       setIsGenerating(false);
//     }, 2000);
//   };

//   return (
//     <div className="p-8 animate-fade-in">
//       <header className="mb-8">
//         <div className="flex justify-between items-center mb-5">
//           <div>
//             <h1 className="text-3xl font-semibold text-foreground mb-2">
//               Smart Insights
//             </h1>
//             <p className="text-muted-foreground">
//               AI-powered analysis and personalized recommendations
//             </p>
//           </div>
//           <Button
//             onClick={handleGenerateAnalysis}
//             disabled={isGenerating}
//             className="bg-primary hover:bg-primary/90"
//           >
//             <Sparkles className="w-4 h-4 mr-2" />
//             {isGenerating ? "Generating..." : "Generate Analysis"}
//           </Button>

//         </div>
//         <BillSelector
//           selectedBill={selectedBill}
//           onBillChange={setSelectedBill}
//         />
//       </header>

//       {/* Key Insights Cards */}
//       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
//         <InsightCard
//           type="savings"
//           title="Potential Monthly Savings"
//           value="₹380"
//           description="By implementing our top 3 recommendations"
//           icon={<DollarSign className="w-5 h-5 text-green-600" />}
//         />
//         <InsightCard
//           type="trend"
//           title="Usage Trend"
//           value="+12%"
//           description="Higher than last month due to increased AC usage"
//           icon={<TrendingUp className="w-5 h-5 text-orange-500" />}
//         />
//         <InsightCard
//           type="carbon"
//           title="Carbon Impact"
//           value="180 kg CO₂"
//           description="Equivalent to planting 8 trees"
//           icon={<Leaf className="w-5 h-5 text-primary" />}
//         />
//       </div>

//       {/* Recommendations */}
//       <div className="mb-8">
//         <div className="flex justify-between items-center mb-6">
//           <h2 className="text-2xl font-semibold text-foreground flex items-center">
//             <Zap className="w-6 h-6 mr-2 text-primary" />
//             Personalized Recommendations
//           </h2>
//           <div className="text-sm text-muted-foreground">
//             Showing {getCurrentRecommendations().length} of{" "}
//             {allRecommendations.length} recommendations
//           </div>
//         </div>

//         <div className="space-y-4 mb-6">
//           {getCurrentRecommendations().map((recommendation, index) => (
//             <RecommendationCard
//               key={`${currentPage}-${index}`}
//               priority={recommendation.priority}
//               title={recommendation.title}
//               description={recommendation.description}
//               savings={recommendation.savings}
//               effort={recommendation.effort}
//               impact={recommendation.impact}
//             />
//           ))}
//         </div>

//         <div className="flex justify-center">
//           <Pagination
//             currentPage={currentPage}
//             totalPages={totalPages}
//             onPageChange={setCurrentPage}
//           />
//         </div>
//       </div>

//       {/* Monthly Report */}
//       <div className="bg-card rounded-xl border border-border p-6 hover:shadow-md transition-shadow animate-fade-in">
//         <div className="flex justify-between items-center mb-6">
//           <h3 className="text-xl font-semibold text-foreground flex items-center">
//             <Gauge className="w-5 h-5 mr-2 text-primary" />
//             Monthly Report
//           </h3>
//           <Button className="bg-primary hover:bg-primary/90">
//             <FileDown className="w-4 h-4 mr-2" />
//             Export PDF
//           </Button>
//         </div>

//         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
//           <ReportMetric
//             label="Total Consumption"
//             value="450 kWh"
//             change="+12% vs last month"
//           />
//           <ReportMetric
//             label="Total Cost"
//             value="₹2,456"
//             change="₹5.46 per kWh"
//           />
//           <ReportMetric
//             label="Daily Average"
//             value="14.5 kWh"
//             change="Peak day: 18.2 kWh"
//           />
//           <ReportMetric
//             label="Efficiency Score"
//             value="7.2/10"
//             change="Good performance"
//           />
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Insights;

// WOrking
// import React, { useState } from "react";
// import { Button } from "@/components/ui/button";
// import { BillSelector } from "../components/bills/BillSelector";
// import {
//   FileDown,
//   Zap,
//   TrendingUp,
//   Leaf,
//   DollarSign,
//   Gauge,
//   Clock,
//   Sparkles,
//   Loader2,
//   AlertCircle,
// } from "lucide-react";
// import { cn } from "@/lib/utils";
// import { Pagination } from "@/components/Pagination"; // Assuming you have this component
// import { useGetInsightReportQuery } from "@/features/api/InsightApi";

// // --- Helper Functions to Transform API Data ---

// const getPriorityString = (priority) => {
//   if (priority === 1) return "high";
//   if (priority === 2) return "medium";
//   return "low";
// };

// const formatCurrency = (amount) =>
//   new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(
//     amount || 0
//   );

// // Calculates total potential savings from the recommendations array
// const calculateTotalSavings = (recommendations = []) => {
//   const total = recommendations.reduce((sum, rec) => {
//     const match = rec.savings.match(/₹([\d,]+)/);
//     if (match) {
//       return sum + parseFloat(match[1].replace(/,/g, ""));
//     }
//     return sum;
//   }, 0);
//   return formatCurrency(total);
// };

// // --- Presentational Sub-components (from your static file) ---

// const InsightCard = ({ type, title, value, description, icon }) => (
//   <div
//     className={cn(
//       "bg-card rounded-xl border p-6 hover:shadow-md transition-all duration-200 hover:-translate-y-1 animate-fade-in",
//       type === "savings" &&
//         "border-green-200 bg-gradient-to-br from-green-50 to-emerald-50",
//       type === "trend" &&
//         "border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50",
//       type === "carbon" &&
//         "border-primary/20 bg-gradient-to-br from-primary/5 to-green-50"
//     )}
//   >
//     <div className="flex items-center gap-3 mb-3">
//       {icon}
//       <h3 className="font-semibold text-foreground">{title}</h3>
//     </div>
//     <div className="mb-2">
//       <span className="text-2xl font-bold text-foreground font-mono">
//         {value}
//       </span>
//     </div>
//     <p className="text-sm text-muted-foreground">{description}</p>
//   </div>
// );

// const RecommendationCard = ({
//   priority,
//   title,
//   description,
//   savings,
//   effort,
//   impact,
// }) => (
//   <div
//     className={cn(
//       "bg-card rounded-xl border p-6 hover:shadow-md transition-all duration-200 hover:-translate-y-1 animate-fade-in",
//       priority === "high" && "border-l-4 border-l-red-400",
//       priority === "medium" && "border-l-4 border-l-amber-400",
//       priority === "low" && "border-l-4 border-l-primary"
//     )}
//   >
//     <div className="flex justify-between items-start mb-3">
//       <div className="flex items-center gap-2">
//         <span
//           className={cn(
//             "px-2 py-1 rounded-full text-xs font-medium",
//             priority === "high" && "bg-red-100 text-red-700",
//             priority === "medium" && "bg-amber-100 text-amber-700",
//             priority === "low" && "bg-green-100 text-green-700"
//           )}
//         >
//           {priority.toUpperCase()} PRIORITY
//         </span>
//       </div>
//       <span className="text-lg font-semibold text-green-600 font-mono">
//         {savings}
//       </span>
//     </div>
//     <h4 className="font-semibold text-foreground mb-2">{title}</h4>
//     <p className="text-muted-foreground mb-4">{description}</p>
//     <div className="flex gap-4 text-sm">
//       <div className="flex items-center gap-1">
//         <Clock className="w-3 h-3 text-muted-foreground" />
//         <span className="text-muted-foreground">Effort: {effort}</span>
//       </div>
//       <div className="flex items-center gap-1">
//         <TrendingUp className="w-3 h-3 text-muted-foreground" />
//         <span className="text-muted-foreground">Impact: {impact}</span>
//       </div>
//     </div>
//   </div>
// );

// const ReportMetric = ({ label, value, change }) => (
//   <div className="text-center animate-fade-in">
//     <p className="text-sm text-muted-foreground mb-1">{label}</p>
//     <p className="text-xl font-semibold text-foreground font-mono mb-1">
//       {value}
//     </p>
//     <p className="text-xs text-muted-foreground">{change}</p>
//   </div>
// );

// const InsightSkeleton = () => (
//   <div className="space-y-8 animate-pulse">
//     <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//       <div className="h-40 bg-gray-200 rounded-xl"></div>
//       <div className="h-40 bg-gray-200 rounded-xl"></div>
//       <div className="h-40 bg-gray-200 rounded-xl"></div>
//     </div>
//     <div className="h-64 bg-gray-200 rounded-xl"></div>
//   </div>
// );

// const InsightsPage = () => {
//   const [selectedBillId, setSelectedBillId] = useState(null);
//   const [currentPage, setCurrentPage] = useState(1);

//   // --- Data Fetching ---
//   const {
//     data: insightReport,
//     isLoading,
//     isError,
//   } = useGetInsightReportQuery(selectedBillId, {
//     skip: !selectedBillId, // Don't fetch until a bill is selected
//   });

//   // --- Pagination Logic ---
//   const recommendations = insightReport?.recommendations || [];
//   const recommendationsPerPage = 3;
//   const totalPages = Math.ceil(recommendations.length / recommendationsPerPage);
//   const getCurrentRecommendations = () => {
//     const startIndex = (currentPage - 1) * recommendationsPerPage;
//     return recommendations.slice(
//       startIndex,
//       startIndex + recommendationsPerPage
//     );
//   };

//   // --- Main Render Logic ---
//   const renderContent = () => {
//     if (!selectedBillId) {
//       return (
//         <div className="text-center py-20 px-8 bg-white rounded-2xl border border-gray-200 shadow-sm">
//           <h2 className="text-2xl font-bold text-gray-700">
//             Please select a bill
//           </h2>
//           <p className="text-gray-500 mt-2">
//             Choose a billing period above to view its AI-powered insights.
//           </p>
//         </div>
//       );
//     }
//     if (isLoading) {
//       return (
//         <div className="text-center py-20">
//           <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto" />
//         </div>
//       );
//     }
//     if (isError || !insightReport) {
//       return (
//         <div className="text-center py-20 text-red-500 flex flex-col items-center">
//           <AlertCircle className="w-12 h-12 mb-4" />
//           <h2 className="text-2xl font-bold">Failed to Load Insights</h2>
//           <p>
//             The report for this bill could not be fetched. It may still be
//             generating.
//           </p>
//         </div>
//       );
//     }

//     const { kpis, recommendations } = insightReport;

//     return (
//       <div className="space-y-8">
//         {/* Key Insights Cards */}
//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//           <InsightCard
//             type="savings"
//             title="Potential Monthly Savings"
//             value={calculateTotalSavings(recommendations)}
//             description="By implementing our top recommendations"
//             icon={<DollarSign className="w-5 h-5 text-green-600" />}
//           />
//           <InsightCard
//             type="trend"
//             title="Usage Trend"
//             value={`${kpis.kwh_change_percent || 0}%`}
//             description="Compared to the previous billing period"
//             icon={<TrendingUp className="w-5 h-5 text-orange-500" />}
//           />
//           <InsightCard
//             type="carbon"
//             title="Carbon Impact"
//             value={`${(kpis.kwh_total * 0.82).toFixed(0)} kg CO₂`}
//             description="Equivalent to planting 3-4 trees"
//             icon={<Leaf className="w-5 h-5 text-primary" />}
//           />
//         </div>

//         {/* Recommendations */}
//         <div>
//           <div className="flex justify-between items-center mb-6">
//             <h2 className="text-2xl font-semibold text-foreground flex items-center">
//               <Zap className="w-6 h-6 mr-2 text-primary" />
//               Personalized Recommendations
//             </h2>
//           </div>
//           <div className="space-y-4 mb-6">
//             {getCurrentRecommendations().map((rec, index) => (
//               <RecommendationCard
//                 key={index}
//                 priority={getPriorityString(rec.priority)}
//                 title={rec.title}
//                 description={rec.description}
//                 savings={rec.savings}
//                 effort={rec.effort}
//                 impact={rec.impact}
//               />
//             ))}
//           </div>
//           <div className="flex justify-center">
//             <Pagination
//               currentPage={currentPage}
//               totalPages={totalPages}
//               onPageChange={setCurrentPage}
//             />
//           </div>
//         </div>

//         {/* Monthly Report */}
//         <div className="bg-card rounded-xl border border-border p-6 hover:shadow-md transition-shadow">
//           <div className="flex justify-between items-center mb-6">
//             <h3 className="text-xl font-semibold text-foreground flex items-center">
//               <Gauge className="w-5 h-5 mr-2 text-primary" />
//               Monthly Report
//             </h3>
//             <Button className="bg-primary hover:bg-primary/90">
//               <FileDown className="w-4 h-4 mr-2" />
//               Export PDF
//             </Button>
//           </div>
//           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
//             <ReportMetric
//               label="Total Consumption"
//               value={`${kpis.kwh_total.toFixed(2)} kWh`}
//               change={`${kpis.kwh_change_percent || 0}% vs last month`}
//             />
//             <ReportMetric
//               label="Total Cost"
//               value={formatCurrency(kpis.cost_total)}
//               change={`${formatCurrency(
//                 kpis.cost_total / kpis.kwh_total
//               )} per kWh`}
//             />
//             <ReportMetric
//               label="Daily Average"
//               value={`${(kpis.kwh_total / 30).toFixed(2)} kWh`}
//               change="Based on a 30-day period"
//             />
//             <ReportMetric
//               label="Efficiency Score"
//               value="7.2/10"
//               change="Good performance"
//             />
//           </div>
//         </div>
//       </div>
//     );
//   };

//   return (
//     <div className="p-8 animate-fade-in">
//       <header className="mb-8">
//         <div className="flex justify-between items-center mb-5">
//           <div>
//             <h1 className="text-3xl font-semibold text-foreground mb-2">
//               Smart Insights
//             </h1>
//             <p className="text-muted-foreground">
//               AI-powered analysis and personalized recommendations
//             </p>
//           </div>
//           <Button className="bg-primary hover:bg-primary/90">
//             <Sparkles className="w-4 h-4 mr-2" />
//             Generate Analysis
//           </Button>
//         </div>
//         <BillSelector
//           selectedBill={selectedBillId}
//           onBillChange={setSelectedBillId}
//         />
//       </header>
//       {renderContent()}
//     </div>
//   );
// };

// export default InsightsPage;

// Better Skeleton
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { BillSelector } from "@/components/bills/BillSelector";
import {
  FileDown,
  Zap,
  TrendingUp,
  Leaf,
  DollarSign,
  Gauge,
  Clock,
  Sparkles,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Pagination } from "@/components/Pagination";

import { toast } from "sonner";
import {
  useGetInsightReportQuery,
  useGetInsightStatusQuery,
  useRefreshInsightReportMutation,
} from "@/features/api/InsightApi";

// --- Helper Functions ---
const getPriorityString = (p) =>
  p === 1 ? "high" : p === 2 ? "medium" : "low";
const formatCurrency = (a) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(
    a || 0
  );
const calculateTotalSavings = (r = []) =>
  formatCurrency(
    r.reduce((sum, rec) => {
      const match = rec.savings.match(/₹([\d,]+)/);
      return match ? sum + parseFloat(match[1].replace(/,/g, "")) : sum;
    }, 0)
  );

// --- Presentational Sub-components ---
const InsightCard = ({ type, title, value, description, icon }) => (
  <div
    className={cn(
      "bg-card rounded-xl border p-6 hover:shadow-md transition-all duration-200 hover:-translate-y-1 animate-fade-in",
      type === "savings" &&
        "border-green-200 bg-gradient-to-br from-green-50 to-emerald-50",
      type === "trend" &&
        "border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50",
      type === "carbon" &&
        "border-primary/20 bg-gradient-to-br from-primary/5 to-green-50"
    )}
  >
    <div className="flex items-center gap-3 mb-3">
      {icon}
      <h3 className="font-semibold text-foreground">{title}</h3>
    </div>
    <div className="mb-2">
      <span className="text-2xl font-bold text-foreground font-mono">
        {value}
      </span>
    </div>
    <p className="text-sm text-muted-foreground">{description}</p>
  </div>
);

const RecommendationCard = ({
  priority,
  title,
  description,
  savings,
  effort,
  impact,
}) => (
  <div
    className={cn(
      "bg-card rounded-xl border p-6 hover:shadow-md transition-all duration-200 hover:-translate-y-1 animate-fade-in",
      priority === "high" && "border-l-4 border-l-red-400",
      priority === "medium" && "border-l-4 border-l-amber-400",
      priority === "low" && "border-l-4 border-l-primary"
    )}
  >
    <div className="flex justify-between items-start mb-3">
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "px-2 py-1 rounded-full text-xs font-medium",
            priority === "high" && "bg-red-100 text-red-700",
            priority === "medium" && "bg-amber-100 text-amber-700",
            priority === "low" && "bg-green-100 text-green-700"
          )}
        >
          {priority.toUpperCase()} PRIORITY
        </span>
      </div>
      <span className="text-lg font-semibold text-green-600 font-mono">
        {savings}
      </span>
    </div>
    <h4 className="font-semibold text-foreground mb-2">{title}</h4>
    <p className="text-muted-foreground mb-4">{description}</p>
    <div className="flex gap-4 text-sm">
      <div className="flex items-center gap-1">
        <Clock className="w-3 h-3 text-muted-foreground" />
        <span className="text-muted-foreground">Effort: {effort}</span>
      </div>
      <div className="flex items-center gap-1">
        <TrendingUp className="w-3 h-3 text-muted-foreground" />
        <span className="text-muted-foreground">Impact: {impact}</span>
      </div>
    </div>
  </div>
);

const ReportMetric = ({ label, value, change }) => (
  <div className="text-center animate-fade-in">
    <p className="text-sm text-muted-foreground mb-1">{label}</p>
    <p className="text-xl font-semibold text-foreground font-mono mb-1">
      {value}
    </p>
    <p className="text-xs text-muted-foreground">{change}</p>
  </div>
);

const InsightSkeleton = () => (
  <div className="space-y-8 animate-pulse">
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="h-40 bg-gray-200 rounded-xl"></div>
      <div className="h-40 bg-gray-200 rounded-xl"></div>
      <div className="h-40 bg-gray-200 rounded-xl"></div>
    </div>
    <div className="h-64 bg-gray-200 rounded-xl"></div>
  </div>
);

// --- The Main Page Component ---
const InsightsPage = () => {
  const [selectedBillId, setSelectedBillId] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);

  // --- API Hooks ---
  const {
    data: insightReport,
    isLoading: isLoadingReport,
    isError: isReportError,
    error: reportError,
    refetch: refetchReport,
  } = useGetInsightReportQuery(selectedBillId, { skip: !selectedBillId });

  // This hook will poll for status updates ONLY when `isGenerating` is true.
  const { data: insightStatus } = useGetInsightStatusQuery(selectedBillId, {
    skip: !isGenerating || !selectedBillId,
    pollingInterval: 5000, // Poll every 5 seconds
  });

  const [refreshInsightReport, { isLoading: isRefreshing }] =
    useRefreshInsightReportMutation();

  // Effect to handle the completion of the polling process
  useEffect(() => {
    if (insightStatus?.status === "completed") {
      setIsGenerating(false); // Stop polling
      toast.success("Analysis complete!", {
        description: "Your smart insights are ready.",
      });
      refetchReport(); // Fetch the final report
    } else if (insightStatus?.status === "failed") {
      setIsGenerating(false); // Stop polling
      toast.error("Analysis Failed", {
        description:
          "Something went wrong during generation. Please try again.",
      });
    }
  }, [insightStatus, refetchReport]);

  const handleGenerateAnalysis = () => {
    if (!selectedBillId) {
      toast.error("Please select a bill first.");
      return;
    }
    setIsGenerating(true);
    toast.info("Starting analysis...", {
      description:
        "This may take a few moments. We'll notify you when it's done.",
    });
    refreshInsightReport(selectedBillId);
  };

  // --- Pagination Logic ---
  const recommendations = insightReport?.recommendations || [];
  const recommendationsPerPage = 3;
  const totalPages = Math.ceil(recommendations.length / recommendationsPerPage);
  const getCurrentRecommendations = () => {
    const startIndex = (currentPage - 1) * recommendationsPerPage;
    return recommendations.slice(
      startIndex,
      startIndex + recommendationsPerPage
    );
  };

  // --- Main Render Logic ---
  const renderContent = () => {
    if (!selectedBillId) {
      return (
        <div className="text-center py-20 px-8 bg-white rounded-2xl border border-gray-200 shadow-sm">
          <h2 className="text-2xl font-bold text-gray-700">
            Please select a bill
          </h2>
          <p className="text-gray-500 mt-2">
            Choose a billing period above to view its AI-powered insights.
          </p>
        </div>
      );
    }
    if (isLoadingReport) {
      return <InsightSkeleton />;
    }
    if (isGenerating) {
      return (
        <div className="text-center py-20 px-8 bg-white rounded-2xl border border-gray-200 shadow-sm">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-700">
            Generating Insights...
          </h2>
          <p className="text-gray-500 mt-2">
            Our AI is analyzing your data. This can take a minute or two.
          </p>
        </div>
      );
    }
    // This is the beautiful empty state for when no report exists yet (404 error)
    if (isReportError && reportError.status === 404) {
      return (
        <div className="text-center py-20 px-8 bg-white rounded-2xl border border-gray-200 shadow-sm">
          <Sparkles className="w-12 h-12 text-primary mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Unlock Your Smart Insights
          </h2>
          <p className="text-gray-600 mb-8 max-w-lg mx-auto">
            Generate an AI-powered analysis of this bill to get personalized
            savings recommendations and a detailed breakdown of your energy
            usage.
          </p>
          <Button
            onClick={handleGenerateAnalysis}
            disabled={isRefreshing}
            className="bg-primary hover:bg-primary/90 px-8 py-3"
          >
            <Zap className="w-5 h-5 mr-2" />
            {isRefreshing ? "Starting..." : "Generate Your Insights"}
          </Button>
        </div>
      );
    }
    if (isReportError) {
      return (
        <div className="text-center py-20 text-red-500 flex flex-col items-center">
          <AlertCircle className="w-12 h-12 mb-4" />
          <h2 className="text-2xl font-bold">Failed to Load Insights</h2>
          <p>An unexpected error occurred. Please try again later.</p>
        </div>
      );
    }
    if (insightReport) {
      const { kpis, recommendations } = insightReport;
      return (
        <div className="space-y-8">
          {/* Insights */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <InsightCard
              type="savings"
              title="Potential Monthly Savings"
              value={calculateTotalSavings(recommendations)}
              description="By implementing our top recommendations"
              icon={<DollarSign className="w-5 h-5 text-green-600" />}
            />
            <InsightCard
              type="trend"
              title="Usage Trend"
              value={`${kpis.kwh_change_percent || 0}%`}
              description="Compared to the previous billing period"
              icon={<TrendingUp className="w-5 h-5 text-orange-500" />}
            />
            <InsightCard
              type="carbon"
              title="Carbon Impact"
              value={`${(kpis.kwh_total * 0.82).toFixed(0)} kg CO₂`}
              description="Equivalent to planting 3-4 trees"
              icon={<Leaf className="w-5 h-5 text-primary" />}
            />
          </div>
          {/* Recommendation */}
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-foreground flex items-center">
                <Zap className="w-6 h-6 mr-2 text-primary" />
                Personalized Recommendations
              </h2>
            </div>
            <div className="space-y-4 mb-6">
              {getCurrentRecommendations().map((rec, index) => (
                <RecommendationCard
                  key={index}
                  priority={getPriorityString(rec.priority)}
                  title={rec.title}
                  description={rec.description}
                  savings={rec.savings}
                  effort={rec.effort}
                  impact={rec.impact}
                />
              ))}
            </div>
            <div className="flex justify-center">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            </div>
          </div>
          {/* Monthly Report */}
          <div className="bg-card rounded-xl border border-border p-6 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-foreground flex items-center">
                <Gauge className="w-5 h-5 mr-2 text-primary" />
                Monthly Report
              </h3>
              <Button className="bg-primary hover:bg-primary/90">
                <FileDown className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <ReportMetric
                label="Total Consumption"
                value={`${kpis.kwh_total.toFixed(2)} kWh`}
                change={`${kpis.kwh_change_percent || 0}% vs last month`}
              />
              <ReportMetric
                label="Total Cost"
                value={formatCurrency(kpis.cost_total)}
                change={`${formatCurrency(
                  kpis.cost_total / kpis.kwh_total
                )} per kWh`}
              />
              <ReportMetric
                label="Daily Average"
                value={`${(kpis.kwh_total / 30).toFixed(2)} kWh`}
                change="Based on a 30-day period"
              />
              <ReportMetric
                label="Efficiency Score"
                value="7.2/10"
                change="Good performance"
              />
            </div>
          </div>
        </div>
      );
    }
    return null; // Should not be reached
  };

  return (
    <div className="p-8 animate-fade-in">
      <header className="mb-8">
        <div className="flex justify-between items-center mb-5">
          <div>
            <h1 className="text-3xl font-semibold text-foreground mb-2">
              Smart Insights
            </h1>
            <p className="text-muted-foreground">
              AI-powered analysis and personalized recommendations
            </p>
          </div>
          <Button
            onClick={handleGenerateAnalysis}
            disabled={isGenerating || isRefreshing}
            className="bg-primary hover:bg-primary/90"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            {isGenerating ? "Generating..." : "Regenerate Analysis"}
          </Button>
        </div>
        <BillSelector
          selectedBill={selectedBillId}
          onBillChange={setSelectedBillId}
        />
      </header>
      {renderContent()}
    </div>
  );
};

export default InsightsPage;
