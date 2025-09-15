import { createSlice } from "@reduxjs/toolkit";

const savedUser = JSON.parse(localStorage.getItem("user"));
const savedAccessToken = localStorage.getItem("accessToken");
const savedRefreshToken = localStorage.getItem("refreshToken");

const initialState = {
    user: savedUser || null,
    accessToken: savedAccessToken || null,
    refreshToken: savedRefreshToken || null,
    isAuthenticated: !!savedAccessToken,
};

const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        userLoggedIn: (state, { payload }) => {
            state.isAuthenticated = true;

            if (payload.user) {
                state.user = payload.user;
                localStorage.setItem("user", JSON.stringify(payload.user));
            }
            if (payload.access_token || payload.accessToken) {
                state.accessToken = payload.access_token || payload.accessToken;
                localStorage.setItem("accessToken", state.accessToken);
            }
            if (payload.refresh_token || payload.refreshToken) {
                state.refreshToken = payload.refresh_token || payload.refreshToken;
                localStorage.setItem("refreshToken", state.refreshToken);
            }
        },

        userLoggedOut: (state) => {
            state.user = null;
            state.accessToken = null;
            state.refreshToken = null;
            state.isAuthenticated = false;

            // clear localStorage
            localStorage.removeItem("user");
            localStorage.removeItem("accessToken");
            localStorage.removeItem("refreshToken");
        },
    },
});

export const { userLoggedIn, userLoggedOut } = authSlice.actions;
export default authSlice.reducer;

export const selectCurrentUser = (state) => state.auth.user;
export const selectRefreshToken = (state) => state.auth.refreshToken;
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated;

export const selectAccessToken = (state) => state.auth.accessToken;
