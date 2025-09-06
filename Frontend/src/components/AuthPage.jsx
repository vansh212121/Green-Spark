import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Eye, EyeOff, Mail, Lock, User, CheckCircle, MapPin } from "lucide-react";

const AuthPage = () => {
  const [mode, setMode] = useState("login");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    firstName: "",
    lastName: "",
    username: "",
    location: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    if (mode === "signup") {
      if (!formData.firstName.trim()) {
        newErrors.firstName = "First name is required";
      } else if (formData.firstName.trim().length < 2) {
        newErrors.firstName = "First name must be at least 2 characters";
      }

      if (!formData.lastName.trim()) {
        newErrors.lastName = "Last name is required";
      } else if (formData.lastName.trim().length < 2) {
        newErrors.lastName = "Last name must be at least 2 characters";
      }

      if (!formData.username.trim()) {
        newErrors.username = "Username is required";
      } else if (formData.username.trim().length < 3) {
        newErrors.username = "Username must be at least 3 characters";
      }

      if (!formData.location.trim()) {
        newErrors.location = "Location is required";
      }

      if (!formData.confirmPassword) {
        newErrors.confirmPassword = "Please confirm your password";
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = "Passwords do not match";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      console.log(`${mode} attempt:`, formData);
    } catch (error) {
      console.error('Auth error:', error);
      setErrors({ general: 'Something went wrong. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleModeSwitch = () => {
    setMode(mode === "login" ? "signup" : "login");
    setErrors({});
    setFormData({
      email: "",
      password: "",
      firstName: "",
      lastName: "",
      username: "",
      location: "",
      confirmPassword: "",
    });
  };

  const passwordStrength = (password) => {
    if (password.length < 6) return { strength: 'weak', color: 'bg-red-500', width: '33%' };
    if (password.length < 10) return { strength: 'medium', color: 'bg-yellow-500', width: '66%' };
    return { strength: 'strong', color: 'bg-green-500', width: '100%' };
  };

  const currentPasswordStrength = passwordStrength(formData.password);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
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

        {/* Main Form Card */}
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl font-semibold text-center">
              {mode === "login" ? "Sign In" : "Create Account"}
            </CardTitle>
            <CardDescription className="text-center">
              {mode === "login"
                ? "Enter your credentials to continue"
                : "Fill in your details to create an account"}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            {errors.general && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{errors.general}</p>
              </div>
            )}

            <div className="space-y-5">
              {mode === "signup" && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="firstName" className="text-sm font-medium text-gray-700">
                        First Name
                      </Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
                        <Input
                          id="firstName"
                          type="text"
                          placeholder="Enter first name"
                          value={formData.firstName}
                          onChange={(e) => handleInputChange("firstName", e.target.value)}
                          className={`pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-colors ${
                            errors.firstName ? "border-red-300 focus:border-red-500 focus:ring-red-200" : "focus:border-primary-500 focus:ring-primary-200"
                          }`}
                          disabled={isLoading}
                        />
                      </div>
                      {errors.firstName && (
                        <p className="text-red-500 text-sm flex items-center gap-1">
                          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
                          {errors.firstName}
                        </p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="lastName" className="text-sm font-medium text-gray-700">
                        Last Name
                      </Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
                        <Input
                          id="lastName"
                          type="text"
                          placeholder="Enter last name"
                          value={formData.lastName}
                          onChange={(e) => handleInputChange("lastName", e.target.value)}
                          className={`pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-colors ${
                            errors.lastName ? "border-red-300 focus:border-red-500 focus:ring-red-200" : "focus:border-primary-500 focus:ring-primary-200"
                          }`}
                          disabled={isLoading}
                        />
                      </div>
                      {errors.lastName && (
                        <p className="text-red-500 text-sm flex items-center gap-1">
                          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
                          {errors.lastName}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="username" className="text-sm font-medium text-gray-700">
                      Username
                    </Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
                      <Input
                        id="username"
                        type="text"
                        placeholder="Choose a username"
                        value={formData.username}
                        onChange={(e) => handleInputChange("username", e.target.value)}
                        className={`pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-colors ${
                          errors.username ? "border-red-300 focus:border-red-500 focus:ring-red-200" : "focus:border-primary-500 focus:ring-primary-200"
                        }`}
                        disabled={isLoading}
                      />
                    </div>
                    {errors.username && (
                      <p className="text-red-500 text-sm flex items-center gap-1">
                        <span className="w-1 h-1 bg-red-500 rounded-full"></span>
                        {errors.username}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="location" className="text-sm font-medium text-gray-700">
                      Location
                    </Label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
                      <Input
                        id="location"
                        type="text"
                        placeholder="Enter your location"
                        value={formData.location}
                        onChange={(e) => handleInputChange("location", e.target.value)}
                        className={`pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-colors ${
                          errors.location ? "border-red-300 focus:border-red-500 focus:ring-red-200" : "focus:border-primary-500 focus:ring-primary-200"
                        }`}
                        disabled={isLoading}
                      />
                    </div>
                    {errors.location && (
                      <p className="text-red-500 text-sm flex items-center gap-1">
                        <span className="w-1 h-1 bg-red-500 rounded-full"></span>
                        {errors.location}
                      </p>
                    )}
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Email Address
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email address"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    className={`pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-colors ${
                      errors.email ? "border-red-300 focus:border-red-500 focus:ring-red-200" : "focus:border-primary-500 focus:ring-primary-200"
                    }`}
                    disabled={isLoading}
                  />
                </div>
                {errors.email && (
                  <p className="text-red-500 text-sm flex items-center gap-1">
                    <span className="w-1 h-1 bg-red-500 rounded-full"></span>
                    {errors.email}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    className={`pl-10 pr-12 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-colors ${
                      errors.password ? "border-red-300 focus:border-red-500 focus:ring-red-200" : "focus:border-primary-500 focus:ring-primary-200"
                    }`}
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 transition-colors"
                    disabled={isLoading}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                
                {mode === "signup" && formData.password && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Password strength</span>
                      <span className="capitalize">{currentPasswordStrength.strength}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className={`h-1.5 rounded-full transition-all duration-300 ${currentPasswordStrength.color}`}
                        style={{ width: currentPasswordStrength.width }}
                      ></div>
                    </div>
                  </div>
                )}
                
                {errors.password && (
                  <p className="text-red-500 text-sm flex items-center gap-1">
                    <span className="w-1 h-1 bg-red-500 rounded-full"></span>
                    {errors.password}
                  </p>
                )}
              </div>

              {mode === "signup" && (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                    Confirm Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="Confirm your password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                      className={`pl-10 pr-12 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-colors ${
                        errors.confirmPassword ? "border-red-300 focus:border-red-500 focus:ring-red-200" : "focus:border-primary-500 focus:ring-primary-200"
                      }`}
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 transition-colors"
                      disabled={isLoading}
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                    {formData.confirmPassword && formData.confirmPassword === formData.password && (
                      <CheckCircle className="absolute right-10 top-3.5 h-4 w-4 text-green-500" />
                    )}
                  </div>
                  {errors.confirmPassword && (
                    <p className="text-red-500 text-sm flex items-center gap-1">
                      <span className="w-1 h-1 bg-red-500 rounded-full"></span>
                      {errors.confirmPassword}
                    </p>
                  )}
                </div>
              )}

              {mode === "login" && (
                <div className="flex justify-between text-sm">
                  <button
                    type="button"
                    className="text-primary-600 hover:text-primary-700 hover:underline transition-colors font-medium"
                    onClick={() => console.log('Reset password clicked')}
                  >
                    Forgot Password?
                  </button>
                  <button
                    type="button"
                    className="text-primary-600 hover:text-primary-700 hover:underline transition-colors font-medium"
                    onClick={() => console.log('Reset email clicked')}
                  >
                    Reset Email
                  </button>
                </div>
              )}

              <Button
                onClick={handleSubmit}
                disabled={isLoading}
                className="w-full h-12 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 disabled:opacity-70"
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    {mode === "login" ? "Signing In..." : "Creating Account..."}
                  </div>
                ) : (
                  mode === "login" ? "Sign In" : "Create Account"
                )}
              </Button>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator className="w-full" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-4 text-gray-500">or</span>
              </div>
            </div>

            <div className="text-center">
              <span className="text-sm text-gray-600">
                {mode === "login" ? "Don't have an account?" : "Already have an account?"}
              </span>
              <button
                type="button"
                onClick={handleModeSwitch}
                disabled={isLoading}
                className="ml-2 text-sm text-primary-600 hover:text-primary-700 font-semibold hover:underline transition-colors disabled:opacity-50"
              >
                {mode === "login" ? "Sign Up" : "Sign In"}
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>
            By continuing, you agree to our{" "}
            <a href="#" className="text-primary-600 hover:underline">Terms of Service</a>{" "}
            and{" "}
            <a href="#" className="text-primary-600 hover:underline">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;


