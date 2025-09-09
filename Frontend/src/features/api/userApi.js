import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { userLoggedOut } from "../authSlice";
import { baseQueryWithReauth } from "@/redux/baseQueryWithReauth";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const userApi = createApi({
  reducerPath: "userApi",
  // Define a tag for user data to enable automatic refetching
  reducerPath: "userApi",
  tagTypes: ['User'],
  // baseQuery: fetchBaseQuery({
  //   baseUrl: BASE_URL,
  //   prepareHeaders: (headers, { getState }) => {
  //     // Attach the JWT access token to every request
  //     const token = getState().auth.accessToken;
  //     if (token) {
  //       headers.set('authorization', `Bearer ${token}`);
  //     }
  //     return headers;
  //   },
  // }),
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    // 1. GET CURRENT USER PROFILE
    getMe: builder.query({
      // THE FIX: Allow an optional token argument to be passed in.
      query: (accessToken) => ({
        url: "/users/me",
        headers: accessToken ? { 'authorization': `Bearer ${accessToken}` } : {},
      }),
      providesTags: ['User'],
      async onQueryStarted(arg, { queryFulfilled, dispatch }) {
        try {
          await queryFulfilled;
        } catch (error) {
          console.error("GetMe Query Failed, logging out.", error);
          dispatch(userLoggedOut());
        }
      }
    }),
    // 2. UPDATE CURRENT USER PROFILE
    updateMyProfile: builder.mutation({
      query: (updateData) => ({ // Matches UserUpdate schema
        url: "/users/me",
        method: "PATCH",
        body: updateData // e.g., { first_name: "Jane" }
      }),
      // On success, invalidate the 'User' tag to force a refetch of getMe
      invalidatesTags: ['User']
    }),
    // 3. CHANGE USER'S PASSWORD
    changeMyPassword: builder.mutation({
      query: (passwordData) => ({ // Matches UserPasswordChange schema
        url: "/users/change-password",
        method: "POST",
        body: passwordData // { current_password, new_password }
      })
    }),
    // 4. DEACTIVATE USER'S ACCOUNT
    deactivateMyAccount: builder.mutation({
      query: () => ({
        url: "/users/me",
        method: "DELETE"
      }),
      async onQueryStarted(arg, { queryFulfilled, dispatch }) {
        try {
          await queryFulfilled;
          // After a successful deactivation, log the user out from the client
          dispatch(userLoggedOut());
        } catch (err) {
          console.error("Deactivation failed on the backend, but forcing logout.", err)
          dispatch(userLoggedOut());
        }
      }
    })
  }),
});

// Export the new hooks to be used in your components
export const {
  useGetMeQuery,
  useUpdateMyProfileMutation,
  useChangeMyPasswordMutation,
  useDeactivateMyAccountMutation,
} = userApi;
