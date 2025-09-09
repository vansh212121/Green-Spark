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
  IndianRupee,
  Timer,
  Eye,
  Activity,
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

  const getStatusColor = (status) => {
    switch (status) {
      case "high":
        return "bg-red-50 text-red-700 border-red-200";
      case "normal":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "low":
        return "bg-green-50 text-green-700 border-green-200";
      default:
        return "bg-gray-50 text-gray-700 border-gray-200";
    }
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
            <Card className=" shadow-sm bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center text-blue-900">
                  <div className="p-2 bg-blue-200 rounded-lg mr-3">
                    <Zap className="w-5 h-5 text-blue-700" />
                  </div>
                  Total Consumption
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="text-3xl font-bold text-blue-900">
                    450 kWh
                  </div>
                  <p className="text-blue-700 text-sm">This month</p>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">
                      +12% vs last month
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className=" shadow-sm bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center text-red-900">
                  <div className="p-2 bg-red-200 rounded-lg mr-3">
                    <AlertTriangle className="w-5 h-5 text-red-700" />
                  </div>
                  Highest Consumer
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="text-2xl font-bold text-red-900">
                    Air Conditioner
                  </div>
                  <p className="text-red-700 text-sm">189 kWh (42%)</p>
                  <Badge className="bg-red-200 text-red-800 hover:bg-red-200">
                    High Usage
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card className=" shadow-sm bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center text-green-900">
                  <div className="p-2 bg-green-200 rounded-lg mr-3">
                    <Activity className="w-5 h-5 text-green-700" />
                  </div>
                  Efficiency Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="text-3xl font-bold text-green-900">
                    7.2/10
                  </div>
                  <p className="text-green-700 text-sm">Good performance</p>
                  <Badge className="bg-green-200 text-green-800 hover:bg-green-200">
                    Room for improvement
                  </Badge>
                </div>
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
          <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Your Appliances
                </h2>
                <p className="text-gray-600 mt-1">
                  Detailed breakdown of energy consumption by device
                </p>
              </div>
              <Button
                variant="outline"
                className="border-blue-200 text-blue-600 hover:bg-blue-50"
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                View All Analytics
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {appliances.map((appliance, index) => (
                <Card
                  key={index}
                  className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-blue-200"
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">{appliance.icon}</div>
                        <div>
                          <CardTitle className="text-lg text-gray-900">
                            {appliance.name}
                          </CardTitle>
                          <CardDescription className="flex items-center gap-2">
                            {appliance.type} • {appliance.efficiency}
                          </CardDescription>
                        </div>
                      </div>
                      <Badge
                        variant="secondary"
                        className={`${getStatusColor(appliance.status)} border`}
                      >
                        {appliance.percentage}%
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <Zap className="w-3 h-3" />
                          <span>Monthly Usage</span>
                        </div>
                        <div className="font-mono font-semibold text-gray-900">
                          {appliance.consumption}
                        </div>
                      </div>

                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <IndianRupee className="w-3 h-3" />
                          <span>Monthly Cost</span>
                        </div>
                        <div className="font-mono font-semibold text-blue-600">
                          {appliance.cost}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Timer className="w-3 h-3" />
                        <span>Usage Pattern</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        {appliance.hours}
                      </div>
                    </div>

                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-4 border-blue-200 text-blue-600 hover:bg-blue-50"
                    >
                      <Eye className="w-4 h-4 mr-2" />
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
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
          <div className="text-center py-20 px-8">
            <div className="w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Zap className="w-10 h-10 text-blue-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Complete Your Appliance Survey
            </h2>
            <p className="text-gray-600 mb-8 max-w-lg mx-auto text-lg">
              Help us understand your appliances to provide accurate insights
              and personalized recommendations for energy savings.
            </p>
            <Button
              onClick={() => setShowSurvey(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3"
            >
              <Plus className="w-5 h-5 mr-2" />
              Start Appliance Survey
            </Button>
          </div>
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

// import { useState } from "react";
// import { ApplianceSurvey } from "@/components/ApplianceSurvey";
// import { ApplianceEstimates } from "@/components/ApplianceEstimates";
// import { BillSelector } from "@/components/BillSelector";
// import { Button } from "@/components/ui/button";
// import {
//   Card,
//   CardContent,
//   CardDescription,
//   CardHeader,
//   CardTitle,
// } from "@/components/ui/card";
// import { Badge } from "@/components/ui/badge";
// import { Separator } from "@/components/ui/separator";
// import {
//   Zap,
//   Settings,
//   TrendingUp,
//   TrendingDown,
//   AlertTriangle,
//   Calculator,
//   BarChart3,
//   Plus,
//   Eye,
//   Activity,
//   Timer,
//   IndianRupee,
// } from "lucide-react";

// const appliances = [
//   {
//     name: "Air Conditioner",
//     type: "Cooling",
//     icon: "❄️",
//     consumption: "189 kWh",
//     cost: "₹1,032",
//     efficiency: "4 Star",
//     hours: "8 hours/day",
//     percentage: 42,
//     status: "high",
//   },
//   {
//     name: "Refrigerator",
//     type: "Kitchen",
//     icon: "🧊",
//     consumption: "81 kWh",
//     cost: "₹442",
//     efficiency: "3 Star",
//     hours: "24 hours/day",
//     percentage: 18,
//     status: "normal",
//   },
//   {
//     name: "Water Heater",
//     type: "Bathroom",
//     icon: "🚿",
//     consumption: "68 kWh",
//     cost: "₹368",
//     efficiency: "4 Star",
//     hours: "2 hours/day",
//     percentage: 15,
//     status: "normal",
//   },
//   {
//     name: "Washing Machine",
//     type: "Laundry",
//     icon: "🔄",
//     consumption: "35 kWh",
//     cost: "₹190",
//     efficiency: "5 Star",
//     hours: "1 hour/day",
//     percentage: 8,
//     status: "low",
//   },
//   {
//     name: "Television",
//     type: "Entertainment",
//     icon: "📺",
//     consumption: "28 kWh",
//     cost: "₹152",
//     efficiency: "4 Star",
//     hours: "6 hours/day",
//     percentage: 6,
//     status: "low",
//   },
//   {
//     name: "Lighting",
//     type: "General",
//     icon: "💡",
//     consumption: "49 kWh",
//     cost: "₹267",
//     efficiency: "LED",
//     hours: "8 hours/day",
//     percentage: 11,
//     status: "normal",
//   },
// ];

// const Appliances = () => {
//   const [showSurvey, setShowSurvey] = useState(false);
//   const [hasSurveyData, setHasSurveyData] = useState(true);
//   const [selectedBill, setSelectedBill] = useState("jan-2025");
//   const [showEstimates, setShowEstimates] = useState(true);

//   const handleSaveAppliances = (appliances) => {
//     console.log("Saved appliances:", appliances);
//     setHasSurveyData(true);
//     setShowSurvey(false);
//   };

// const getStatusColor = (status) => {
//   switch (status) {
//     case "high":
//       return "bg-red-50 text-red-700 border-red-200";
//     case "normal":
//       return "bg-blue-50 text-blue-700 border-blue-200";
//     case "low":
//       return "bg-green-50 text-green-700 border-green-200";
//     default:
//       return "bg-gray-50 text-gray-700 border-gray-200";
//   }
// };

//   return (
//     <div className="min-h-screen bg-gray-50">
//       <div className="max-w-7xl mx-auto p-6 space-y-8">
//         {/* Header Section */}
//         <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
//           <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
//             <div className="space-y-2">
//               <div className="flex items-center gap-3">
//                 <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-xl">
//                   <Zap className="w-6 h-6 text-blue-600" />
//                 </div>
//                 <div>
//                   <h1 className="text-3xl font-bold text-gray-900">
//                     Appliance Insights
//                   </h1>
//                   <p className="text-gray-600">
//                     Track and optimize your appliance energy consumption
//                   </p>
//                 </div>
//               </div>
//             </div>

//             <div className="flex flex-wrap gap-3">
//               <Button
//                 onClick={() => setShowEstimates(!showEstimates)}
//                 variant={showEstimates ? "default" : "outline"}
//                 className={`${
//                   showEstimates
//                     ? "bg-blue-600 hover:bg-blue-700 text-white"
//                     : "border-blue-200 text-blue-600 hover:bg-blue-50"
//                 }`}
//               >
//                 <Calculator className="w-4 h-4 mr-2" />
//                 Generate Estimates
//               </Button>
//               <Button
//                 onClick={() => setShowSurvey(true)}
//                 variant="outline"
//                 className="border-gray-200 hover:bg-gray-50"
//               >
//                 <Settings className="w-4 h-4 mr-2" />
//                 Update Survey
//               </Button>
//             </div>
//           </div>

//           <div className="mt-8">
//             <BillSelector
//               selectedBill={selectedBill}
//               onBillChange={setSelectedBill}
//             />
//           </div>
//         </div>

//         {hasSurveyData ? (
//           <div className="space-y-8">
//             {/* Quick Stats */}
// <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//   <Card className="border-0 shadow-sm bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
//     <CardHeader className="pb-4">
//       <CardTitle className="text-lg flex items-center text-blue-900">
//         <div className="p-2 bg-blue-200 rounded-lg mr-3">
//           <Zap className="w-5 h-5 text-blue-700" />
//         </div>
//         Total Consumption
//       </CardTitle>
//     </CardHeader>
//     <CardContent>
//       <div className="space-y-3">
//         <div className="text-3xl font-bold text-blue-900">
//           450 kWh
//         </div>
//         <p className="text-blue-700 text-sm">This month</p>
//         <div className="flex items-center gap-2">
//           <TrendingUp className="w-4 h-4 text-green-600" />
//           <span className="text-sm text-green-600 font-medium">
//             +12% vs last month
//           </span>
//         </div>
//       </div>
//     </CardContent>
//   </Card>

//   <Card className="border-0 shadow-sm bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
//     <CardHeader className="pb-4">
//       <CardTitle className="text-lg flex items-center text-red-900">
//         <div className="p-2 bg-red-200 rounded-lg mr-3">
//           <AlertTriangle className="w-5 h-5 text-red-700" />
//         </div>
//         Highest Consumer
//       </CardTitle>
//     </CardHeader>
//     <CardContent>
//       <div className="space-y-3">
//         <div className="text-2xl font-bold text-red-900">
//           Air Conditioner
//         </div>
//         <p className="text-red-700 text-sm">189 kWh (42%)</p>
//         <Badge className="bg-red-200 text-red-800 hover:bg-red-200">
//           High Usage
//         </Badge>
//       </div>
//     </CardContent>
//   </Card>

//   <Card className="border-0 shadow-sm bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
//     <CardHeader className="pb-4">
//       <CardTitle className="text-lg flex items-center text-green-900">
//         <div className="p-2 bg-green-200 rounded-lg mr-3">
//           <Activity className="w-5 h-5 text-green-700" />
//         </div>
//         Efficiency Score
//       </CardTitle>
//     </CardHeader>
//     <CardContent>
//       <div className="space-y-3">
//         <div className="text-3xl font-bold text-green-900">
//           7.2/10
//         </div>
//         <p className="text-green-700 text-sm">Good performance</p>
//         <Badge className="bg-green-200 text-green-800 hover:bg-green-200">
//           Room for improvement
//         </Badge>
//       </div>
//     </CardContent>
//   </Card>
// </div>

//             {/* Estimates Section */}
//             {showEstimates && (
//               <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
//                 <ApplianceEstimates selectedBill={selectedBill} />
//               </div>
//             )}

//             {/* Appliance List */}
//     <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
//       <div className="flex items-center justify-between mb-8">
//         <div>
//           <h2 className="text-2xl font-bold text-gray-900">
//             Your Appliances
//           </h2>
//           <p className="text-gray-600 mt-1">
//             Detailed breakdown of energy consumption by device
//           </p>
//         </div>
//         <Button
//           variant="outline"
//           className="border-blue-200 text-blue-600 hover:bg-blue-50"
//         >
//           <BarChart3 className="w-4 h-4 mr-2" />
//           View All Analytics
//         </Button>
//       </div>

//       <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
//         {appliances.map((appliance, index) => (
//           <Card
//             key={index}
//             className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-blue-200"
//           >
//             <CardHeader className="pb-4">
//               <div className="flex items-center justify-between">
//                 <div className="flex items-center gap-3">
//                   <div className="text-3xl">{appliance.icon}</div>
//                   <div>
//                     <CardTitle className="text-lg text-gray-900">
//                       {appliance.name}
//                     </CardTitle>
//                     <CardDescription className="flex items-center gap-2">
//                       {appliance.type} • {appliance.efficiency}
//                     </CardDescription>
//                   </div>
//                 </div>
//                 <Badge
//                   variant="secondary"
//                   className={`${getStatusColor(
//                     appliance.status
//                   )} border`}
//                 >
//                   {appliance.percentage}%
//                 </Badge>
//               </div>
//             </CardHeader>

//             <CardContent className="space-y-4">
//               <div className="grid grid-cols-2 gap-4">
//                 <div className="space-y-1">
//                   <div className="flex items-center gap-2 text-xs text-gray-500">
//                     <Zap className="w-3 h-3" />
//                     <span>Monthly Usage</span>
//                   </div>
//                   <div className="font-mono font-semibold text-gray-900">
//                     {appliance.consumption}
//                   </div>
//                 </div>

//                 <div className="space-y-1">
//                   <div className="flex items-center gap-2 text-xs text-gray-500">
//                     <IndianRupee className="w-3 h-3" />
//                     <span>Monthly Cost</span>
//                   </div>
//                   <div className="font-mono font-semibold text-blue-600">
//                     {appliance.cost}
//                   </div>
//                 </div>
//               </div>

//               <div className="space-y-1">
//                 <div className="flex items-center gap-2 text-xs text-gray-500">
//                   <Timer className="w-3 h-3" />
//                   <span>Usage Pattern</span>
//                 </div>
//                 <div className="text-sm text-gray-700">
//                   {appliance.hours}
//                 </div>
//               </div>

//               <Button
//                 variant="outline"
//                 size="sm"
//                 className="w-full mt-4 border-blue-200 text-blue-600 hover:bg-blue-50"
//               >
//                 <Eye className="w-4 h-4 mr-2" />
//                 View Details
//               </Button>
//             </CardContent>
//           </Card>
//         ))}
//       </div>
//     </div>
//   </div>
// ) : (
//   // Empty State - No Survey Data
//   <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
//     <div className="text-center py-20 px-8">
//       <div className="w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
//         <Zap className="w-10 h-10 text-blue-600" />
//       </div>
//       <h2 className="text-3xl font-bold text-gray-900 mb-4">
//         Complete Your Appliance Survey
//       </h2>
//       <p className="text-gray-600 mb-8 max-w-lg mx-auto text-lg">
//         Help us understand your appliances to provide accurate insights
//         and personalized recommendations for energy savings.
//       </p>
//       <Button
//         onClick={() => setShowSurvey(true)}
//         className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3"
//       >
//         <Plus className="w-5 h-5 mr-2" />
//         Start Appliance Survey
//       </Button>
//     </div>
//   </div>
//         )}

//         {showSurvey && (
//           <ApplianceSurvey
//             onClose={() => setShowSurvey(false)}
//             onSave={handleSaveAppliances}
//           />
//         )}
//       </div>
//     </div>
//   );
// };

// export default Appliances;
