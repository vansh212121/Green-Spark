import { ChartCard } from "@/components/ChartCard";
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
  Area,
  AreaChart,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Zap, TrendingUp, Calculator } from "lucide-react";
import { useGetEstimatesForBillQuery } from "@/features/api/applianceApi";

const applianceData = [
  { appliance: "AC", consumption: 189, cost: 1032, efficiency: 85 },
  { appliance: "Refrigerator", consumption: 81, cost: 442, efficiency: 78 },
  { appliance: "Water Heater", consumption: 68, cost: 368, efficiency: 82 },
  { appliance: "Washing Machine", consumption: 35, cost: 190, efficiency: 88 },
  { appliance: "TV", consumption: 28, cost: 152, efficiency: 92 },
  { appliance: "Lighting", consumption: 49, cost: 267, efficiency: 95 },
];

const monthlyEstimates = [
  { month: "Jan", estimated: 420, actual: 450, savings: 30 },
  { month: "Feb", estimated: 380, actual: 395, savings: 15 },
  { month: "Mar", estimated: 410, actual: 425, savings: 15 },
  { month: "Apr", estimated: 480, actual: 465, savings: -15 },
  { month: "May", estimated: 520, actual: 535, savings: 15 },
  { month: "Jun", estimated: 550, actual: 525, savings: -25 },
];

const efficiencyData = [
  { name: "High Efficiency", value: 35, color: "#22c55e" },
  { name: "Medium Efficiency", value: 45, color: "#f59e0b" },
  { name: "Low Efficiency", value: 20, color: "#ef4444" },
];

const COLORS = ["#22c55e", "#f59e0b", "#ef4444"];

export const ApplianceEstimates = ({ selectedBill, appliances }) => {
  const { data, isLoading, isError } =
    useGetEstimatesForBillQuery(selectedBill);

  if (isLoading)
    return <p className="text-gray-500 p-6">Loading appliance estimates...</p>;
  if (isError || !data?.length)
    return (
      <p className="text-gray-500 p-6">No estimates available for this bill.</p>
    );

  const estimates = data;

  // Helper to get appliance name from the list
  const getApplianceName = (user_appliance_id) => {
    const appliance = appliances.find((a) => a.id === user_appliance_id);
    return appliance ? appliance.custom_name : "Unknown Appliance";
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Appliance Estimates
          </h2>
          <p className="text-gray-600">
            Based on {selectedBill || "January 2025"} bill data and your
            appliance survey
          </p>
        </div>
        <Button className="bg-primary-500 hover:bg-primary-600">
          <Calculator className="w-4 h-4 mr-2" />
          Recalculate Estimates
        </Button>
      </div>

      {/* Accuracy Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-gray-600">Estimation Accuracy</h3>
            <Zap className="w-5 h-5 text-primary-500" />
          </div>
          <div className="text-2xl font-semibold text-gray-900 mb-1">94%</div>
          <p className="text-sm text-gray-500">Within 6% of actual usage</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-gray-600">Potential Savings</h3>
            <TrendingUp className="w-5 h-5 text-success-400" />
          </div>
          <div className="text-2xl font-semibold text-gray-900 mb-1">₹380</div>
          <p className="text-sm text-gray-500">Per month with optimization</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-gray-600">Average Efficiency</h3>
            <Calculator className="w-5 h-5 text-warning-500" />
          </div>
          <div className="text-2xl font-semibold text-gray-900 mb-1">83%</div>
          <p className="text-sm text-gray-500">Room for improvement</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ChartCard title="Appliance Consumption Breakdown">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={applianceData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis type="number" axisLine={false} tickLine={false} />
              <YAxis
                type="category"
                dataKey="appliance"
                axisLine={false}
                tickLine={false}
                width={80}
              />
              <Bar dataKey="consumption" fill="#22c55e" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Efficiency Distribution">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={efficiencyData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
              >
                {efficiencyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Estimated vs Actual Usage">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={monthlyEstimates}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="month" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Line
                type="monotone"
                dataKey="estimated"
                stroke="#3b82f6"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Estimated"
              />
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#22c55e"
                strokeWidth={3}
                name="Actual"
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Monthly Savings Potential">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthlyEstimates}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="month" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Area
                type="monotone"
                dataKey="savings"
                stroke="#f59e0b"
                fill="#fef3c7"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
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
