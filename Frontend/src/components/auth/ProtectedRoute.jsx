import { selectIsAuthenticated } from "@/features/authSlice";
import React from "react";
import { useSelector } from "react-redux";
import { Navigate, Outlet, useLocation } from "react-router-dom";

const ProtectedRoute = () => {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const location = useLocation();

  if (isAuthenticated) {
    // If the user is authenticated, render the child routes (e.g., Dashboard, Settings).
    // The <Outlet /> component is a placeholder for the nested routes.
    return <Outlet />;
  }

  // If the user is not authenticated, redirect them to the auth page.
  // We pass the original location they were trying to visit in the state.
  // This allows us to redirect them back after a successful login.
  return <Navigate to="/auth" state={{ from: location }} replace />;
};

export default ProtectedRoute;
