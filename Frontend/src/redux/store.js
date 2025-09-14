import { configureStore } from "@reduxjs/toolkit";
import rootReducer from "./rootReducer";
import { authApi } from "@/features/api/authApi";
import { userApi } from "@/features/api/userApi";
import { billApi } from "@/features/api/billApi";
import { applianceApi } from "@/features/api/applianceApi";
import { insightApi } from "@/features/api/InsightApi";



export const appStore = configureStore({
    reducer: rootReducer,
    middleware: (defaultMiddleware) =>
        defaultMiddleware().concat(
            authApi.middleware,
            userApi.middleware,
            billApi.middleware,
            applianceApi.middleware,
            insightApi.middleware,

        ),
});

const initializeApp = async () => {
    const refreshToken = localStorage.getItem("refreshToken");
    if (refreshToken) {
        console.log("App Init: Found refresh token. Attempting to refresh session.");
        try {
            // Dispatch the refresh token mutation to get a new access token and user data
            await appStore.dispatch(authApi.endpoints.refreshToken.initiate(refreshToken));
        } catch (error) {
            console.error("App Init: Token refresh failed.", error);
            // If refresh fails (e.g., token is invalid), log the user out
            appStore.dispatch(userLoggedOut());
        }
    } else {
        console.log("App Init: No refresh token found.");
    }
};

initializeApp();
