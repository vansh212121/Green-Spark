import { useState } from "react";
import { ApplianceSurvey } from "@/components/ApplianceSurvey";
import { ApplianceEstimates } from "@/components/ApplianceEstimates";
import { BillSelector } from "@/components/BillSelector";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Zap,
  Settings,
  TrendingUp,
  AlertTriangle,
  Calculator,
  BarChart3,
  Plus,
} from "lucide-react";

const appliances = [
  {
    name: "Air Conditioner",
    type: "Cooling",
    icon: "❄️",
    consumption: "189 kWh",
    cost: "₹1,032",
    efficiency: "4 Star",
    hours: "8 hours/day",
  },
  {
    name: "Refrigerator",
    type: "Kitchen",
    icon: "🧊",
    consumption: "81 kWh",
    cost: "₹442",
    efficiency: "3 Star",
    hours: "24 hours/day",
  },
  {
    name: "Water Heater",
    type: "Bathroom",
    icon: "🚿",
    consumption: "68 kWh",
    cost: "₹368",
    efficiency: "4 Star",
    hours: "2 hours/day",
  },
  {
    name: "Washing Machine",
    type: "Laundry",
    icon: "🔄",
    consumption: "35 kWh",
    cost: "₹190",
    efficiency: "5 Star",
    hours: "1 hour/day",
  },
  {
    name: "Television",
    type: "Entertainment",
    icon: "📺",
    consumption: "28 kWh",
    cost: "₹152",
    efficiency: "4 Star",
    hours: "6 hours/day",
  },
  {
    name: "Lighting",
    type: "General",
    icon: "💡",
    consumption: "49 kWh",
    cost: "₹267",
    efficiency: "LED",
    hours: "8 hours/day",
  },
];

const Appliances = () => {
  const [showSurvey, setShowSurvey] = useState(false);
  const [hasSurveyData, setHasSurveyData] = useState(true); // Set to false to show empty state
  const [selectedBill, setSelectedBill] = useState("jan-2025");
  const [showEstimates, setShowEstimates] = useState(true);

  const handleSaveAppliances = (appliances) => {
    console.log("Saved appliances:", appliances);
    setHasSurveyData(true);
    setShowSurvey(false);
  };

  return (
    <div className="p-8 animate-fade-in">
      <header className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-semibold text-gray-900 mb-2">
              Appliance Insights
            </h1>
            <p className="text-gray-600">
              Track and optimize your appliance energy consumption
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              onClick={() => setShowEstimates(true)}
              variant={showEstimates ? "default" : "outline"}
              className={
                showEstimates ? "bg-primary-500 hover:bg-primary-600" : ""
              }
            >
              <Calculator className="w-4 h-4 mr-2" />
              Generate Estimates
            </Button>
            <Button onClick={() => setShowSurvey(true)} variant="outline">
              <Settings className="w-4 h-4 mr-2" />
              Update Survey
            </Button>
          </div>
        </div>

        <BillSelector
          selectedBill={selectedBill}
          onBillChange={setSelectedBill}
        />
      </header>

      {hasSurveyData ? (
        <div className="space-y-8">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center">
                  <Zap className="w-5 h-5 mr-2 text-primary-500" />
                  Total Consumption
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  450 kWh
                </div>
                <p className="text-sm text-gray-600">This month</p>
                <Badge variant="secondary" className="mt-2">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  +12% vs last month
                </Badge>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 text-warning-500" />
                  Highest Consumer
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  Air Conditioner
                </div>
                <p className="text-sm text-gray-600">189 kWh (42%)</p>
                <Badge variant="destructive" className="mt-2">
                  High Usage
                </Badge>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-success-500" />
                  Efficiency Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  7.2/10
                </div>
                <p className="text-sm text-gray-600">Good performance</p>
                <Badge variant="secondary" className="mt-2">
                  Room for improvement
                </Badge>
              </CardContent>
            </Card>
          </div>

          {/* Estimates Section */}
          {showEstimates && (
            <>
              <Separator />
              <ApplianceEstimates selectedBill={selectedBill} />
              <Separator />
            </>
          )}

          {/* Appliance List */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-gray-900">
                Your Appliances
              </h2>
              <Button variant="outline" size="sm">
                <BarChart3 className="w-4 h-4 mr-2" />
                View All Analytics
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {appliances.map((appliance, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">
                        {appliance.name}
                      </CardTitle>
                      <div className="text-2xl">{appliance.icon}</div>
                    </div>
                    <CardDescription>
                      {appliance.type} • {appliance.efficiency} efficiency
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">
                          Monthly Usage:
                        </span>
                        <span className="font-mono font-medium">
                          {appliance.consumption}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">
                          Monthly Cost:
                        </span>
                        <span className="font-mono font-medium">
                          {appliance.cost}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">
                          Usage Pattern:
                        </span>
                        <span className="text-sm">{appliance.hours}</span>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="w-full mt-4">
                      View Details
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      ) : (
        // Empty State - No Survey Data
        <div className="text-center py-16">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Zap className="w-8 h-8 text-primary-600" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Complete Your Appliance Survey
          </h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Help us understand your appliances to provide accurate insights and
            personalized recommendations for energy savings.
          </p>
          <Button
            onClick={() => setShowSurvey(true)}
            className="bg-primary-500 hover:bg-primary-600"
          >
            <Plus className="w-4 h-4 mr-2" />
            Start Appliance Survey
          </Button>
        </div>
      )}

      {showSurvey && (
        <ApplianceSurvey
          onClose={() => setShowSurvey(false)}
          onSave={handleSaveAppliances}
        />
      )}
    </div>
  );
};

export default Appliances;
