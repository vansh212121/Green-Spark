// import { useState } from "react";
// import { MetricCard } from "@/components/MetricCard";
// import { ChartCard } from "@/components/ChartCard";
// import { BillSelector } from "@/components/BillSelector";
// import {
//   BarChart,
//   Bar,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   ResponsiveContainer,
//   PieChart,
//   Pie,
//   Cell,
//   LineChart,
//   Line,
//   AreaChart,
//   Area,
// } from "recharts";
// import { Button } from "@/components/ui/button";
// import { Calendar, Download, Zap } from "lucide-react";

// const monthlyData = [
//   { month: "Aug", consumption: 320, cost: 1890 },
//   { month: "Sep", consumption: 350, cost: 2010 },
//   { month: "Oct", consumption: 380, cost: 2190 },
//   { month: "Nov", consumption: 320, cost: 1890 },
//   { month: "Dec", consumption: 380, cost: 2190 },
//   { month: "Jan", consumption: 450, cost: 2456 },
// ];

// const billBreakdown = [
//   { name: "Energy Charges", value: 1680, color: "#22c55e" },
//   { name: "Fixed Charges", value: 180, color: "#3b82f6" },
//   { name: "Taxes & Duties", value: 596, color: "#f59e0b" },
// ];

// const dailyUsage = [
//   { day: "Mon", usage: 12.5, peak: 18.2 },
//   { day: "Tue", usage: 14.2, peak: 16.8 },
//   { day: "Wed", usage: 13.8, peak: 17.5 },
//   { day: "Thu", usage: 15.1, peak: 19.2 },
//   { day: "Fri", usage: 16.8, peak: 20.1 },
//   { day: "Sat", usage: 18.2, peak: 22.5 },
//   { day: "Sun", usage: 17.5, peak: 21.8 },
// ];

// const hourlyPattern = [
//   { hour: "00", consumption: 2.1 },
//   { hour: "02", consumption: 1.8 },
//   { hour: "04", consumption: 1.5 },
//   { hour: "06", consumption: 3.2 },
//   { hour: "08", consumption: 4.8 },
//   { hour: "10", consumption: 6.5 },
//   { hour: "12", consumption: 8.2 },
//   { hour: "14", consumption: 9.8 },
//   { hour: "16", consumption: 7.5 },
//   { hour: "18", consumption: 12.5 },
//   { hour: "20", consumption: 15.2 },
//   { hour: "22", consumption: 8.8 },
// ];

// const COLORS = ["#22c55e", "#3b82f6", "#f59e0b"];

// const Overview = () => {
//   const [selectedBill, setSelectedBill] = useState("jan-2025");
//   return (
//     <div className="p-8 animate-fade-in">
//       <header className="mb-8">
//         <div className="flex justify-between items-center mb-4">
//           <div>
//             <h1 className="text-3xl font-semibold text-gray-900 mb-2">
//               Energy Overview
//             </h1>
//             <p className="text-gray-600">
//               January 2025 • Last updated 2 hours ago
//             </p>
//           </div>
//           <div className="flex gap-3">
//             <Button variant="outline" size="sm">
//               <Calendar className="w-4 h-4 mr-2" />
//               Last 6 months
//             </Button>
//             <Button variant="outline" size="sm">
//               <Download className="w-4 h-4 mr-2" />
//               Export
//             </Button>
//           </div>
//         </div>

// <BillSelector
//   selectedBill={selectedBill}
//   onBillChange={setSelectedBill}
// />
//       </header>

//       {/* Key Metrics Cards */}
//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
//         <MetricCard
//           title="This Month"
//           value="₹2,456"
//           change="+12%"
//           changeType="increase"
//           subtitle="450 kWh consumed"
//         />
//         <MetricCard
//           title="Last Month"
//           value="₹2,190"
//           change="-8%"
//           changeType="decrease"
//           subtitle="380 kWh consumed"
//         />
//         <MetricCard
//           title="Average Daily"
//           value="₹79"
//           change="14.5 kWh/day"
//           changeType="neutral"
//           subtitle="Slightly above normal"
//         />
//         <MetricCard
//           title="Carbon Footprint"
//           value="180 kg CO₂"
//           change="-15%"
//           changeType="decrease"
//           subtitle="vs last month"
//         />
//       </div>

