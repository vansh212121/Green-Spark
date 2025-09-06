import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FileText } from "lucide-react";

const bills = [
  {
    id: "jan-2025",
    month: "January 2025",
    amount: "₹2,456",
    units: "450 kWh",
    date: "2 days ago",
  },
  {
    id: "dec-2024",
    month: "December 2024",
    amount: "₹2,190",
    units: "380 kWh",
    date: "1 month ago",
  },
  {
    id: "nov-2024",
    month: "November 2024",
    amount: "₹1,890",
    units: "320 kWh",
    date: "2 months ago",
  },
  {
    id: "oct-2024",
    month: "October 2024",
    amount: "₹2,190",
    units: "380 kWh",
    date: "3 months ago",
  },
  {
    id: "sep-2024",
    month: "September 2024",
    amount: "₹2,010",
    units: "350 kWh",
    date: "4 months ago",
  },
  {
    id: "aug-2024",
    month: "August 2024",
    amount: "₹1,890",
    units: "320 kWh",
    date: "5 months ago",
  },
];

export const BillSelector = ({ selectedBill, onBillChange }) => {
  const getSelectedBillData = () => {
    if (!selectedBill) return bills[0];
    return bills.find((bill) => bill.id === selectedBill) || bills[0];
  };

  const selectedData = getSelectedBillData();

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <FileText className="w-4 h-4" />
        <span>Showing data for:</span>
      </div>

      <Select value={selectedBill || bills[0].id} onValueChange={onBillChange}>
        <SelectTrigger className="w-64">
          <SelectValue>
            <div className="flex items-center justify-between w-full">
              <span>{selectedData.month}</span>
              <span className="text-primary-600 font-mono">
                {selectedData.amount}
              </span>
            </div>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {bills.map((bill) => (
            <SelectItem key={bill.id} value={bill.id}>
              <div className="flex items-center justify-between w-full min-w-0">
                <div className="flex flex-col">
                  <span className="font-medium">{bill.month}</span>
                  <span className="text-xs text-gray-500">
                    {bill.units} • {bill.date}
                  </span>
                </div>
                <span className="ml-4 font-mono text-primary-600">
                  {bill.amount}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
