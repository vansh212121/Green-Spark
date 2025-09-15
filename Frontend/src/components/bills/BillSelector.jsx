import React, { useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FileText, Zap } from "lucide-react";
import { useGetMyBillsQuery } from "@/features/api/billApi";

export const BillSelector = ({ selectedBill, onBillChange }) => {
  // 1. Fetch the transformed and formatted list of bills directly in this component.
  const { data: billsData, isLoading } = useGetMyBillsQuery();
  const bills = billsData?.results || [];

  useEffect(() => {
    if (bills.length > 0 && !selectedBill) {
      onBillChange(bills[0].id); // ✅ runs only once now
    }
  }, [bills, selectedBill, onBillChange]);

  const getSelectedBillData = () => {
    if (!selectedBill && bills.length > 0) return bills[0];
    return bills.find((bill) => bill.id === selectedBill) || null;
  };
  const selectedData = getSelectedBillData();

  if (isLoading || bills.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-50 rounded-lg">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-900">
                Electricity Bill
              </h3>
              <p className="text-xs text-gray-500">Select billing period</p>
            </div>
          </div>
          <Select disabled>
            <SelectTrigger className="w-72 h-12">
              <SelectValue
                placeholder={
                  isLoading ? "Loading bills..." : "No bills available"
                }
              />
            </SelectTrigger>
          </Select>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-blue-50 rounded-lg">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-900">
              Electricity Bill
            </h3>
            <p className="text-xs text-gray-500">Select billing period</p>
          </div>
        </div>

        <Select value={selectedBill} onValueChange={onBillChange}>
          <SelectTrigger className="w-72 h-12 border-gray-200 hover:border-blue-300">
            <SelectValue>
              {selectedData && (
                <div className="flex items-center justify-between w-full">
                  <div className="flex flex-col items-start">
                    <span className="font-medium text-gray-900">
                      {selectedData.month}
                    </span>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Zap className="w-3 h-3" />
                      <span>{selectedData.units}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-semibold ml-8 text-lg text-blue-600 font-mono">
                      {selectedData.amount}
                    </span>
                  </div>
                </div>
              )}
            </SelectValue>
          </SelectTrigger>
          <SelectContent className="w-72">
            {bills.map((bill, index) => (
              <SelectItem
                key={bill.id}
                value={bill.id}
                className="p-4 cursor-pointer"
              >
                <div className="flex items-center justify-between w-full">
                  <div className="flex flex-col items-start">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">
                        {bill.month}
                      </span>
                      {index === 0 && (
                        <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                          Latest
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Zap className="w-3 h-3" />
                        <span>{bill.units}</span>
                      </div>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-500">{bill.date}</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <span className="font-semibold text-blue-600 font-mono">
                      {bill.amount}
                    </span>
                  </div>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
