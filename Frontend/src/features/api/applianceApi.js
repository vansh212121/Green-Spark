import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQueryWithReauth } from "@/redux/baseQueryWithReauth";

export const applianceApi = createApi({
    reducerPath: "applianceApi",
    tagTypes: ['ApplianceList', 'ApplianceCatalog', 'Estimates'],
    baseQuery: baseQueryWithReauth,
    endpoints: (builder) => ({
        // GET /appliances/catalog
        getApplianceCatalog: builder.query({
            query: () => "/appliances/catalog",
            providesTags: ['ApplianceCatalog'], // A simple tag since this is a global list.
        }),

        // GET /appliances/{bill_id}/appliances
        getAppliancesForBill: builder.query({
            query: (billId) => `/appliances/${billId}/appliances`,
            // Provides a specific tag for this bill's appliance list, e.g., { type: 'ApplianceList', id: 'bill-123' }
            providesTags: (result, error, billId) => [{ type: 'ApplianceList', id: billId }],
        }),

        // GET /appliances/{appliance_id}
        getApplianceById: builder.query({
            query: (applianceId) => `/appliances/${applianceId}`,
        }),

        // GET /appliances/estimates/{bill_id}
        getEstimatesForBill: builder.query({
            query: (billId) => `/appliances/estimates/${billId}`,
            // Provides a specific tag for this bill's estimates.
            providesTags: (result, error, billId) => [{ type: 'Estimates', id: billId }],
        }),

        // POST /appliances/{bill_id}/create
        createAppliance: builder.mutation({
            query: ({ billId, body }) => ({
                url: `/appliances/${billId}/create`,
                method: "POST",
                body,
            }),
            // When an appliance is created, invalidate the specific list it belongs to.
            invalidatesTags: (result, error, { billId }) => [{ type: 'ApplianceList', id: billId }],
        }),

        // PATCH /appliances/{bill_id}/{appliance_id}
        updateAppliance: builder.mutation({
            query: ({ billId, applianceId, body }) => ({
                url: `/appliances/${billId}/${applianceId}`,
                method: "PATCH",
                body,
            }),
            // When an appliance is updated, invalidate the specific list it belongs to.
            invalidatesTags: (result, error, { billId }) => [{ type: 'ApplianceList', id: billId }],
        }),

        // DELETE /appliances/{bill_id}/{appliance_id}
        deleteAppliance: builder.mutation({
            query: ({ billId, applianceId }) => ({
                url: `/appliances/${billId}/${applianceId}`,
                method: "DELETE",
            }),
            // When an appliance is deleted, invalidate the specific list it belongs to.
            invalidatesTags: (result, error, { billId }) => [{ type: 'ApplianceList', id: billId }],
        }),
    }),
});

// Export the auto-generated hooks for use in our components
export const {
    useGetApplianceCatalogQuery,
    useGetAppliancesForBillQuery,
    useGetApplianceByIdQuery,
    useGetEstimatesForBillQuery,
    useCreateApplianceMutation,
    useUpdateApplianceMutation,
    useDeleteApplianceMutation,
} = applianceApi;
