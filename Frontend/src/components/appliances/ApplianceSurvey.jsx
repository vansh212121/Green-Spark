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
import { Plus, Trash2, Home } from "lucide-react";
import {
  useGetApplianceCatalogQuery,
  useCreateApplianceMutation,
} from "@/features/api/applianceApi"; // RTK query
import { toast } from "sonner";

const STAR_RATINGS = [
  "1 Star",
  "2 Star",
  "3 Star",
  "4 Star",
  "5 Star",
  "Don't Know",
];

export const ApplianceSurvey = ({
  billId,
  onClose,
  applianceToEdit = null,
}) => {
  const mapApplianceToForm = (appl) => ({
    id: appl.id || appl.appliance_id || Date.now().toString(), // local key
    appliance_id: appl.id || appl.appliance_id || null, // this is for API
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

  const [appliances, setAppliances] = useState(
    applianceToEdit
      ? [mapApplianceToForm(applianceToEdit)]
      : [
          {
            id: "1",
            type: "",
            customName: "",
            brand: "",
            model: "",
            starRating: "",
            wattage: "",
            hoursPerDay: "",
            daysPerWeek: "7",
            count: "1",
            purchaseYear: new Date().getFullYear().toString(),
            notes: "",
          },
        ]
  );

  // Fetch catalog
  const { data: catalogData, isLoading } = useGetApplianceCatalogQuery();
  const catalogOptions =
    catalogData?.map((item) => ({
      value: item.category_id,
      label: item.label,
      icon: item.icon_emoji,
      typicalWattage: item.typical_wattage,
    })) || [];

  // Create mutation
  const [createAppliance, { isLoading: isCreating }] =
    useCreateApplianceMutation();

  const addAppliance = () => {
    setAppliances([
      ...appliances,
      {
        id: Date.now().toString(),
        type: "",
        customName: "",
        brand: "",
        model: "",
        starRating: "",
        wattage: "",
        hoursPerDay: "",
        daysPerWeek: "7",
        count: "1",
        purchaseYear: new Date().getFullYear().toString(),
        notes: "",
      },
    ]);
  };

  const removeAppliance = (id) => {
    setAppliances(appliances.filter((a) => a.id !== id));
  };

  const updateAppliance = (id, field, value) => {
    setAppliances(
      appliances.map((a) => (a.id === id ? { ...a, [field]: value } : a))
    );
  };

  const handleSave = async () => {
    const validAppliances = appliances.filter((a) => a.type);

    // Map frontend data to API request format
    const payloads = validAppliances.map((a) => ({
      appliance_catalog_id: a.type,
      custom_name:
        a.customName || catalogOptions.find((c) => c.value === a.type)?.label,
      count: Number(a.count) || 1,
      custom_wattage:
        Number(a.wattage) ||
        catalogOptions.find((c) => c.value === a.type)?.typicalWattage ||
        0,
      hours_per_day: Number(a.hoursPerDay) || 0,
      days_per_week: Number(a.daysPerWeek) || 7,
      brand: a.brand || null,
      model: a.model || null,
      star_rating: a.starRating ? Number(a.starRating[0]) : null,
      purchase_year: a.purchaseYear
        ? Number(a.purchaseYear)
        : new Date().getFullYear(),
      notes: a.notes || null,
    }));

    try {
      for (const payload of payloads) {
        await createAppliance({ billId, body: payload }).unwrap();
        toast.success("✅ Appliances saved successfully!");
      }
      onClose();
    } catch (err) {
      const message =
        err?.data?.error?.message ||
        err?.data?.message ||
        err?.error ||
        "❌ Failed to save appliances. Please try again.";

      toast.error(message);
      console.error("Error creating appliances:", err);
    }
  };
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-auto bg-card animate-scale-in">
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Home className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-foreground">
                  Appliance Survey
                </h2>
                <p className="text-sm text-muted-foreground">
                  Add your home appliances to get accurate energy analysis
                </p>
              </div>
            </div>
            <Button variant="ghost" onClick={onClose}>
              ✕
            </Button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {appliances.map((appliance, index) => (
            <Card
              key={appliance.id}
              className="p-6 bg-muted/30 animate-fade-in"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-foreground">
                  Appliance {index + 1}
                </h3>
                {appliances.length > 1 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeAppliance(appliance.id)}
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Appliance Type */}
                <div className="space-y-2">
                  <Label>Appliance Type</Label>
                  <Select
                    value={appliance.type}
                    onValueChange={(v) =>
                      updateAppliance(appliance.id, "type", v)
                    }
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
                    value={appliance.customName}
                    onChange={(e) =>
                      updateAppliance(
                        appliance.id,
                        "customName",
                        e.target.value
                      )
                    }
                    placeholder="e.g., Living Room AC"
                  />
                </div>

                {/* Brand */}
                <div className="space-y-2">
                  <Label>Brand (Optional)</Label>
                  <Input
                    value={appliance.brand}
                    onChange={(e) =>
                      updateAppliance(appliance.id, "brand", e.target.value)
                    }
                  />
                </div>

                {/* Model */}
                <div className="space-y-2">
                  <Label>Model (Optional)</Label>
                  <Input
                    value={appliance.model}
                    onChange={(e) =>
                      updateAppliance(appliance.id, "model", e.target.value)
                    }
                  />
                </div>

                {/* Star Rating */}
                <div className="space-y-2">
                  <Label>Star Rating</Label>
                  <Select
                    value={appliance.starRating}
                    onValueChange={(v) =>
                      updateAppliance(appliance.id, "starRating", v)
                    }
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
                    value={appliance.wattage}
                    onChange={(e) =>
                      updateAppliance(appliance.id, "wattage", e.target.value)
                    }
                    placeholder="e.g., 1500"
                  />
                </div>

                {/* Hours per Day */}
                <div className="space-y-2">
                  <Label>Hours per Day</Label>
                  <Input
                    type="number"
                    max="24"
                    value={appliance.hoursPerDay}
                    onChange={(e) =>
                      updateAppliance(
                        appliance.id,
                        "hoursPerDay",
                        e.target.value
                      )
                    }
                    placeholder="e.g., 8"
                  />
                </div>

                {/* Days per Week */}
                <div className="space-y-2">
                  <Label>Days per Week</Label>
                  <Input
                    type="number"
                    max="7"
                    value={appliance.daysPerWeek}
                    onChange={(e) =>
                      updateAppliance(
                        appliance.id,
                        "daysPerWeek",
                        e.target.value
                      )
                    }
                    placeholder="e.g., 7"
                  />
                </div>

                {/* Count */}
                <div className="space-y-2">
                  <Label>Quantity</Label>
                  <Input
                    type="number"
                    min="1"
                    value={appliance.count}
                    onChange={(e) =>
                      updateAppliance(appliance.id, "count", e.target.value)
                    }
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
                    value={appliance.purchaseYear}
                    onChange={(e) =>
                      updateAppliance(
                        appliance.id,
                        "purchaseYear",
                        e.target.value
                      )
                    }
                  />
                </div>

                {/* Notes */}
                <div className="space-y-2 md:col-span-2 lg:col-span-3">
                  <Label>Additional Notes (Optional)</Label>
                  <Input
                    value={appliance.notes}
                    onChange={(e) =>
                      updateAppliance(appliance.id, "notes", e.target.value)
                    }
                    placeholder="Any additional information..."
                  />
                </div>
              </div>
            </Card>
          ))}

          <Button
            variant="outline"
            onClick={addAppliance}
            className="w-full border-dashed border-2 hover:bg-primary/5 hover:border-primary"
          >
            <Plus className="w-4 h-4 mr-2" /> Add Another Appliance
          </Button>
        </div>

        <div className="p-6 border-t border-border flex justify-between">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            className="bg-primary hover:bg-primary/90"
            disabled={isCreating}
          >
            {isCreating ? "Saving..." : "Save Appliances"}
          </Button>
        </div>
      </Card>
    </div>
  );
};
