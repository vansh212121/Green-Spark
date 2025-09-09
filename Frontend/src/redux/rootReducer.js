import { combineReducers } from "@reduxjs/toolkit";
import authReducer from "../features/authSlice";
import { authApi } from "@/features/api/authApi";
import { userApi } from "@/features/api/userApi";


const rootReducer = combineReducers({
    // API Reducers
    [authApi.reducerPath]: authApi.reducer,
    [userApi.reducerPath]: userApi.reducer,

    // Regular Slice Reducer
    auth: authReducer,
});

export default rootReducer;
