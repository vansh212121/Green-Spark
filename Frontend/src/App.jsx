import { TooltipProvider } from "@/components/ui/tooltip";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import Overview from "./pages/Overview";
import Bills from "./pages/Bills";
import Appliances from "./pages/Appliances";
import Insights from "./pages/Insights";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import { Toaster } from "sonner";
import { Provider } from "react-redux";
import AuthPage from "./components/auth/AuthPage";
import ResetPasswordPage from "./components/auth/ResetPasswordPage";
import VerifyEmailPage from "./components/auth/VerifyEmailPage";
import { appStore } from "./redux/store";
import ConfirmEmailChangePage from "./components/auth/ConfirmEmailChangePage";
import ProtectedRoute from "./components/auth/ProtectedRoute";

const App = () => (
  <Provider store={appStore}>
    <TooltipProvider>
      <Toaster />
      <BrowserRouter>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Layout />}>
              <Route index element={<Overview />} />
              <Route path="bills" element={<Bills />} />
              <Route path="appliances" element={<Appliances />} />
              <Route path="insights" element={<Insights />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Route>
          <Route path="auth" element={<AuthPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route
            path="/confirm-email-change"
            element={<ConfirmEmailChangePage />}
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </Provider>
);

export default App;
