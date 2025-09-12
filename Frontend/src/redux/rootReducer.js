import { combineReducers } from "@reduxjs/toolkit";
import authReducer from "../features/authSlice";
import { authApi } from "@/features/api/authApi";
import { userApi } from "@/features/api/userApi";
import { billApi } from "@/features/api/billApi";
import { applianceApi } from "@/features/api/applianceApi";


const rootReducer = combineReducers({
    // API Reducers
    [authApi.reducerPath]: authApi.reducer,
    [userApi.reducerPath]: userApi.reducer,
    [billApi.reducerPath]: billApi.reducer,
    [applianceApi.reducerPath]: applianceApi.reducer,

    // Regular Slice Reducer
    auth: authReducer,
});

export default rootReducer;
