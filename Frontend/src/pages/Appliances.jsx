import { useState } from "react";
import { ApplianceSurvey } from "@/components/appliances/ApplianceSurvey";
import { ApplianceEstimates } from "@/components/appliances/ApplianceEstimates";
import { BillSelector } from "@/components/bills/BillSelector";
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
  Edit2,
  Trash2,
} from "lucide-react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";
import {
  useDeleteApplianceMutation,
  useGetAppliancesForBillQuery,
} from "@/features/api/applianceApi";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { UpdateApplianceForm } from "@/components/appliances/UpdateApplianceForm";
import { toast } from "sonner";
import { useTriggerBillEstimationMutation } from "@/features/api/billApi";

const Appliances = () => {
  const [showSurvey, setShowSurvey] = useState(false);
  const [hasSurveyData, setHasSurveyData] = useState(true);
  const [selectedBill, setSelectedBill] = useState(null);
  const [showEstimates, setShowEstimates] = useState(true);
  const [selectedAppliance, setSelectedAppliance] = useState(null);
  const [editingAppliance, setEditingAppliance] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [applianceToDelete, setApplianceToDelete] = useState(null);

  const [deleteApplianceApi, { isLoading: isDeleting }] =
    useDeleteApplianceMutation();

  const handleSaveAppliances = (appliances) => {
    setHasSurveyData(true);
    setShowSurvey(false);
  };
  const handleDeleteApplianceConfirm = async () => {
    if (!applianceToDelete) return;

    try {
      await deleteApplianceApi({
        billId: selectedBill,
        applianceId: applianceToDelete.id,
      }).unwrap();

      toast.success(
        `✅ "${applianceToDelete.custom_name}" deleted successfully!`
      );
      setShowDeleteModal(false);
      setApplianceToDelete(null);

      // Optional: Refetch appliances or invalidate cache if using RTK Query tags
    } catch (err) {
      const message =
        err?.data?.error?.message ||
        err?.data?.message ||
        err?.error ||
        "❌ Failed to delete appliance. Please try again.";

      toast.error(message);
      console.error("Error deleting appliance:", err);
    }
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

  const {
    data: appliancesData,
    isLoading,
    isError,
  } = useGetAppliancesForBillQuery(selectedBill, { skip: !selectedBill });

  const [triggerEstimation, { isLoading: isEstimating }] =
    useTriggerBillEstimationMutation();

  const handleGenerateEstimates = async () => {
    if (!selectedBill) {
      toast.error("Please select a bill first.");
      return;
    }

    try {
      await triggerEstimation(selectedBill).unwrap();
      toast.success("✅ Appliance estimation has been queued.");
      setShowEstimates(true); // show estimates after triggering
    } catch (err) {
      const message =
        err?.data?.error?.message ||
        err?.data?.message ||
        err?.error ||
        "❌ Failed to queue estimation.";
      toast.error(message);
      console.error("Error triggering estimation:", err);
    }
  };

  const appliances = appliancesData?.items || [];
  const handleEditAppliance = (appliance) => {
    setEditingAppliance(appliance); // store the appliance being edited
    setShowSurvey(true); // open modal
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
              onClick={handleGenerateEstimates}
              variant={showEstimates ? "default" : "outline"}
              className={
                showEstimates ? "bg-primary-500 hover:bg-primary-600" : ""
              }
              disabled={isEstimating}
            >
              <Calculator className="w-4 h-4 mr-2" />
              {isEstimating ? "Generating..." : "Generate Estimates"}
            </Button>
            <Button onClick={() => setShowSurvey(true)} variant="outline">
              <Settings className="w-4 h-4 mr-2" />
              Add Appliances
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
              <ApplianceEstimates
                selectedBill={selectedBill}
                appliances={appliancesData?.items || []}
              />
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
            </div>

            {isLoading ? (
              <p className="text-gray-500">Loading appliances...</p>
            ) : isError ? (
              <p className="text-red-500">Failed to load appliances.</p>
            ) : appliances.length === 0 ? (
              <p className="text-gray-500">
                No appliances found for this bill.
              </p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {appliances.map((appliance, index) => (
                  <Card
                    key={index}
                    className="hover:shadow-lg transition-all duration-300 border border-gray-200 hover:border-blue-200"
                  >
                    <CardHeader className="pb-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="text-3xl">{"🔌"}</div>
                          <div>
                            <CardTitle className="text-lg text-gray-900">
                              {appliance.custom_name}
                            </CardTitle>
                            <CardDescription className="flex items-center gap-2">
                              {appliance.brand} • {appliance.star_rating}★
                            </CardDescription>
                          </div>
                        </div>

                        {/* Edit & Delete Buttons */}
                        <div className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditAppliance(appliance)}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-destructive hover:bg-destructive/10"
                            onClick={() => {
                              setApplianceToDelete(appliance);
                              setShowDeleteModal(true);
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <Zap className="w-3 h-3" />
                            <span>Wattage</span>
                          </div>
                          <div className="font-mono font-semibold text-gray-900">
                            {appliance.custom_wattage} W
                          </div>
                        </div>

                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <Timer className="w-3 h-3" />
                            <span>Usage</span>
                          </div>
                          <div className="text-sm text-gray-700">
                            {appliance.hours_per_day}h/day •{" "}
                            {appliance.days_per_week}d/week
                          </div>
                        </div>
                      </div>

                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full mt-4 border-blue-200 text-blue-600 hover:bg-blue-50"
                        onClick={() => setSelectedAppliance(appliance)}
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        View Details
                      </Button>
                    </CardContent>
                  </Card>
                ))}

                {/* Appliance Details Modal */}
                <Dialog
                  open={!!selectedAppliance}
                  onOpenChange={() => setSelectedAppliance(null)}
                >
                  <DialogContent className="max-w-lg bg-white rounded-2xl shadow-lg p-6 animate-fade-in">
                    <DialogHeader className="border-b border-gray-200 pb-4 mb-4">
                      <DialogTitle className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <Zap className="w-5 h-5 text-blue-600" />
                        {selectedAppliance?.custom_name}
                      </DialogTitle>
                      <DialogDescription className="text-sm text-gray-500">
                        Detailed information about this appliance
                      </DialogDescription>
                    </DialogHeader>

                    {selectedAppliance && (
                      <div className="space-y-4 text-gray-700 text-sm">
                        <div className="grid grid-cols-2 gap-4">
                          <p>
                            <strong>Brand:</strong> {selectedAppliance.brand}
                          </p>
                          <p>
                            <strong>Model:</strong> {selectedAppliance.model}
                          </p>
                          <p>
                            <strong>Star Rating:</strong>{" "}
                            {selectedAppliance.star_rating}★
                          </p>
                          <p>
                            <strong>Wattage:</strong>{" "}
                            {selectedAppliance.custom_wattage} W
                          </p>
                          <p>
                            <strong>Usage:</strong>{" "}
                            {selectedAppliance.hours_per_day}h/day •{" "}
                            {selectedAppliance.days_per_week}d/week
                          </p>
                          <p>
                            <strong>Purchase Year:</strong>{" "}
                            {selectedAppliance.purchase_year}
                          </p>
                          {selectedAppliance.notes && (
                            <p className="col-span-2">
                              <strong>Notes:</strong> {selectedAppliance.notes}
                            </p>
                          )}
                        </div>

                        <Button
                          variant="outline"
                          onClick={() => setSelectedAppliance(null)}
                          className="mt-4 w-full border-blue-200 text-blue-600 hover:bg-blue-50"
                        >
                          Close
                        </Button>
                      </div>
                    )}
                  </DialogContent>
                </Dialog>
              </div>
            )}
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
      {showSurvey &&
        (editingAppliance ? (
          <UpdateApplianceForm
            billId={selectedBill}
            applianceToEdit={editingAppliance}
            onClose={() => {
              setShowSurvey(false);
              setEditingAppliance(null);
            }}
            onUpdated={() => {
              setShowSurvey(false);
              setEditingAppliance(null);
              // Optionally refetch appliances
            }}
          />
        ) : (
          <ApplianceSurvey
            billId={selectedBill}
            onClose={() => setShowSurvey(false)}
            onSave={handleSaveAppliances}
          />
        ))}
      {/* Delete Modal */}
      <AlertDialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Appliance</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to permanently delete this appliance? This
              will:
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Remove this appliance from your bill</li>
                <li>Delete all details associated with this appliance</li>
              </ul>
              <p className="mt-3 text-sm font-semibold text-red-600">
                This action cannot be undone.
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-600 hover:bg-red-700"
              onClick={handleDeleteApplianceConfirm}
            >
              Delete Appliance
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Appliances;
