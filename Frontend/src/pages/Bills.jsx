import { useState } from "react";
import { Button } from "@/components/ui/button";
import { BillSelector } from "@/components/BillSelector";
import { Upload, FileText, CheckCircle, Filter } from "lucide-react";

const BillItem = ({
  month,
  amount,
  units,
  status,
  date,
  isSelected,
  onClick,
}) => (
  <div
    className={`flex items-center justify-between p-4 hover:bg-gray-50 cursor-pointer transition-colors border-l-4 ${
      isSelected ? "border-l-primary-500 bg-primary-50" : "border-l-transparent"
    }`}
    onClick={onClick}
  >
    <div className="flex items-center gap-4">
      <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
        <FileText className="w-5 h-5 text-primary-600" />
      </div>
      <div>
        <h4 className="font-medium text-gray-900">{month}</h4>
        <p className="text-sm text-gray-500">{date}</p>
      </div>
    </div>
    <div className="flex items-center gap-6">
      <div className="text-right">
        <p className="font-mono font-semibold text-gray-900">{amount}</p>
        <p className="text-sm text-gray-500">{units}</p>
      </div>
      <div className="flex items-center gap-2">
        <CheckCircle className="w-4 h-4 text-success-400" />
        <span className="text-sm text-success-400 capitalize">{status}</span>
      </div>
    </div>
  </div>
);

const Bills = () => {
  const [selectedBill, setSelectedBill] = useState("jan-2025");

  const bills = [
    {
      id: "jan-2025",
      month: "January 2025",
      amount: "₹2,456",
      units: "450 kWh",
      status: "processed",
      date: "2 days ago",
    },
    {
      id: "dec-2024",
      month: "December 2024",
      amount: "₹2,190",
      units: "380 kWh",
      status: "processed",
      date: "1 month ago",
    },
    {
      id: "nov-2024",
      month: "November 2024",
      amount: "₹1,890",
      units: "320 kWh",
      status: "processed",
      date: "2 months ago",
    },
    {
      id: "oct-2024",
      month: "October 2024",
      amount: "₹2,190",
      units: "380 kWh",
      status: "processed",
      date: "3 months ago",
    },
  ];
  return (
    <div className="p-8 animate-fade-in">
      <header className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-semibold text-gray-900 mb-2">
              Bills & Data
            </h1>
            <p className="text-gray-600">
              Upload your electricity bills or enter data manually
            </p>
          </div>
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter Bills
          </Button>
        </div>

        <BillSelector
          selectedBill={selectedBill}
          onBillChange={setSelectedBill}
        />
      </header>

      {/* Upload Section */}
      <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-8 mb-8 hover:border-primary-400 transition-colors">
        <div className="text-center">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Upload className="w-8 h-8 text-primary-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Upload Your Bill
          </h3>
          <p className="text-gray-600 mb-6">
            Drag and drop your PDF or image file, or click to browse
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button className="bg-primary-500 hover:bg-primary-600">
              <Upload className="w-4 h-4 mr-2" />
              Choose File
            </Button>
            <Button variant="outline">Enter Manually</Button>
          </div>
          <p className="text-sm text-gray-500 mt-4">
            Supports PDF, JPG, PNG files up to 10MB
          </p>
        </div>
      </div>

      {/* Recent Bills */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">Recent Bills</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {bills.map((bill) => (
            <BillItem
              key={bill.id}
              month={bill.month}
              amount={bill.amount}
              units={bill.units}
              status={bill.status}
              date={bill.date}
              isSelected={selectedBill === bill.id}
              onClick={() => setSelectedBill(bill.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Bills;
