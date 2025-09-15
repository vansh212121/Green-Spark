import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQueryWithReauth } from "@/redux/baseQueryWithReauth";

export const insightApi = createApi({
    reducerPath: "insightApi",
    // Define ID-based tags for caching statuses and reports for specific bills.
    tagTypes: ['InsightStatus', 'InsightReport'],
    baseQuery: baseQueryWithReauth,
    endpoints: (builder) => ({
        // GET /insights/status/{bill_id}
        getInsightStatus: builder.query({
            query: (billId) => `/insights/status/${billId}`,
            // Provides a specific tag for this bill's insight status.
            providesTags: (result, error, billId) => [{ type: 'InsightStatus', id: billId }],
        }),

        // GET /insights/report/{bill_id}
        getInsightReport: builder.query({
            query: (billId) => `/insights/report/${billId}`,
            // Provides a specific tag for this bill's insight report.
            providesTags: (result, error, billId) => [{ type: 'InsightReport', id: billId }],
        }),

        // POST /insights/report/{bill_id}/refresh
        refreshInsightReport: builder.mutation({
            query: (billId) => ({
                url: `/insights/report/${billId}/refresh`,
                method: "POST",
            }),
            // When a refresh is triggered, we must invalidate both the old report and the status
            // to encourage the UI to start polling the status endpoint again.
            invalidatesTags: (result, error, billId) => [
                { type: 'InsightReport', id: billId },
                { type: 'InsightStatus', id: billId }
            ],
        }),
    }),
});

// Export the auto-generated hooks for use in our components
export const {
    useGetInsightStatusQuery,
    useGetInsightReportQuery,
    useRefreshInsightReportMutation,
} = insightApi;
