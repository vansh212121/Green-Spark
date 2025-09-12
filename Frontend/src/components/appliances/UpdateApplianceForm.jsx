import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Home } from "lucide-react";
import {
  useUpdateApplianceMutation,
  useGetApplianceCatalogQuery,
} from "@/features/api/applianceApi";
import { toast } from "sonner";

const STAR_RATINGS = [
  "1 Star",
  "2 Star",
  "3 Star",
  "4 Star",
  "5 Star",
  "Don't Know",
];

export const UpdateApplianceForm = ({ billId, applianceToEdit, onClose }) => {
  const { data: catalogData, isLoading } = useGetApplianceCatalogQuery();
  const catalogOptions =
    catalogData?.map((item) => ({
      value: item.category_id,
      label: item.label,
      icon: item.icon_emoji,
      typicalWattage: item.typical_wattage,
    })) || [];

  const mapApplianceToForm = (appl) => ({
    type: appl.appliance_catalog_id || "",
    customName: appl.custom_name || "",
    brand: appl.brand || "",
    model: appl.model || "",
    starRating: appl.star_rating ? `${appl.star_rating} Star` : "",
    wattage: appl.custom_wattage?.toString() || "",
    hoursPerDay: appl.hours_per_day?.toString() || "",
    daysPerWeek: appl.days_per_week?.toString() || "7",
    count: appl.count?.toString() || "1",
    purchaseYear:
      appl.purchase_year?.toString() || new Date().getFullYear().toString(),
    notes: appl.notes || "",
  });

  const [formState, setFormState] = useState(
    mapApplianceToForm(applianceToEdit)
  );
  const [updateApplianceApi, { isLoading: isUpdating }] =
    useUpdateApplianceMutation();

  const handleChange = (field, value) => {
    setFormState({ ...formState, [field]: value });
  };

  const handleUpdate = async () => {
    const payload = {
      appliance_catalog_id: formState.type,
      custom_name:
        formState.customName ||
        catalogOptions.find((c) => c.value === formState.type)?.label,
      count: Number(formState.count) || 1,
      custom_wattage:
        Number(formState.wattage) ||
        catalogOptions.find((c) => c.value === formState.type)
          ?.typicalWattage ||
        0,
      hours_per_day: Number(formState.hoursPerDay) || 0,
      days_per_week: Number(formState.daysPerWeek) || 7,
      brand: formState.brand || null,
      model: formState.model || null,
      star_rating: formState.starRating
        ? Number(formState.starRating[0])
        : null,
      purchase_year: formState.purchaseYear
        ? Number(formState.purchaseYear)
        : new Date().getFullYear(),
      notes: formState.notes || null,
    };

    try {
      await updateApplianceApi({
        billId,
        applianceId: applianceToEdit.id,
        body: payload,
      }).unwrap();
      toast.success(`✅ "${payload.custom_name}" updated successfully!`);
      onClose();
    } catch (err) {
      const message =
        err?.data?.error?.message ||
        err?.data?.message ||
        err?.error ||
        "❌ Failed to update appliance";
      toast.error(message);
      console.error("Update appliance error:", err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-auto bg-card animate-scale-in">
        {/* Header */}
        <div className="p-6 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <Home className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-foreground">
                Update Appliance
              </h2>
              <p className="text-sm text-muted-foreground">
                Edit appliance details for accurate energy analysis
              </p>
            </div>
          </div>
          <Button variant="ghost" onClick={onClose}>
            ✕
          </Button>
        </div>

        {/* Form */}
        <div className="p-6 space-y-6">
          <Card className="p-6 bg-muted/30 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Appliance Type */}
              <div className="space-y-2">
                <Label>Appliance Type</Label>
                <Select
                  value={formState.type}
                  onValueChange={(v) => handleChange("type", v)}
                >
                  <SelectTrigger>
                    <SelectValue
                      placeholder={
                        isLoading ? "Loading..." : "Select appliance"
                      }
                    />
                  </SelectTrigger>
                  <SelectContent>
                    {catalogOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        <span className="flex items-center gap-2">
                          <span>{option.icon}</span>
                          {option.label}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Custom Name */}
              <div className="space-y-2">
                <Label>Custom Name (Optional)</Label>
                <Input
                  value={formState.customName}
                  onChange={(e) => handleChange("customName", e.target.value)}
                  placeholder="e.g., Living Room AC"
                />
              </div>

              {/* Brand */}
              <div className="space-y-2">
                <Label>Brand (Optional)</Label>
                <Input
                  value={formState.brand}
                  onChange={(e) => handleChange("brand", e.target.value)}
                />
              </div>

              {/* Model */}
              <div className="space-y-2">
                <Label>Model (Optional)</Label>
                <Input
                  value={formState.model}
                  onChange={(e) => handleChange("model", e.target.value)}
                />
              </div>

              {/* Star Rating */}
              <div className="space-y-2">
                <Label>Star Rating</Label>
                <Select
                  value={formState.starRating}
                  onValueChange={(v) => handleChange("starRating", v)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select rating" />
                  </SelectTrigger>
                  <SelectContent>
                    {STAR_RATINGS.map((r) => (
                      <SelectItem key={r} value={r}>
                        {r}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Power */}
              <div className="space-y-2">
                <Label>Power (Watts)</Label>
                <Input
                  type="number"
                  value={formState.wattage}
                  onChange={(e) => handleChange("wattage", e.target.value)}
                  placeholder="e.g., 1500"
                />
              </div>

              {/* Hours per Day */}
              <div className="space-y-2">
                <Label>Hours per Day</Label>
                <Input
                  type="number"
                  max="24"
                  value={formState.hoursPerDay}
                  onChange={(e) => handleChange("hoursPerDay", e.target.value)}
                  placeholder="e.g., 8"
                />
              </div>

              {/* Days per Week */}
              <div className="space-y-2">
                <Label>Days per Week</Label>
                <Input
                  type="number"
                  max="7"
                  value={formState.daysPerWeek}
                  onChange={(e) => handleChange("daysPerWeek", e.target.value)}
                  placeholder="e.g., 7"
                />
              </div>

              {/* Quantity */}
              <div className="space-y-2">
                <Label>Quantity</Label>
                <Input
                  type="number"
                  min="1"
                  value={formState.count}
                  onChange={(e) => handleChange("count", e.target.value)}
                  placeholder="e.g., 2"
                />
              </div>

              {/* Purchase Year */}
              <div className="space-y-2">
                <Label>Purchase Year</Label>
                <Input
                  type="number"
                  min="1990"
                  max={new Date().getFullYear()}
                  value={formState.purchaseYear}
                  onChange={(e) => handleChange("purchaseYear", e.target.value)}
                />
              </div>

              {/* Notes */}
              <div className="space-y-2 md:col-span-2 lg:col-span-3">
                <Label>Additional Notes (Optional)</Label>
                <Input
                  value={formState.notes}
                  onChange={(e) => handleChange("notes", e.target.value)}
                  placeholder="Any additional information..."
                />
              </div>
            </div>
          </Card>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-border flex justify-between">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleUpdate}
            className="bg-primary hover:bg-primary/90"
            disabled={isUpdating}
          >
            {isUpdating ? "Updating..." : "Update Appliance"}
          </Button>
        </div>
      </Card>
    </div>
  );
};
