import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { userLoggedIn, userLoggedOut } from "../authSlice";
import { userApi } from "./userApi";
import { baseQueryWithReauth } from "@/redux/baseQueryWithReauth";

const BASE_URL = "http://127.0.0.1:8000/api/v1";

export const authApi = createApi({
  reducerPath: "authApi",
  // baseQuery: fetchBaseQuery({
  //   baseUrl: BASE_URL,
  //   prepareHeaders: (headers, { getState }) => {
  //     const token = getState().auth.accessToken;
  //     if (token) {
  //       headers.set('authorization', `Bearer ${token}`);
  //     }
  //     return headers;
  //   },
  // }),
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    login: builder.mutation({
      query: (credentials) => ({
        url: "/auth/login",
        method: "POST",
        body: new URLSearchParams({ username: credentials.email, password: credentials.password }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      }),
      async onQueryStarted(arg, { queryFulfilled, dispatch }) {
        try {
          const { data: tokenData } = await queryFulfilled;

          const userResponse = await dispatch(userApi.endpoints.getMe.initiate(tokenData.access_token));

          if (userResponse.isError) {

            throw new Error("Login succeeded, but failed to fetch user profile.");
          }


          const fullCredentials = {
            user: userResponse.data,
            access_token: tokenData.access_token,
            refresh_token: tokenData.refresh_token,
          };

          dispatch(userLoggedIn(fullCredentials));

        } catch (err) {
          console.error("Login sequence failed:", err);

          throw err;
        }
      },
    }),

    signup: builder.mutation({
      query: (userInfo) => ({
        url: "/auth/signup",
        method: "POST",
        body: userInfo,
      }),

      async onQueryStarted(arg, { queryFulfilled, dispatch }) {
        try {
          await queryFulfilled;
          console.log("Signup successful. Logging in...");
          dispatch(authApi.endpoints.login.initiate({ email: arg.email, password: arg.password }));
        } catch (err) {
          console.error("Signup failed:", err);
        }
      }
    }),

    logout: builder.mutation({
      query: (body) => ({
        url: '/auth/logout',
        method: 'POST',
        body,
      }),
      async onQueryStarted(arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
        } finally {
          dispatch(userLoggedOut());
          dispatch(userApi.util.resetApiState());
        }
      },
    }),


    refreshToken: builder.mutation({
      query: (refreshToken) => ({
        url: "/auth/refresh",
        method: "POST",
        body: { refresh_token: refreshToken },
      }),
      async onQueryStarted(arg, { queryFulfilled, dispatch }) {
        try {
          const { data } = await queryFulfilled;

          // ✅ Immediately persist the rotated tokens
          localStorage.setItem("accessToken", data.access_token);
          localStorage.setItem("refreshToken", data.refresh_token);

          // Then fetch user profile
          const userResponse = await dispatch(
            userApi.endpoints.getMe.initiate(data.access_token)
          );

          const credentials = {
            user: userResponse.data,
            access_token: data.access_token,
            refresh_token: data.refresh_token,
          };
          dispatch(userLoggedIn(credentials));
        } catch (error) {
          console.error("Token refresh failed:", error);
          dispatch(userLoggedOut());
        }
      },
    }),


    // ======Password Change========
    requestPasswordReset: builder.mutation({
      query: (body) => ({ // Expects { email: "user@example.com" }
        url: "/auth/password-reset-request",
        method: "POST",
        body,
      }),
    }),
    confirmPasswordReset: builder.mutation({
      query: (body) => ({ // Expects { token, new_password, confirm_password }
        url: "/auth/password-reset-confirm",
        method: "POST",
        body,
      }),
    }),

    // =========Email Change=========
    requestVerificationEmail: builder.mutation({
      query: (body) => ({ // Expects { email: "user@example.com" }
        url: "/auth/email/request-verification-email",
        method: "POST",
        body,
      }),
    }),
    verifyEmail: builder.mutation({
      query: (token) => ({
        url: "/auth/email/verify-email",
        method: "POST",
        params: { token },
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useSignupMutation,
  useLogoutMutation,
  useRefreshTokenMutation,
  useRequestPasswordResetMutation,
  useConfirmPasswordResetMutation,
  useRequestVerificationEmailMutation,
  useVerifyEmailMutation,
} = authApi;