//       {/* Main Charts */}
//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
//         <ChartCard title="6-Month Usage Trend">
//           <ResponsiveContainer width="100%" height="100%">
//             <BarChart data={monthlyData}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
//               <XAxis dataKey="month" axisLine={false} tickLine={false} />
//               <YAxis axisLine={false} tickLine={false} />
//               <Bar dataKey="consumption" fill="#22c55e" radius={[4, 4, 0, 0]} />
//             </BarChart>
//           </ResponsiveContainer>
//         </ChartCard>

//         <ChartCard title="Current Bill Breakdown">
//           <ResponsiveContainer width="100%" height="100%">
//             <PieChart>
//               <Pie
//                 data={billBreakdown}
//                 cx="50%"
//                 cy="50%"
//                 outerRadius={80}
//                 dataKey="value"
//                 label={({ name, percent }) =>
//                   `${name} ${(percent * 100).toFixed(0)}%`
//                 }
//               >
//                 {billBreakdown.map((entry, index) => (
//                   <Cell
//                     key={`cell-${index}`}
//                     fill={COLORS[index % COLORS.length]}
//                   />
//                 ))}
//               </Pie>
//             </PieChart>
//           </ResponsiveContainer>
//         </ChartCard>

//         <ChartCard title="Daily Usage Pattern">
//           <ResponsiveContainer width="100%" height="100%">
//             <LineChart data={dailyUsage}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
//               <XAxis dataKey="day" axisLine={false} tickLine={false} />
//               <YAxis axisLine={false} tickLine={false} />
//               <Line
//                 type="monotone"
//                 dataKey="usage"
//                 stroke="#22c55e"
//                 strokeWidth={3}
//                 dot={{ fill: "#22c55e", strokeWidth: 2 }}
//               />
//               <Line
//                 type="monotone"
//                 dataKey="peak"
//                 stroke="#f59e0b"
//                 strokeWidth={2}
//                 strokeDasharray="5 5"
//                 dot={{ fill: "#f59e0b", strokeWidth: 2 }}
//               />
//             </LineChart>
//           </ResponsiveContainer>
//         </ChartCard>

//         <ChartCard title="24-Hour Consumption Pattern">
//           <ResponsiveContainer width="100%" height="100%">
//             <AreaChart data={hourlyPattern}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
//               <XAxis dataKey="hour" axisLine={false} tickLine={false} />
//               <YAxis axisLine={false} tickLine={false} />
//               <Area
//                 type="monotone"
//                 dataKey="consumption"
//                 stroke="#3b82f6"
//                 fill="#dbeafe"
//                 strokeWidth={2}
//               />
//             </AreaChart>
//           </ResponsiveContainer>
//         </ChartCard>
//       </div>

//       {/* Quick Actions & Recommendations */}
//       <div className="bg-white rounded-xl border border-gray-200 p-6">
//         <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
//           <Zap className="w-5 h-5 mr-2 text-primary-500" />
//           Quick Actions
//         </h3>
//         <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//           <div className="p-4 bg-gradient-subtle rounded-lg border border-primary-100">
//             <h4 className="font-medium text-gray-900 mb-2">
//               Update Appliance Usage
//             </h4>
//             <p className="text-sm text-gray-600 mb-3">
//               Your AC usage seems higher this month
//             </p>
//             <Button size="sm" className="bg-primary-500 hover:bg-primary-600">
//               Review Settings
//             </Button>
//           </div>
//           <div className="p-4 bg-gradient-subtle rounded-lg border border-primary-100">
//             <h4 className="font-medium text-gray-900 mb-2">
//               Potential Savings
//             </h4>
//             <p className="text-sm text-gray-600 mb-3">
//               You could save ₹300/month with these tips
//             </p>
//             <Button size="sm" className="bg-primary-500 hover:bg-primary-600">
//               View Insights
//             </Button>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Overview;

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area,
  Tooltip,
  Legend,
} from "recharts";
import {
  Calendar,
  Download,
  Zap,
  TrendingUp,
  TrendingDown,
  Activity,
  Leaf,
  DollarSign,
  BarChart3,
  AlertCircle,
  CheckCircle2,
  Clock,
  Target,
} from "lucide-react";
import { BillSelector } from "@/components/BillSelector";

