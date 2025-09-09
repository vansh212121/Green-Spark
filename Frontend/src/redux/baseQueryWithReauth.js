import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { userLoggedOut, userLoggedIn } from "@/features/authSlice";
import { authApi } from "@/features/api/authApi";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

// Wrapped baseQuery
const rawBaseQuery = fetchBaseQuery({
    baseUrl: BASE_URL,
    prepareHeaders: (headers, { getState }) => {
        const token = getState().auth.accessToken;
        if (token) {
            headers.set("authorization", `Bearer ${token}`);
        }
        return headers;
    },
});

export const baseQueryWithReauth = async (args, api, extraOptions) => {
    let result = await rawBaseQuery(args, api, extraOptions);

    if (result.error && result.error.status === 401) {
        console.warn("⏳ Access token expired. Trying refresh...");
        const refreshToken = localStorage.getItem("refreshToken");

        if (refreshToken) {
            try {
                // Try to refresh
                const refreshResult = await rawBaseQuery(
                    {
                        url: "/auth/refresh",
                        method: "POST",
                        body: { refresh_token: refreshToken },
                    },
                    api,
                    extraOptions
                );

                if (refreshResult.data) {
                    const { access_token, refresh_token } = refreshResult.data;

                    // ✅ Save new tokens immediately
                    localStorage.setItem("accessToken", access_token);
                    localStorage.setItem("refreshToken", refresh_token);

                    api.dispatch(
                        userLoggedIn({
                            user: api.getState().auth.user, // keep old user until refetched
                            access_token,
                            refresh_token,
                        })
                    );

                    // Retry the original query with new token
                    result = await rawBaseQuery(args, api, extraOptions);
                } else {
                    api.dispatch(userLoggedOut());
                }
            } catch (err) {
                console.error("Refresh failed:", err);
                api.dispatch(userLoggedOut());
            }
        } else {
            api.dispatch(userLoggedOut());
        }
    }

    return result;
};
