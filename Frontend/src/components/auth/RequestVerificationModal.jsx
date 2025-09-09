import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Mail } from "lucide-react";
import { toast } from "sonner";
import { useRequestVerificationEmailMutation } from "@/features/api/authApi";

export const RequestVerificationModal = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState("");
  const [requestVerificationEmail, { isLoading }] =
    useRequestVerificationEmailMutation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await requestVerificationEmail({ email }).unwrap();
      // Show the backend's generic success message, which is returned on both success and failure for security.
      toast.success("Request Sent", {
        description:
          "If an account with that email needs verification, a new link has been sent.",
      });
      onClose();
    } catch (err) {
      // This will catch specific errors, like "account already verified".
      const errorMessage =
        err?.data?.error?.message || "An unexpected error occurred.";
      toast.error("Request Failed", {
        description: errorMessage,
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Resend Verification Email</DialogTitle>
          <DialogDescription>
            Enter your email address to receive a new verification link.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="email-verification">Email Address</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="email-verification"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Sending..." : "Send Link"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
