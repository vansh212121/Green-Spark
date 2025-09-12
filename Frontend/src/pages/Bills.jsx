// import { useState } from "react";
// import { Button } from "@/components/ui/button";
// import { BillSelector } from "@/components/BillSelector";
// import { Upload, FileText, CheckCircle, Filter } from "lucide-react";

// const BillItem = ({
//   month,
//   amount,
//   units,
//   status,
//   date,
//   isSelected,
//   onClick,
// }) => (
//   <div
//     className={`flex items-center justify-between p-4 hover:bg-gray-50 cursor-pointer transition-colors border-l-4 ${
//       isSelected ? "border-l-primary-500 bg-primary-50" : "border-l-transparent"
//     }`}
//     onClick={onClick}
//   >
//     <div className="flex items-center gap-4">
//       <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
//         <FileText className="w-5 h-5 text-primary-600" />
//       </div>
//       <div>
//         <h4 className="font-medium text-gray-900">{month}</h4>
//         <p className="text-sm text-gray-500">{date}</p>
//       </div>
//     </div>
//     <div className="flex items-center gap-6">
//       <div className="text-right">
//         <p className="font-mono font-semibold text-gray-900">{amount}</p>
//         <p className="text-sm text-gray-500">{units}</p>
//       </div>
//       <div className="flex items-center gap-2">
//         <CheckCircle className="w-4 h-4 text-success-400" />
//         <span className="text-sm text-success-400 capitalize">{status}</span>
//       </div>
//     </div>
//   </div>
// );

// const Bills = () => {
//   const [selectedBill, setSelectedBill] = useState("jan-2025");

//   const bills = [
//     {
//       id: "jan-2025",
//       month: "January 2025",
//       amount: "₹2,456",
//       units: "450 kWh",
//       status: "processed",
//       date: "2 days ago",
//     },
//     {
//       id: "dec-2024",
//       month: "December 2024",
//       amount: "₹2,190",
//       units: "380 kWh",
//       status: "processed",
//       date: "1 month ago",
//     },
//     {
//       id: "nov-2024",
//       month: "November 2024",
//       amount: "₹1,890",
//       units: "320 kWh",
//       status: "processed",
//       date: "2 months ago",
//     },
//     {
//       id: "oct-2024",
//       month: "October 2024",
//       amount: "₹2,190",
//       units: "380 kWh",
//       status: "processed",
//       date: "3 months ago",
//     },
//   ];
//   return (
//     <div className="p-8 animate-fade-in">
//       <header className="mb-8">
//         <div className="flex justify-between items-center mb-4">
//           <div>
//             <h1 className="text-3xl font-semibold text-gray-900 mb-2">
//               Bills & Data
//             </h1>
//             <p className="text-gray-600">
//               Upload your electricity bills or enter data manually
//             </p>
//           </div>
//           <Button variant="outline" size="sm">
//             <Filter className="w-4 h-4 mr-2" />
//             Filter Bills
//           </Button>
//         </div>

//         <BillSelector
//           selectedBill={selectedBill}
//           onBillChange={setSelectedBill}
//         />
//       </header>

//       {/* Upload Section */}
//       <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-8 mb-8 hover:border-primary-400 transition-colors">
//         <div className="text-center">
//           <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
//             <Upload className="w-8 h-8 text-primary-600" />
//           </div>
//           <h3 className="text-xl font-semibold text-gray-900 mb-2">
//             Upload Your Bill
//           </h3>
//           <p className="text-gray-600 mb-6">
//             Drag and drop your PDF or image file, or click to browse
//           </p>
//           <div className="flex flex-col sm:flex-row gap-3 justify-center">
//             <Button className="bg-primary-500 hover:bg-primary-600">
//               <Upload className="w-4 h-4 mr-2" />
//               Choose File
//             </Button>
//             <Button variant="outline">Enter Manually</Button>
//           </div>
//           <p className="text-sm text-gray-500 mt-4">
//             Supports PDF, JPG, PNG files up to 10MB
//           </p>
//         </div>
//       </div>

//       {/* Recent Bills */}
//       <div className="bg-white rounded-xl border border-gray-200">
//         <div className="p-6 border-b border-gray-200">
//           <h3 className="text-xl font-semibold text-gray-900">Recent Bills</h3>
//         </div>
//         <div className="divide-y divide-gray-200">
//           {bills.map((bill) => (
//             <BillItem
//               key={bill.id}
//               month={bill.month}
//               amount={bill.amount}
//               units={bill.units}
//               status={bill.status}
//               date={bill.date}
//               isSelected={selectedBill === bill.id}
//               onClick={() => setSelectedBill(bill.id)}
//             />
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Bills;
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Upload, FileText, CheckCircle, Filter, Loader2, AlertCircle } from "lucide-react";
import { useGetMyBillsQuery } from "../features/api/billApi";
import { BillUploadZone } from "../components/bills/BillUploadZone";

