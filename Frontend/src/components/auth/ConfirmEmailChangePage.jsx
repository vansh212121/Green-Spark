import React, { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useDispatch } from "react-redux";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import { useConfirmEmailChangeMutation } from "@/features/api/authApi";

// Re-using our smart error handler
const getApiErrorMessage = (err, defaultMessage) => {
  if (err.data?.detail && Array.isArray(err.data.detail)) {
    const firstError = err.data.detail[0];
    const fieldName = firstError.loc.slice(-1)[0];
    return `${fieldName}: ${firstError.msg}`;
  }
  if (err.data?.error?.message) {
    return err.data.error.message;
  }
  return defaultMessage;
};

const ConfirmEmailChangePage = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const dispatch = useDispatch();

  const [confirmEmailChange] = useConfirmEmailChangeMutation();
  const [status, setStatus] = useState("verifying"); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState(
    "Confirming your new email address..."
  );

  useEffect(() => {
    // This effect runs only once when the page loads.
    if (!token) {
      setStatus("error");
      setMessage("Invalid request. No confirmation token found in the link.");
      return;
    }

    const performConfirmation = async () => {
      try {
        const response = await confirmEmailChange(token).unwrap();
        // onQueryStarted in the API slice handles logging the user out.
        setStatus("success");
        setMessage(
          response.message || "Your email has been successfully updated!"
        );
      } catch (err) {
        // onQueryStarted will also log the user out on failure.
        setStatus("error");
        setMessage(
          getApiErrorMessage(
            err,
            "Confirmation failed. The link may be invalid or expired."
          )
        );
      }
    };

    performConfirmation();
  }, [token, confirmEmailChange, dispatch]);

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
              {status === "verifying" && "Confirmation in Progress"}
              {status === "success" && "Confirmation Complete"}
              {status === "error" && "Confirmation Failed"}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-6">
            <p className="text-gray-600">{message}</p>
            {status === "success" && (
              <p className="text-sm text-muted-foreground">
                For your security, you have been logged out. Please sign in with
                your new email address.
              </p>
            )}
            <Button asChild className="w-full">
              <Link to="/auth">Proceed to Login</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ConfirmEmailChangePage;