// Sample data
const monthlyData = [
  { month: "Aug", consumption: 320, cost: 1890, target: 350 },
  { month: "Sep", consumption: 350, cost: 2010, target: 350 },
  { month: "Oct", consumption: 380, cost: 2190, target: 350 },
  { month: "Nov", consumption: 320, cost: 1890, target: 350 },
  { month: "Dec", consumption: 380, cost: 2190, target: 350 },
  { month: "Jan", consumption: 450, cost: 2456, target: 350 },
];

const billBreakdown = [
  { name: "Energy Charges", value: 1680, color: "#22c55e" },
  { name: "Fixed Charges", value: 180, color: "#3b82f6" },
  { name: "Taxes & Duties", value: 596, color: "#f59e0b" },
];

const dailyUsage = [
  { day: "Mon", usage: 12.5, peak: 18.2 },
  { day: "Tue", usage: 14.2, peak: 16.8 },
  { day: "Wed", usage: 13.8, peak: 17.5 },
  { day: "Thu", usage: 15.1, peak: 19.2 },
  { day: "Fri", usage: 16.8, peak: 20.1 },
  { day: "Sat", usage: 18.2, peak: 22.5 },
  { day: "Sun", usage: 17.5, peak: 21.8 },
];

const hourlyPattern = [
  { hour: "00", consumption: 2.1 },
  { hour: "02", consumption: 1.8 },
  { hour: "04", consumption: 1.5 },
  { hour: "06", consumption: 3.2 },
  { hour: "08", consumption: 4.8 },
  { hour: "10", consumption: 6.5 },
  { hour: "12", consumption: 8.2 },
  { hour: "14", consumption: 9.8 },
  { hour: "16", consumption: 7.5 },
  { hour: "18", consumption: 12.5 },
  { hour: "20", consumption: 15.2 },
  { hour: "22", consumption: 8.8 },
];

const insights = [
  {
    type: "warning",
    icon: AlertCircle,
    title: "High Peak Usage",
    description: "Your consumption spikes between 6-8 PM",
    action: "View Details",
    color: "bg-amber-50 border-amber-200",
  },
  {
    type: "success",
    icon: CheckCircle2,
    title: "Energy Efficient Week",
    description: "15% below your monthly average",
    action: "See Trends",
    color: "bg-green-50 border-green-200",
  },
  {
    type: "info",
    icon: Target,
    title: "Budget On Track",
    description: "₹544 remaining for January",
    action: "Manage Budget",
    color: "bg-blue-50 border-blue-200",
  },
];

