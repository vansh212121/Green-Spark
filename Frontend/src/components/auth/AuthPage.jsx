import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  User,
  CheckCircle,
  MapPin,
} from "lucide-react";

// RTK Query Hooks for API calls
import { useLoginMutation, useSignupMutation } from "@/features/api/authApi";
import { useState } from "react";
import { ForgotPasswordModal } from "./PasswordResetModal";
import { RequestVerificationModal } from "./RequestVerificationModal";

const AuthPage = () => {
  const [mode, setMode] = useState("login");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    username: "",
    timezone: "",
    confirmPassword: "",
  });

  const navigate = useNavigate();

  // --- RTK Query Hooks ---
  const [login, { isLoading: isLoginLoading }] = useLoginMutation();
  const [signup, { isLoading: isSignupLoading }] = useSignupMutation();
  const isLoading = isLoginLoading || isSignupLoading;

  const [isForgotPasswordModalOpen, setIsForgotPasswordModalOpen] =
    useState(false);
  const [isRequestVerificationModalOpen, setisRequestVerificationModalOpen] =
    useState(false);

  // --- Helper Functions ---
  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleModeSwitch = () => {
    setMode(mode === "login" ? "signup" : "login");
    setFormData({
      email: "",
      password: "",
      first_name: "",
      last_name: "",
      username: "",
      timezone: "",
      confirmPassword: "",
    });
  };

  // --- Main Submit Handler ---
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (mode === "signup" && formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match."); // Step 2: Use toast.error
      return;
    }

    try {
      if (mode === "login") {
        await login({
          email: formData.email,
          password: formData.password,
        }).unwrap();
        toast.success("Login successful!", {
          // Step 2: Use toast.success
          description: "Redirecting you to the dashboard...",
        });
      } else {
        const { first_name, last_name, username, email, password, timezone } =
          formData;
        await signup({
          first_name,
          last_name,
          username,
          email,
          password,
          timezone,
        }).unwrap();
        toast.success("Account created successfully!", {
          description: "Logging you in and redirecting...",
        });
      }
      setTimeout(() => navigate("/"), 1000);
    } catch (err) {
      // --- CORRECTED Custom Error Handling Logic ---
      let errorMessage = "An unknown error occurred."; // Default fallback

      // Check for your custom error structure first.
      if (err?.data?.error?.message) {
        errorMessage = err.data.error.message;
      }
      // Then, as a fallback, check for FastAPI's default validation error structure.
      else if (err.data?.detail) {
        if (Array.isArray(err.data.detail)) {
          const firstError = err.data.detail[0];
          errorMessage = `${firstError.loc[1]} - ${firstError.msg}`;
        } else {
          errorMessage = err.data.detail;
        }
      }

      // toast.error("Authentication Failed", {
      toast.error(err?.data?.error?.code, {
        description: errorMessage,
      });
      console.error("Auth error:", err);
    }
  };

  // UI feedback, not validation
  const passwordStrength = (password) => {
    if (!password) return { strength: "", color: "bg-gray-200", width: "0%" };
    if (password.length < 6)
      return { strength: "weak", color: "bg-red-500", width: "33%" };
    if (password.length < 10)
      return { strength: "medium", color: "bg-yellow-500", width: "66%" };
    return { strength: "strong", color: "bg-green-500", width: "100%" };
  };
  const currentPasswordStrength = passwordStrength(formData.password);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-500 rounded-2xl mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {mode === "login" ? "Welcome Back!" : "Join Us Today"}
          </h1>
          <p className="text-gray-600">
            {mode === "login"
              ? "Sign in to access your account"
              : "Create your account to get started"}
          </p>
        </div>

        <Card className="shadow-lg border-gray-200">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl font-semibold text-center">
              {mode === "login" ? "Sign In" : "Create Account"}
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            <CardDescription className="text-center">
              {mode === "login"
                ? "Enter your credentials to continue"
                : "Fill in your details to create an account"}
            </CardDescription>
            <form onSubmit={handleSubmit} className="space-y-5">
              {mode === "signup" && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first_name">First Name</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="first_name"
                          placeholder="John"
                          value={formData.first_name}
                          onChange={(e) =>
                            handleInputChange("first_name", e.target.value)
                          }
                          disabled={isLoading}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="last_name">Last Name</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="last_name"
                          placeholder="Doe"
                          value={formData.last_name}
                          onChange={(e) =>
                            handleInputChange("last_name", e.target.value)
                          }
                          disabled={isLoading}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="username"
                        placeholder="johndoe21"
                        value={formData.username}
                        onChange={(e) =>
                          handleInputChange("username", e.target.value)
                        }
                        disabled={isLoading}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="timezone">Timezone</Label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="timezone"
                        placeholder="e.g., Asia/Kolkata"
                        value={formData.timezone}
                        onChange={(e) =>
                          handleInputChange("timezone", e.target.value)
                        }
                        disabled={isLoading}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@example.com"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    disabled={isLoading}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={(e) =>
                      handleInputChange("password", e.target.value)
                    }
                    disabled={isLoading}
                    className="pl-10 pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
                {mode === "signup" && formData.password && (
                  <div className="space-y-2 pt-1">
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full transition-all duration-300 ${currentPasswordStrength.color}`}
                        style={{ width: currentPasswordStrength.width }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              {mode === "signup" && (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="Confirm your password"
                      value={formData.confirmPassword}
                      onChange={(e) =>
                        handleInputChange("confirmPassword", e.target.value)
                      }
                      disabled={isLoading}
                      className="pl-10 pr-12"
                      required
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setShowConfirmPassword(!showConfirmPassword)
                      }
                      className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                      disabled={isLoading}
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                    {formData.confirmPassword &&
                      formData.confirmPassword === formData.password && (
                        <CheckCircle className="absolute right-10 top-3 h-4 w-4 text-green-500" />
                      )}
                  </div>
                </div>
              )}

              {mode === "login" && (
                <div className="text-sm flex justify-between">
                  <button
                    type="button"
                    className="font-medium text-primary-600 hover:underline"
                    onClick={() => setIsForgotPasswordModalOpen(true)}
                  >
                    Forgot Password?
                  </button>
                  <button
                    type="button"
                    className="text-primary-600 hover:text-primary-700 hover:underline transition-colors font-medium"
                    onClick={() => setisRequestVerificationModalOpen(true)}
                  >
                    Unverified? click here!
                  </button>
                </div>
              )}

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 font-medium"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>
                      {mode === "login"
                        ? "Signing In..."
                        : "Creating Account..."}
                    </span>
                  </div>
                ) : mode === "login" ? (
                  "Sign In"
                ) : (
                  "Create Account"
                )}
              </Button>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-4 text-gray-500">or</span>
              </div>
            </div>

            <div className="text-center">
              <span className="text-sm text-gray-600">
                {mode === "login"
                  ? "Don't have an account?"
                  : "Already have an account?"}
              </span>
              <button
                type="button"
                onClick={handleModeSwitch}
                disabled={isLoading}
                className="ml-2 text-sm text-primary-600 hover:underline font-semibold disabled:opacity-50"
              >
                {mode === "login" ? "Sign Up" : "Sign In"}
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
      <ForgotPasswordModal
        isOpen={isForgotPasswordModalOpen}
        onClose={() => setIsForgotPasswordModalOpen(false)}
      />
      <RequestVerificationModal
        isOpen={isRequestVerificationModalOpen}
        onClose={() => setisRequestVerificationModalOpen(false)}
      />
    </div>
  );
};

export default AuthPage;
