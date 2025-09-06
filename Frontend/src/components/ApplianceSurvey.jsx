import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select"
import { Card } from "@/components/ui/card"
import { Plus, Trash2, Home } from "lucide-react"

const APPLIANCE_OPTIONS = [
  { value: "air_conditioner", label: "Air Conditioner", icon: "❄️" },
  { value: "refrigerator", label: "Refrigerator", icon: "🧊" },
  { value: "water_heater", label: "Water Heater/Geyser", icon: "🚿" },
  { value: "washing_machine", label: "Washing Machine", icon: "👕" },
  { value: "microwave", label: "Microwave", icon: "📱" },
  { value: "television", label: "Television", icon: "📺" },
  { value: "fan", label: "Ceiling/Table Fan", icon: "🌀" },
  { value: "lighting", label: "LED/CFL Bulbs", icon: "💡" },
  { value: "laptop", label: "Laptop/Computer", icon: "💻" },
  { value: "iron", label: "Iron", icon: "🔥" },
  { value: "dishwasher", label: "Dishwasher", icon: "🍽️" },
  { value: "other", label: "Other", icon: "⚡" }
]

const STAR_RATINGS = [
  "1 Star",
  "2 Star",
  "3 Star",
  "4 Star",
  "5 Star",
  "Don't Know"
]

export const ApplianceSurvey = ({ onClose, onSave }) => {
  const [appliances, setAppliances] = useState([
    {
      id: "1",
      type: "",
      brand: "",
      model: "",
      starRating: "",
      wattage: "",
      hoursPerDay: "",
      daysPerWeek: "7",
      notes: ""
    }
  ])

  const addAppliance = () => {
    setAppliances([
      ...appliances,
      {
        id: Date.now().toString(),
        type: "",
        brand: "",
        model: "",
        starRating: "",
        wattage: "",
        hoursPerDay: "",
        daysPerWeek: "7",
        notes: ""
      }
    ])
  }

  const removeAppliance = id => {
    setAppliances(appliances.filter(appliance => appliance.id !== id))
  }

  const updateAppliance = (id, field, value) => {
    setAppliances(
      appliances.map(appliance =>
        appliance.id === id ? { ...appliance, [field]: value } : appliance
      )
    )
  }

  const handleSave = () => {
    const validAppliances = appliances.filter(appliance => appliance.type)
    onSave(validAppliances)
    onClose()
  }

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
                <div className="space-y-2">
                  <Label htmlFor={`type-${appliance.id}`}>Appliance Type</Label>
                  <Select
                    value={appliance.type}
                    onValueChange={value =>
                      updateAppliance(appliance.id, "type", value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select appliance" />
                    </SelectTrigger>
                    <SelectContent>
                      {APPLIANCE_OPTIONS.map(option => (
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

                <div className="space-y-2">
                  <Label htmlFor={`brand-${appliance.id}`}>
                    Brand (Optional)
                  </Label>
                  <Input
                    id={`brand-${appliance.id}`}
                    value={appliance.brand}
                    onChange={e =>
                      updateAppliance(appliance.id, "brand", e.target.value)
                    }
                    placeholder="e.g., LG, Samsung"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`model-${appliance.id}`}>
                    Model (Optional)
                  </Label>
                  <Input
                    id={`model-${appliance.id}`}
                    value={appliance.model}
                    onChange={e =>
                      updateAppliance(appliance.id, "model", e.target.value)
                    }
                    placeholder="e.g., 1.5 Ton, 200L"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`star-${appliance.id}`}>Star Rating</Label>
                  <Select
                    value={appliance.starRating}
                    onValueChange={value =>
                      updateAppliance(appliance.id, "starRating", value)
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select rating" />
                    </SelectTrigger>
                    <SelectContent>
                      {STAR_RATINGS.map(rating => (
                        <SelectItem key={rating} value={rating}>
                          {rating}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`wattage-${appliance.id}`}>
                    Power (Watts)
                  </Label>
                  <Input
                    id={`wattage-${appliance.id}`}
                    type="number"
                    value={appliance.wattage}
                    onChange={e =>
                      updateAppliance(appliance.id, "wattage", e.target.value)
                    }
                    placeholder="e.g., 1500"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor={`hours-${appliance.id}`}>Hours/Day</Label>
                  <Input
                    id={`hours-${appliance.id}`}
                    type="number"
                    max="24"
                    value={appliance.hoursPerDay}
                    onChange={e =>
                      updateAppliance(
                        appliance.id,
                        "hoursPerDay",
                        e.target.value
                      )
                    }
                    placeholder="e.g., 8"
                  />
                </div>

                <div className="space-y-2 md:col-span-2 lg:col-span-3">
                  <Label htmlFor={`notes-${appliance.id}`}>
                    Additional Notes (Optional)
                  </Label>
                  <Input
                    id={`notes-${appliance.id}`}
                    value={appliance.notes}
                    onChange={e =>
                      updateAppliance(appliance.id, "notes", e.target.value)
                    }
                    placeholder="Any additional information about usage patterns..."
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
            <Plus className="w-4 h-4 mr-2" />
            Add Another Appliance
          </Button>
        </div>

        <div className="p-6 border-t border-border flex justify-between">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            className="bg-primary hover:bg-primary/90"
          >
            Save Appliances
          </Button>
        </div>
      </Card>
    </div>
  )
}