// --- UI Sub-components ---

// Renders the skeleton loader for a bill item
const BillItemSkeleton = () => (
    <div className="flex items-center justify-between p-4 border-l-4 border-l-transparent animate-pulse">
        <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
            <div>
                <div className="h-4 bg-gray-200 rounded w-28 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-20"></div>
            </div>
        </div>
        <div className="flex items-center gap-6">
            <div className="text-right">
                <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-16"></div>
            </div>
            <div className="flex items-center gap-2 w-28">
                <div className="h-4 w-4 bg-gray-200 rounded-full"></div>
                <div className="h-4 bg-gray-200 rounded w-20"></div>
            </div>
        </div>
    </div>
);

// Renders a single bill item with dynamic status
const BillItem = ({ bill, isSelected, onClick }) => {
    const statusConfig = {
        processing: { icon: Loader2, color: "text-blue-500", iconClass: "animate-spin" },
        success: { icon: CheckCircle, color: "text-green-500" },
        failed: { icon: AlertCircle, color: "text-red-500" },
        default: { icon: FileText, color: "text-gray-500" },
    };

    const { month, amount, units, status, date } = bill;
    const { icon: Icon, color, iconClass } = statusConfig[status] || statusConfig.default;

    return (
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
                    <p className="text-sm text-gray-500">Uploaded {date}</p>
                </div>
            </div>
            <div className="flex items-center gap-6">
                <div className="text-right">
                    <p className="font-mono font-semibold text-gray-900">{amount}</p>
                    <p className="text-sm text-gray-500">{units}</p>
                </div>
                <div className={`flex items-center gap-2 w-28 ${color}`}>
                    <Icon className={`w-4 h-4 ${iconClass || ''}`} />
                    <span className="text-sm capitalize">{status}</span>
                </div>
            </div>
        </div>
    );
};

// --- Main Page Component ---

const Bills = () => {
    const [selectedBill, setSelectedBill] = useState(null);
    const { data: billsData, isLoading, isError } = useGetMyBillsQuery();

    const renderBillList = () => {
        if (isLoading) {
            return (
                <div className="divide-y divide-gray-200">
                    {[...Array(3)].map((_, i) => <BillItemSkeleton key={i} />)}
                </div>
            );
        }
        if (isError) {
            return (
                <div className="text-center p-10 text-red-500 space-y-2">
                    <AlertCircle className="w-12 h-12 mx-auto text-red-300" />
                    <h4 className="font-semibold text-lg">Loading Failed</h4>
                    <p className="text-sm">Could not fetch your bills. Please try again later.</p>
                </div>
            );
        }
        if (!billsData || billsData.results.length === 0) {
            return (
                <div className="text-center p-10 text-gray-500 space-y-2">
                    <FileText className="w-12 h-12 mx-auto text-gray-300" />
                    <h4 className="font-semibold text-lg text-gray-700">No Bills Found</h4>
                    <p className="text-sm">Get started by uploading your first electricity bill above.</p>
                </div>
            );
        }
        return (
            <div className="divide-y divide-gray-200">
                {billsData.results.map((bill) => (
                    <BillItem
                        key={bill.id}
                        bill={bill}
                        isSelected={selectedBill === bill.id}
                        onClick={() => setSelectedBill(bill.id)}
                    />
                ))}
            </div>
        );
    };

    return (
        <div className="p-8 animate-fade-in">
            <header className="mb-8">
                <div className="flex justify-between items-center mb-4">
                    <div>
                        <h1 className="text-3xl font-semibold text-gray-900 mb-2">Bills & Data</h1>
                        <p className="text-gray-600">Upload and manage your electricity bills.</p>
                    </div>
                    <Button variant="outline" size="sm">
                        <Filter className="w-4 h-4 mr-2" />
                        Filter Bills
                    </Button>
                </div>
            </header>

            <BillUploadZone />

            <div className="bg-white rounded-xl border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                    <h3 className="text-xl font-semibold text-gray-900">Recent Bills</h3>
                </div>
                {renderBillList()}
            </div>
        </div>
    );
};

export default Bills;

