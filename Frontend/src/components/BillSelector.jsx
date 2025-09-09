// import {
//   Select,
//   SelectContent,
//   SelectItem,
//   SelectTrigger,
//   SelectValue,
// } from "@/components/ui/select";
// import { FileText } from "lucide-react";

// const bills = [
//   {
//     id: "jan-2025",
//     month: "January 2025",
//     amount: "₹2,456",
//     units: "450 kWh",
//     date: "2 days ago",
//   },
//   {
//     id: "dec-2024",
//     month: "December 2024",
//     amount: "₹2,190",
//     units: "380 kWh",
//     date: "1 month ago",
//   },
//   {
//     id: "nov-2024",
//     month: "November 2024",
//     amount: "₹1,890",
//     units: "320 kWh",
//     date: "2 months ago",
//   },
//   {
//     id: "oct-2024",
//     month: "October 2024",
//     amount: "₹2,190",
//     units: "380 kWh",
//     date: "3 months ago",
//   },
//   {
//     id: "sep-2024",
//     month: "September 2024",
//     amount: "₹2,010",
//     units: "350 kWh",
//     date: "4 months ago",
//   },
//   {
//     id: "aug-2024",
//     month: "August 2024",
//     amount: "₹1,890",
//     units: "320 kWh",
//     date: "5 months ago",
//   },
// ];

// export const BillSelector = ({ selectedBill, onBillChange }) => {
//   const getSelectedBillData = () => {
//     if (!selectedBill) return bills[0];
//     return bills.find((bill) => bill.id === selectedBill) || bills[0];
//   };

//   const selectedData = getSelectedBillData();

//   return (
//     <div className="flex items-center gap-4">
//       <div className="flex items-center gap-2 text-sm text-gray-600">
//         <FileText className="w-4 h-4" />
//         <span>Showing data for:</span>
//       </div>

//       <Select value={selectedBill || bills[0].id} onValueChange={onBillChange}>
//         <SelectTrigger className="w-64">
//           <SelectValue>
//             <div className="flex items-center justify-between w-full">
//               <span>{selectedData.month}</span>
//               <span className="text-primary-600 font-mono">
//                 {selectedData.amount}
//               </span>
//             </div>
//           </SelectValue>
//         </SelectTrigger>
//         <SelectContent>
//           {bills.map((bill) => (
//             <SelectItem key={bill.id} value={bill.id}>
//               <div className="flex items-center justify-between w-full min-w-0">
//                 <div className="flex flex-col">
//                   <span className="font-medium">{bill.month}</span>
//                   <span className="text-xs text-gray-500">
//                     {bill.units} • {bill.date}
//                   </span>
//                 </div>
//                 <span className="ml-4 font-mono text-primary-600">
//                   {bill.amount}
//                 </span>
//               </div>
//             </SelectItem>
//           ))}
//         </SelectContent>
//       </Select>
//     </div>
//   );
// };

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FileText, Zap } from "lucide-react";

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

        <Select
          value={selectedBill || bills[0].id}
          onValueChange={onBillChange}
        >
          <SelectTrigger className="w-72 h-12 border-gray-200 hover:border-blue-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all duration-200">
            <SelectValue>
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
            </SelectValue>
          </SelectTrigger>
          <SelectContent className="w-72">
            {bills.map((bill, index) => (
              <SelectItem
                key={bill.id}
                value={bill.id}
                className="p-4 hover:bg-blue-50 focus:bg-blue-50 cursor-pointer"
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
