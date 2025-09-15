import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import { useVerifyEmailMutation } from "@/features/api/authApi";

const VerifyEmailPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");

  const [verifyEmail, { isLoading }] = useVerifyEmailMutation();
  const [status, setStatus] = useState("verifying"); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState(
    "Verifying your account, please wait..."
  );

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Invalid verification link. No token found.");
      return;
    }

    const performVerification = async () => {
      try {
        const response = await verifyEmail(token).unwrap();
        setStatus("success");
        setMessage(
          response.message || "Your email has been successfully verified!"
        );
      } catch (err) {
        setStatus("error");
        setMessage(
          err?.data?.error?.message ||
            "Verification failed. The link may be invalid or expired."
        );
      }
    };

    performVerification();
  }, [token, verifyEmail]);

  const StatusDisplay = () => {
    switch (status) {
      case "verifying":
        return <Loader2 className="h-12 w-12 text-primary-500 animate-spin" />;
      case "success":
        return <CheckCircle className="h-12 w-12 text-green-500" />;
      case "error":
        return <XCircle className="h-12 w-12 text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-lg border-gray-200">
          <CardHeader className="text-center pb-4">
            <div className="flex justify-center mb-4">
              <StatusDisplay />
            </div>
            <CardTitle className="text-2xl font-bold">
              {status === "verifying" && "Verification in Progress"}
              {status === "success" && "Verification Complete"}
              {status === "error" && "Verification Failed"}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-6">
            <p className="text-gray-600">{message}</p>
            <Button asChild className="w-full">
              <Link to="/auth">Proceed to Login</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VerifyEmailPage;
