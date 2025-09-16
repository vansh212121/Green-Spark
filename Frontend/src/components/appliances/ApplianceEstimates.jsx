import React, { useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Zap, TrendingUp, Calculator, AlertCircle } from "lucide-react";

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
} from "recharts";
import { useGetEstimatesForBillQuery } from "@/features/api/applianceApi";
import { ChartCard } from "../ChartCard";

// --- Presentational Sub-components ---
const MetricCard = ({ title, value, subtitle, icon: Icon, iconColor }) => (
  <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <div className="flex items-center justify-between mb-4">
      <h3 className="font-medium text-gray-600">{title}</h3>
      <Icon className={`w-5 h-5 ${iconColor}`} />
    </div>
    <div className="text-2xl font-semibold text-gray-900 mb-1">{value}</div>
    <p className="text-sm text-gray-500">{subtitle}</p>
  </div>
);

const MetricCardSkeleton = () => (
  <div className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse">
    <div className="flex items-center justify-between mb-4">
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="w-5 h-5 bg-gray-200 rounded-full"></div>
    </div>
    <div className="h-7 bg-gray-300 rounded w-1/3 mb-1"></div>
    <div className="h-3 bg-gray-200 rounded w-3/4"></div>
  </div>
);

const ChartSkeleton = () => (
  <div className="h-80 bg-gray-200 rounded-xl animate-pulse"></div>
);

export const ApplianceEstimates = ({ selectedBill, appliances }) => {
  // Hooks are called at the top, before any conditional returns.
  const {
    data: estimates,
    isLoading,
    isError,
  } = useGetEstimatesForBillQuery(selectedBill, {
    skip: !selectedBill,
  });

  const getApplianceName = (user_appliance_id) => {
    const appliance = appliances.find((a) => a.id === user_appliance_id);
    return appliance ? appliance.custom_name : "Unknown";
  };

  const { metrics, chartData } = useMemo(() => {
    if (
      !estimates ||
      estimates.length === 0 ||
      !appliances ||
      appliances.length === 0
    ) {
      return { metrics: null, chartData: null };
    }

    const totalKwh = estimates.reduce((sum, est) => sum + est.estimated_kwh, 0);
    const totalCost = estimates.reduce(
      (sum, est) => sum + est.estimated_cost,
      0
    );
    const blendedRate = totalKwh > 0 ? totalCost / totalKwh : 0;
    const metrics = {
      totalKwh: `${totalKwh.toFixed(1)} kWh`,
      totalCost: new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
      }).format(totalCost),
      blendedRate: `₹${blendedRate.toFixed(2)} / kWh`,
      count: estimates.length,
    };

    const applianceConsumptionData = estimates
      .map((est) => ({
        name: getApplianceName(est.user_appliance_id),
        consumption: parseFloat(est.estimated_kwh.toFixed(1)),
      }))
      .sort((a, b) => a.consumption - b.consumption);

    let highEff = 0,
      medEff = 0,
      lowEff = 0;
    appliances.forEach((app) => {
      if (app.star_rating >= 4) highEff++;
      else if (app.star_rating === 3) medEff++;
      else lowEff++;
    });
    const efficiencyData = [
      { name: "High (4-5 Stars)", value: highEff, color: "#22c55e" },
      { name: "Medium (3 Stars)", value: medEff, color: "#f59e0b" },
      { name: "Low (1-2 Stars)", value: lowEff, color: "#ef4444" },
    ].filter((d) => d.value > 0);

    const chartData = { applianceConsumptionData, efficiencyData };

    return { metrics, chartData };
  }, [estimates, appliances]);

  const renderMetrics = () => {
    if (isLoading) {
      return [...Array(3)].map((_, i) => <MetricCardSkeleton key={i} />);
    }
    if (isError || !metrics) {
      return (
        <div className="md:col-span-3 text-center p-6 bg-gray-50 rounded-lg">
          <AlertCircle className="mx-auto w-8 h-8 text-gray-400 mb-2" />
          <p className="text-gray-600">No estimates available for this bill.</p>
        </div>
      );
    }
    return (
      <>
        <MetricCard
          title="Total Estimated Consumption"
          value={metrics.totalKwh}
          subtitle={`From ${metrics.count} surveyed appliances`}
          icon={Zap}
          iconColor="text-primary-500"
        />
        <MetricCard
          title="Total Estimated Cost"
          value={metrics.totalCost}
          subtitle="For the surveyed devices"
          icon={TrendingUp}
          iconColor="text-green-500"
        />
        <MetricCard
          title="Blended Appliance Rate"
          value={metrics.blendedRate}
          subtitle="Average cost of energy used"
          icon={Calculator}
          iconColor="text-amber-500"
        />
      </>
    );
  };

  const renderCharts = () => {
    if (isLoading) {
      return (
        <>
          <ChartSkeleton />
          <ChartSkeleton />
        </>
      );
    }
    if (isError || !chartData) {
      return null;
    }
    return (
      <>
        <ChartCard title="Appliance Consumption Breakdown">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData.applianceConsumptionData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 12 }}
                width={80}
                interval={0}
              />
              <Tooltip
                cursor={{ fill: "#fafafa" }}
                formatter={(value) => [`${value} kWh`, "Consumption"]}
              />
              <Bar dataKey="consumption" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Efficiency Distribution">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData.efficiencyData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                nameKey="name"
                labelLine={false}
                label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
              >
                {chartData.efficiencyData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value, name) => [value, name]} />
              <Legend iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </>
    );
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <MetricCardSkeleton />
      </div>
    );
  }
  if (isError || !estimates) {
    return (
      <p className="text-gray-500 p-6">No estimates available for this bill.</p>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Appliance Estimates
          </h2>
          <p className="text-gray-600">
            Based on your appliance survey for the selected bill.
          </p>
        </div>
        <Button className="bg-primary-500 hover:bg-primary-600">
          <Calculator className="w-4 h-4 mr-2" />
          Recalculate Estimates
        </Button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {renderMetrics()}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {renderCharts()}
      </div>
      {/* Detailed Appliance List */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">
            Appliance Estimates
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Estimated energy consumption and cost for each appliance
          </p>
        </div>
        <div className="divide-y divide-gray-200">
          {estimates.map((applianceEstimate, index) => (
            <div key={index} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Zap className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {getApplianceName(applianceEstimate.user_appliance_id)}
                    </h4>
                    <p className="text-sm text-gray-500">Estimated usage</p>
                  </div>
                </div>
                <div className="flex items-center space-x-8 text-right">
                  <div>
                    <p className="font-mono font-semibold text-gray-900">
                      {applianceEstimate.estimated_kwh.toFixed(2)} kWh
                    </p>
                    <p className="text-sm text-gray-500">Estimated kWh</p>
                  </div>
                  <div>
                    <p className="font-mono font-semibold text-gray-900">
                      ₹{applianceEstimate.estimated_cost.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-500">Estimated Cost</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
