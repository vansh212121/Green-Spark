import React, { useMemo, useState } from "react";
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
  Tooltip,
  Legend,
  ZAxis,
  ScatterChart,
  Scatter,
} from "recharts";
import {
  Calendar,
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
  FileText,
} from "lucide-react";
import { BillSelector } from "@/components/bills/BillSelector";
import { Link } from "react-router-dom";
import { useGetBillByIdQuery } from "@/features/api/billApi";

const InsightCard = ({ type, title, description, action, icon: Icon }) => {
  const colorConfig = {
    warning: "bg-amber-50 border-amber-200",
    success: "bg-green-50 border-green-200",
    info: "bg-blue-50 border-blue-200",
  };
  return (
    <Card
      className={`${colorConfig[type]} border hover:shadow-md transition-all duration-300`}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-white rounded-lg">
            <Icon className="w-4 h-4 text-gray-700" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900 mb-1">{title}</h4>
            <p className="text-sm text-gray-600 mb-2">{description}</p>
            <Button
              variant="link"
              size="sm"
              className="p-0 h-auto text-primary-600 hover:text-primary-700"
            >
              {action} →
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Enhanced metric card component
const MetricCard = ({
  title,
  value,
  change,
  changeType,
  subtitle,
  icon: Icon,
}) => {
  const getChangeColor = () => {
    if (changeType === "increase") return "text-red-600 bg-red-100";
    if (changeType === "decrease") return "text-green-600 bg-green-100";
    return "text-gray-600 bg-gray-100";
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
          <div className="p-2 bg-primary-100 rounded-lg">
            <Icon className="w-5 h-5 text-primary-600" />
          </div>
          <Badge
            className={`flex items-center px-2 py-1 text-xs font-medium ${getChangeColor()}`}
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
      </CardContent>
    </Card>
  );
};

const ChartCard = ({ title, description, children }) => (
  <Card className="shadow-sm hover:shadow-lg transition-shadow duration-300">
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      <CardDescription>{description}</CardDescription>
    </CardHeader>
    <CardContent className="h-80">{children}</CardContent>
  </Card>
);

const Overview = () => {
  const [selectedBill, setSelectedBill] = useState(null);

  const {
    data: billData,
    isLoading,
    isError,
  } = useGetBillByIdQuery(selectedBill, {
    skip: !selectedBill,
  });

  const { metrics, chartsData } = useMemo(() => {
    if (!billData) return { metrics: null, chartsData: null };

    const formatCurrency = (amount) =>
      new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
      }).format(amount || 0);

    const totalBill = {
      title: `Bill for ${new Date(billData.billing_period_start).toLocaleString(
        "default",
        { month: "long" }
      )}`,
      value: formatCurrency(billData.cost_total),
      subtitle: `${billData.kwh_total.toFixed(2)} kWh consumed`,
      change: `${formatCurrency(billData.cost_total / billData.kwh_total)}/kWh`,
    };

    let highestConsumer = {
      value: "N/A",
      subtitle: "No appliances found",
      change: "0%",
    };
    if (billData.user_appliances && billData.user_appliances.length > 0) {
      const topAppliance = billData.user_appliances.reduce(
        (max, app) =>
          app.estimates[0]?.estimated_cost > max.estimates[0]?.estimated_cost
            ? app
            : max,
        billData.user_appliances[0]
      );
      const topEstimate = topAppliance.estimates[0];
      highestConsumer = {
        value: topAppliance.custom_name,
        subtitle: `${topEstimate.estimated_kwh.toFixed(2)} kWh`,
        change: `${(
          (topEstimate.estimated_cost / billData.cost_total) *
          100
        ).toFixed(0)}%`,
      };
    }

    const startDate = new Date(billData.billing_period_start);
    const endDate = new Date(billData.billing_period_end);
    const daysInPeriod = (endDate - startDate) / (1000 * 60 * 60 * 24) + 1;
    const dailyAverage = {
      value: formatCurrency(billData.cost_total / daysInPeriod),
      subtitle: `${(billData.kwh_total / daysInPeriod).toFixed(2)} kWh/day`,
      change: `${daysInPeriod}-day period`,
    };

    const carbonFootprint = {
      value: `${(billData.kwh_total * 0.82).toFixed(1)} kg CO₂`,
      subtitle: "CO₂ emissions for this period",
      change: `~${Math.round((billData.kwh_total * 0.82) / 22)} trees`,
    };

    let quickInsights = [];
    if (billData.user_appliances && billData.user_appliances.length > 0) {
      const topAppliance = billData.user_appliances.reduce(
        (max, app) =>
          app.estimates[0]?.estimated_cost > max.estimates[0]?.estimated_cost
            ? app
            : max,
        billData.user_appliances[0]
      );
      quickInsights.push({
        type: "warning",
        icon: AlertCircle,
        title: "Primary Consumer",
        description: `${topAppliance.custom_name} is your highest usage device this month.`,
        action: "View Appliances",
      });
    }
    if (billData.parse_status === "success") {
      quickInsights.push({
        type: "success",
        icon: CheckCircle2,
        title: "Bill Processed",
        description: `Successfully analyzed your bill for ${new Date(
          billData.billing_period_start
        ).toLocaleString("default", { month: "long" })}.`,
        action: "See Report",
      });
    }
    const applianceCount = billData.user_appliances?.length || 0;
    quickInsights.push({
      type: "info",
      icon: Target,
      title: `${applianceCount} Appliances Surveyed`,
      description: `Your insights are based on the ${applianceCount} appliances you've added for this bill.`,
      action: "Manage Appliances",
    });

    const metricsData = {
      totalBill,
      highestConsumer,
      dailyAverage,
      carbonFootprint,
      quickInsights: quickInsights.slice(0, 3),
    };

    const COLORS = ["#3b82f6", "#10b981", "#f97316", "#ef4444", "#8b5cf6"];
    const billBreakdownData =
      billData.normalized_json?.charges_breakdown?.map((item, index) => ({
        name: item.name,
        value: item.amount,
        color: COLORS[index % COLORS.length],
      })) || [];
    const applianceConsumptionData =
      billData.user_appliances
        ?.map((app) => ({
          name: app.custom_name,
          consumption: app.estimates[0]?.estimated_kwh || 0,
        }))
        .sort((a, b) => b.consumption - a.consumption) || [];
    const efficiencyData =
      billData.user_appliances?.map((app) => ({
        name: app.custom_name,
        wattage: app.custom_wattage,
        consumption: app.estimates[0]?.estimated_kwh || 0,
      })) || [];
    const ageVsConsumptionData =
      billData.user_appliances?.map((app) => ({
        name: app.custom_name,
        year: app.purchase_year,
        consumption: app.estimates[0]?.estimated_kwh || 0,
      })) || [];
    const chartsData = {
      billBreakdownData,
      applianceConsumptionData,
      efficiencyData,
      ageVsConsumptionData,
    };

    return { metrics: metricsData, chartsData };
  }, [billData]);

  const renderMetricCards = () => {
    if (isLoading) {
      return [...Array(4)].map((_, i) => (
        <div
          key={i}
          className="h-44 bg-gray-200 rounded-xl animate-pulse"
        ></div>
      ));
    }
    if (isError) {
      return (
        <div className="md:col-span-2 lg:col-span-4 text-center text-red-500">
          Failed to load bill data.
        </div>
      );
    }
    if (!selectedBill) {
      return (
        <div className="md:col-span-2 lg:col-span-4 text-center p-10 bg-gray-50 rounded-lg">
          <FileText className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-700">Select a Bill</h3>
          <p className="text-gray-500">
            Choose a billing period above to see your overview.
          </p>
        </div>
      );
    }
    if (metrics) {
      return (
        <>
          <MetricCard
            title={metrics.totalBill.title}
            value={metrics.totalBill.value}
            change={metrics.totalBill.change}
            changeType="neutral"
            subtitle={metrics.totalBill.subtitle}
            icon={DollarSign}
          />
          <MetricCard
            title="Highest Consumer"
            value={metrics.highestConsumer.value}
            change={metrics.highestConsumer.change}
            changeType="increase"
            subtitle={metrics.highestConsumer.subtitle}
            icon={BarChart3}
          />
          <MetricCard
            title="Daily Average"
            value={metrics.dailyAverage.value}
            change={metrics.dailyAverage.change}
            changeType="neutral"
            subtitle={metrics.dailyAverage.subtitle}
            icon={Activity}
          />
          <MetricCard
            title="Carbon Footprint"
            value={metrics.carbonFootprint.value}
            change={metrics.carbonFootprint.change}
            changeType="decrease"
            subtitle={metrics.carbonFootprint.subtitle}
            icon={Leaf}
          />
        </>
      );
    }
    return null;
  };
  const renderQuickInsights = () => {
    if (isLoading || isError || !metrics?.quickInsights) {
      return [...Array(3)].map((_, i) => (
        <Card
          key={i}
          className="h-28 bg-gray-200 animate-pulse border-none"
        ></Card>
      ));
    }
    return metrics.quickInsights.map((insight, index) => (
      <InsightCard key={index} {...insight} />
    ));
  };

  const renderCharts = () => {
    if (isLoading) {
      return [...Array(4)].map((_, i) => (
        <div
          key={i}
          className="h-96 bg-gray-200 rounded-xl animate-pulse"
        ></div>
      ));
    }
    if (isError || !metrics) {
      return null; // Don't show charts if there's an error or no data
    }

    const {
      billBreakdownData,
      applianceConsumptionData,
      efficiencyData,
      ageVsConsumptionData,
    } = chartsData;

    return (
      <>
        <ChartCard
          title="Bill Cost Breakdown"
          description="Distribution of charges for the selected month"
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={billBreakdownData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={110}
                paddingAngle={3}
                dataKey="value"
                nameKey="name"
              >
                {billBreakdownData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`₹${value.toFixed(2)}`, "Amount"]}
              />
              <Legend iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Appliance Consumption (kWh)"
          description="Energy usage per appliance for this bill"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={applianceConsumptionData}
              margin={{ top: 20, right: 20, left: -10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 12 }} />
              <YAxis tick={{ fill: "#64748b", fontSize: 12 }} />
              <Tooltip
                formatter={(value) => [
                  `${value.toFixed(2)} kWh`,
                  "Consumption",
                ]}
              />
              <Bar dataKey="consumption" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Appliance Efficiency Matrix"
          description="Consumption (kWh) vs. Power (Wattage)"
        >
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart
              margin={{ top: 20, right: 20, bottom: 20, left: -10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                type="number"
                dataKey="wattage"
                name="Power"
                unit="W"
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <YAxis
                type="number"
                dataKey="consumption"
                name="Consumption"
                unit="kWh"
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <ZAxis dataKey="name" name="Appliance" />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} />
              <Scatter name="Appliances" data={efficiencyData} fill="#10b981" />
            </ScatterChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Appliance Age vs. Consumption"
          description="Does older equipment use more energy?"
        >
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart
              margin={{ top: 20, right: 20, bottom: 20, left: -10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                type="number"
                dataKey="year"
                name="Purchase Year"
                tick={{ fill: "#64748b", fontSize: 12 }}
                domain={["dataMin - 1", "dataMax + 1"]}
              />
              <YAxis
                type="number"
                dataKey="consumption"
                name="Consumption"
                unit="kWh"
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <ZAxis dataKey="name" name="Appliance" />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} />
              <Scatter
                name="Appliances"
                data={ageVsConsumptionData}
                fill="#f97316"
              />
            </ScatterChart>
          </ResponsiveContainer>
        </ChartCard>
      </>
    );
  };

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
        </div>
        <div className="mb-4 ">
          <BillSelector
            selectedBill={selectedBill}
            onBillChange={setSelectedBill}
          />
        </div>
        {/* Quick Insights Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {renderQuickInsights()}
        </div>
      </div>

      {/* Enhanced Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        {renderMetricCards()}
      </div>

      {/* Enhanced Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        {renderCharts()}
      </div>

      {/* Enhanced Quick Actions & Recommendations */}
      <Card className="bg-white/80 backdrop-blur-sm border-gray-200 hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-xl font-semibold text-gray-900">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Zap className="w-5 h-5 text-primary-600" />
            </div>
            Quick Actions
          </CardTitle>
          <CardDescription>
            AI-powered recommendations to optimize your energy consumption
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gradient-subtle rounded-lg border border-primary-100">
              <h4 className="font-medium text-gray-900 mb-2">
                Update Appliance Usage
              </h4>
              <p className="text-sm text-gray-600 mb-3">
                Your Appliance usage seems higher this month
              </p>
              <Link to="appliances">
                <Button
                  size="sm"
                  className="bg-primary-500 hover:bg-primary-600"
                >
                  Review Appliances
                </Button>
              </Link>
            </div>
            <div className="p-4 bg-gradient-subtle rounded-lg border border-primary-100">
              <h4 className="font-medium text-gray-900 mb-2">
                Potential Savings
              </h4>
              <p className="text-sm text-gray-600 mb-3">
                You could save upto ₹300/month with these tips
              </p>
              <Link to="insights">
                <Button
                  size="sm"
                  className="bg-primary-500 hover:bg-primary-600"
                >
                  View Insights
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Overview;
