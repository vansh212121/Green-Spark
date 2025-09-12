import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQueryWithReauth } from "@/redux/baseQueryWithReauth";

// --- Helper Functions for Data Transformation ---
const formatMonthYear = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
};

const formatRelativeDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays <= 1) return "Today";
    if (diffDays <= 30) return `${diffDays} days ago`;
    const diffMonths = Math.floor(diffDays / 30);
    return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
};

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount || 0);
};


export const billApi = createApi({
    reducerPath: "billApi",
    tagTypes: ['BillList', 'Bill'],
    baseQuery: baseQueryWithReauth,
    endpoints: (builder) => ({
        getMyBills: builder.query({
            query: (params) => ({
                url: "/users/me/bills",
                params: params,
            }),
            providesTags: ['BillList'],
            transformResponse: (responseData) => {
                if (!responseData || !Array.isArray(responseData.items)) {
                    console.error("API did not return a valid 'items' array. Returning empty.");
                    return { ...responseData, results: [] };
                }

                const transformedBills = responseData.items.map(bill => ({
                    id: bill.id,
                    // THE FIX: Changed from billing_period_end_date to billing_period_start
                    month: formatMonthYear(bill.billing_period_start),
                    amount: formatCurrency(bill.cost_total),
                    units: bill.kwh_total ? `${bill.kwh_total.toFixed(2)} kWh` : 'N/A',
                    status: bill.parse_status || 'unknown',
                    date: formatRelativeDate(bill.created_at),
                }));

                return { ...responseData, results: transformedBills };
            }
        }),

        // Query to get a single, detailed bill by its ID
        getBillById: builder.query({
            query: (billId) => `/bills/${billId}`,
            // Provides a specific tag for this bill, e.g., { type: 'Bill', id: '123-abc' }
            providesTags: (result, error, id) => [{ type: 'Bill', id }],
        }),

        // Mutation to initiate the upload process by getting a presigned URL
        requestUploadUrl: builder.mutation({
            query: (body) => ({ // Expects { filename: "...", content_type: "..." }
                url: "/bills/upload",
                method: "POST",
                body,
            }),
        }),

        // Mutation to confirm the upload is complete and start the backend parsing
        confirmBillUpload: builder.mutation({
            query: (body) => ({ // Expects { file_uri: "..." }
                url: "/bills/confirm",
                method: "POST",
                body,
            }),
            // After confirming, the list of bills has changed. Invalidate the cache.
            invalidatesTags: ['BillList'],
        }),

        // Mutation to delete a bill by its ID
        deleteBill: builder.mutation({
            query: (billId) => ({
                url: `/bills/${billId}`,
                method: "DELETE",
            }),
            // After deleting, the list of bills has changed. Invalidate the cache.
            invalidatesTags: ['BillList'],
        }),

        triggerBillEstimation: builder.mutation({
            query: (billId) => ({
                url: `/bills/${billId}/estimate`,
                method: "POST",
            }),
            // We may not need to invalidate anything since this just queues a task
        }),
    }),
});

// Export the auto-generated hooks for use in our components
export const {
    useGetMyBillsQuery,
    useGetBillByIdQuery,
    useRequestUploadUrlMutation,
    useConfirmBillUploadMutation,
    useDeleteBillMutation,
    useTriggerBillEstimationMutation,
} = billApi;
