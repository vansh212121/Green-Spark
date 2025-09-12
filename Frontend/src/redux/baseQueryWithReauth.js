import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { userLoggedOut, userLoggedIn } from "@/features/authSlice";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

const rawBaseQuery = fetchBaseQuery({
    baseUrl: BASE_URL,
    prepareHeaders: (headers, { getState }) => {
        const token = getState().auth.accessToken;
        console.log("🔑 Using access token:", token?.slice(0, 20) + "...");
        if (token) {
            headers.set("authorization", `Bearer ${token}`);
        }
        return headers;
    }

});

// A list of endpoints where a 401 error should NOT trigger a token refresh,
// as they are expected to fail with 401 on bad user credentials.
const refreshBlacklistedEndpoints = [
    '/auth/login',
    '/auth/logout',
];

export const baseQueryWithReauth = async (args, api, extraOptions) => {
    let result = await rawBaseQuery(args, api, extraOptions);

    // THE FIX: Check if the failed request's URL is in our blacklist.
    if (result.error && result.error.status === 401 && !refreshBlacklistedEndpoints.includes(args.url)) {
        console.warn("⏳ Access token expired. Trying refresh...");
        const refreshToken = localStorage.getItem("refreshToken");

        if (refreshToken) {
            try {
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
                    localStorage.setItem("accessToken", access_token);
                    localStorage.setItem("refreshToken", refresh_token);

                    api.dispatch(
                        userLoggedIn({
                            user: api.getState().auth.user,
                            access_token,
                            refresh_token,
                        })
                    );

                    // Retry the original query with the new token
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