// Enhanced metric card component
const MetricCard = ({
  title,
  value,
  change,
  changeType,
  subtitle,
  icon: Icon,
  trend = null,
}) => {
  const getChangeColor = () => {
    if (changeType === "increase") return "text-red-600 bg-red-50";
    if (changeType === "decrease") return "text-green-600 bg-green-50";
    return "text-gray-600 bg-gray-50";
  };

  const getTrendIcon = () => {
    if (changeType === "increase") return <TrendingUp className="w-3 h-3" />;
    if (changeType === "decrease") return <TrendingDown className="w-3 h-3" />;
    return <Activity className="w-3 h-3" />;
  };

  return (
    <Card className="relative overflow-hidden bg-white/60 backdrop-blur-sm border-gray-200 hover:shadow-lg transition-all duration-300">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="p-2 bg-primary-50 rounded-lg">
            <Icon className="w-5 h-5 text-primary-600" />
          </div>
          <Badge
            className={`px-2 py-1 text-xs font-medium ${getChangeColor()}`}
          >
            {getTrendIcon()}
            <span className="ml-1">{change}</span>
          </Badge>
        </div>
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">
            {title}
          </h3>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-500">{subtitle}</p>
        </div>
        {trend && (
          <div
            className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 to-primary-300"
            style={{ width: `${trend}%` }}
          />
        )}
      </CardContent>
    </Card>
  );
};

// Chart card wrapper
const ChartCard = ({ title, description, children, action }) => (
  <Card className="bg-white/60 backdrop-blur-sm border-gray-200 hover:shadow-lg transition-all duration-300">
    <CardHeader className="pb-3">
      <div className="flex items-center justify-between">
        <div>
          <CardTitle className="text-lg font-semibold text-gray-900">
            {title}
          </CardTitle>
          {description && (
            <CardDescription className="text-sm text-gray-600 mt-1">
              {description}
            </CardDescription>
          )}
        </div>
        {action && (
          <Button
            variant="ghost"
            size="sm"
            className="text-primary-600 hover:text-primary-700"
          >
            {action}
          </Button>
        )}
      </div>
    </CardHeader>
    <CardContent className="pt-2">
      <div className="h-80">{children}</div>
    </CardContent>
  </Card>
);

