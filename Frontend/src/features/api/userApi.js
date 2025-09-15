import { createApi } from "@reduxjs/toolkit/query/react";
import { userLoggedOut } from "../authSlice";
import { baseQueryWithReauth } from "@/redux/baseQueryWithReauth";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const userApi = createApi({
  reducerPath: "userApi",
  // Define a tag for user data to enable automatic refetching
  reducerPath: "userApi",
  tagTypes: ['User'],
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    // 1. GET CURRENT USER PROFILE
    getMe: builder.query({
      query: () => '/users/me',
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

    // PATCH /users/me
    updateMyProfile: builder.mutation({
      query: (updateData) => ({ // Matches the UserUpdate schema
        url: "/users/me",
        method: "PATCH",
        body: updateData
      }),
      invalidatesTags: ['User'] // On success, this invalidates the 'User' tag, forcing getMe to refetch
    }),

    // POST /users/change-password
    changeMyPassword: builder.mutation({
      query: (passwordData) => ({ // Matches the UserPasswordChange schema
        url: "/users/change-password",
        method: "POST",
        body: passwordData
      })
    }),

    // DELETE /users/me
    deactivateMyAccount: builder.mutation({
      query: () => ({
        url: "/users/me",
        method: "DELETE"
      }),
      async onQueryStarted(arg, { queryFulfilled, dispatch }) {
        try {
          await queryFulfilled;
          // Always log out on the client after a successful deactivation
          dispatch(userLoggedOut());
        } catch (err) {
          console.error("Deactivation failed on server, but forcing logout.", err);
          dispatch(userLoggedOut());
        }
      }
    })
  }),
});

export const {
  useGetMeQuery,
  useUpdateMyProfileMutation,
  useChangeMyPasswordMutation,
  useDeactivateMyAccountMutation,
} = userApi;