const Overview = () => {
  const [selectedPeriod, setSelectedPeriod] = useState("6months");
  const [selectedBill, setSelectedBill] = useState("jan-2025");

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-gray-50 p-8">
      {/* Enhanced Header Section */}
      <div className="mb-10">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
          <div className="mb-4 lg:mb-0">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Energy Dashboard
            </h1>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live monitoring</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span>Last updated 2 minutes ago</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                <span>January 2025</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button
              variant="outline"
              size="sm"
              className="bg-white/80 backdrop-blur-sm hover:bg-white"
            >
              <Calendar className="w-4 h-4 mr-2" />
              Last 6 months
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="bg-white/80 backdrop-blur-sm hover:bg-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Data
            </Button>
            <Button
              size="sm"
              className="bg-primary-500 hover:bg-primary-600 text-white"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Detailed Report
            </Button>
          </div>
        </div>
        <div className="mb-4 ">
          <BillSelector
            selectedBill={selectedBill}
            onBillChange={setSelectedBill}
          />
        </div>
        {/* Quick Insights Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {insights.map((insight, index) => (
            <Card
              key={index}
              className={`${insight.color} border hover:shadow-md transition-all duration-300`}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-white rounded-lg">
                    <insight.icon className="w-4 h-4 text-gray-700" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      {insight.title}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {insight.description}
                    </p>
                    <Button
                      variant="link"
                      size="sm"
                      className="p-0 h-auto text-primary-600 hover:text-primary-700"
                    >
                      {insight.action} →
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Enhanced Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <MetricCard
          title="Current Month"
          value="₹2,456"
          change="+12%"
          changeType="increase"
          subtitle="450 kWh consumed"
          icon={DollarSign}
          trend={75}
        />
        <MetricCard
          title="Previous Month"
          value="₹2,190"
          change="-8%"
          changeType="decrease"
          subtitle="380 kWh consumed"
          icon={BarChart3}
          trend={65}
        />
        <MetricCard
          title="Daily Average"
          value="₹79"
          change="14.5 kWh"
          changeType="neutral"
          subtitle="Slightly above normal"
          icon={Activity}
          trend={82}
        />
        <MetricCard
          title="Carbon Footprint"
          value="180 kg"
          change="-15%"
          changeType="decrease"
          subtitle="CO₂ emissions saved"
          icon={Leaf}
          trend={45}
        />
      </div>

      {/* Enhanced Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        <ChartCard
          title="6-Month Consumption Trend"
          description="Monthly usage vs target comparison"
          action="View Details"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={monthlyData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="month"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
              />
              <Bar
                dataKey="target"
                fill="#e2e8f0"
                radius={[2, 2, 0, 0]}
                name="Target"
              />
              <Bar
                dataKey="consumption"
                fill="#22c55e"
                radius={[4, 4, 0, 0]}
                name="Actual"
              />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Bill Breakdown"
          description="Current month cost distribution"
          action="Breakdown"
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={billBreakdown}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
              >
                {billBreakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
                formatter={(value) => [`₹${value}`, "Amount"]}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Weekly Usage Pattern"
          description="Daily consumption with peak indicators"
          action="Optimize"
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={dailyUsage}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="day"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
              />
              <Line
                type="monotone"
                dataKey="usage"
                stroke="#22c55e"
                strokeWidth={3}
                dot={{ fill: "#22c55e", strokeWidth: 2, r: 4 }}
                name="Average Usage"
              />
              <Line
                type="monotone"
                dataKey="peak"
                stroke="#f59e0b"
                strokeWidth={2}
                strokeDasharray="8 8"
                dot={{ fill: "#f59e0b", strokeWidth: 2, r: 4 }}
                name="Peak Usage"
              />
              <Legend />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="24-Hour Consumption"
          description="Hourly usage pattern analysis"
          action="Schedule"
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={hourlyPattern}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="hour"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
                formatter={(value) => [`${value} kWh`, "Consumption"]}
              />
              <Area
                type="monotone"
                dataKey="consumption"
                stroke="#3b82f6"
                fill="url(#colorConsumption)"
                strokeWidth={2}
              />
              <defs>
                <linearGradient
                  id="colorConsumption"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
                </linearGradient>
              </defs>
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Enhanced Quick Actions & Recommendations */}
      <Card className="bg-white/80 backdrop-blur-sm border-gray-200 hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-xl font-semibold text-gray-900">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Zap className="w-5 h-5 text-primary-600" />
            </div>
            Smart Recommendations
          </CardTitle>
          <CardDescription>
            AI-powered insights to optimize your energy consumption
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-6 bg-gradient-to-r from-primary-50 to-primary-100 rounded-xl border border-primary-200">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary-500 rounded-lg">
                  <TrendingDown className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Reduce Peak Usage
                  </h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Your AC usage peaks at 8 PM. Consider pre-cooling at 6 PM
                    for better rates.
                  </p>
                  <Badge className="bg-primary-500 text-white">
                    Save ₹400/month
                  </Badge>
                  <Button
                    size="sm"
                    className="mt-3 bg-primary-500 hover:bg-primary-600 text-white"
                  >
                    Set Schedule
                  </Button>
                </div>
              </div>
            </div>

            <div className="p-6 bg-gradient-to-r from-green-50 to-green-100 rounded-xl border border-green-200">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-green-500 rounded-lg">
                  <Leaf className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Solar Opportunity
                  </h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Based on your usage, solar panels could cover 70% of your
                    consumption.
                  </p>
                  <Badge className="bg-green-500 text-white">
                    ROI in 3.2 years
                  </Badge>
                  <Button
                    size="sm"
                    className="mt-3 bg-green-500 hover:bg-green-600 text-white"
                  >
                    Get Quote
                  </Button>
                </div>
              </div>
            </div>

            <div className="p-6 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl border border-blue-200">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-500 rounded-lg">
                  <Target className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Smart Appliances
                  </h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Upgrade to 5-star rated appliances to reduce consumption by
                    25%.
                  </p>
                  <Badge className="bg-blue-500 text-white">
                    Long-term savings
                  </Badge>
                  <Button
                    size="sm"
                    className="mt-3 bg-blue-500 hover:bg-blue-600 text-white"
                  >
                    View Options
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Overview;
