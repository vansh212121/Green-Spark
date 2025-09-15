import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  User,
  Mail,
  Lock,
  HelpCircle,
  UserX,
  Trash2,
  Save,
  Loader2,
} from "lucide-react";

import {
  useChangeMyPasswordMutation,
  useDeactivateMyAccountMutation,
  useGetMeQuery,
  useUpdateMyProfileMutation,
} from "@/features/api/userApi";
import { toast } from "sonner";
import { useRequestEmailChangeMutation } from "@/features/api/authApi";

// Helper function to parse complex API errors
const getApiErrorMessage = (err, defaultMessage) => {
  // Check for FastAPI's 422 validation error format
  if (err.data?.detail && Array.isArray(err.data.detail)) {
    const firstError = err.data.detail[0];
    const fieldName = firstError.loc.slice(-1)[0];
    return `${fieldName}: ${firstError.msg}`;
  }
  // Check for our custom error format (e.g., 401, 400)
  if (err.data?.error?.message) {
    return err.data.error.message;
  }
  // Fallback for any other error
  return defaultMessage;
};

const Settings = () => {
  const { data: currentUser, isLoading: isLoadingUser } = useGetMeQuery();

  // --- State Management ---
  const [profileData, setProfileData] = useState({
    first_name: "",
    last_name: "",
    username: "",
  });

  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const [emailData, setEmailData] = useState({
    new_email: "",
    confirm_email: "",
  });

  const [updateMyProfile, { isLoading: isUpdatingProfile }] =
    useUpdateMyProfileMutation();
  const [changeMyPassword, { isLoading: isChangingPassword }] =
    useChangeMyPasswordMutation();
  const [deactivateMyAccount, { isLoading: isDeactivating }] =
    useDeactivateMyAccountMutation();
  const [requestEmailChange, { isLoading: isChangingEmail }] =
    useRequestEmailChangeMutation();

  // Effect to populate the form once the user data is fetched
  useEffect(() => {
    if (currentUser) {
      setProfileData({
        first_name: currentUser.first_name || "",
        last_name: currentUser.last_name || "",
        username: currentUser.username || "",
      });
    }
  }, [currentUser]);

  // --- Handlers ---
  const handleProfileInputChange = (e) => {
    setProfileData({ ...profileData, [e.target.id]: e.target.value });
  };
  const handlePasswordInputChange = (e) =>
    setPasswordData({ ...passwordData, [e.target.id]: e.target.value });
  const handleEmailInputChange = (e) =>
    setEmailData({ ...emailData, [e.target.id]: e.target.value });

  const handleDeactivateAccount = async () => {
    try {
      await deactivateMyAccount().unwrap();
      toast.success("Account deactivated successfully.");
      setShowDeactivateModal(false);
      // The mutation already logs the user out via onQueryStarted
    } catch (err) {
      console.error("Deactivation failed:", err);
      toast.error("Failed to deactivate account. Logging out locally.");
      dispatch(userLoggedOut());
      setShowDeactivateModal(false);
    }
  };

  // Profile Update
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    const changedData = Object.keys(profileData).reduce((acc, key) => {
      if (profileData[key] !== currentUser[key]) acc[key] = profileData[key];
      return acc;
    }, {});

    if (Object.keys(changedData).length === 0) {
      toast.info("No profile changes to save.");
      return;
    }

    toast.promise(updateMyProfile(changedData).unwrap(), {
      loading: "Updating your profile...",
      success: "Profile updated successfully!",
      error: (err) => getApiErrorMessage(err, "Failed to update profile."),
    });
  };
  // Password Update
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error("New passwords do not match.");
      return;
    }

    const promise = changeMyPassword({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password,
    }).unwrap();

    toast.promise(promise, {
      loading: "Changing your password...",
      success: () => {
        setPasswordData({
          current_password: "",
          new_password: "",
          confirm_password: "",
        });
        return "Password changed successfully!";
      },
      error: (err) => getApiErrorMessage(err, "Failed to change password."),
    });
  };
  // Email Change Handler
  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    if (emailData.new_email !== emailData.confirm_email) {
      toast.error("New emails do not match.");
      return;
    }

    const promise = requestEmailChange({
      new_email: emailData.new_email,
    }).unwrap();

    toast.promise(promise, {
      loading: "Sending verification link...",
      success: (data) => {
        setEmailData({ new_email: "", confirm_email: "" }); // Reset form on success
        return (
          data.message || "Verification link sent to your new email address."
        );
      },
      error: (err) =>
        getApiErrorMessage(err, "Failed to request email change."),
    });
  };

  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleDeleteAccount = () => {
    // Handle delete account logic here
    console.log("Account deleted");
    setShowDeleteModal(false);
  };

  // --- Loading State ---
  if (isLoadingUser) {
    return (
      <div className="p-8 flex justify-center items-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="p-8 animate-fade-in">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">
          Manage your account preferences and application settings
        </p>
      </header>

      <div className="space-y-8">
        {/* Profile Settings */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <User className="w-5 h-5 text-primary-500" />
            <h3 className="text-xl font-semibold text-gray-900">
              Profile Settings
            </h3>
          </div>
          <form onSubmit={handleProfileSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  value={profileData.first_name}
                  onChange={handleProfileInputChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  value={profileData.last_name}
                  onChange={handleProfileInputChange}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  value={profileData.username}
                  onChange={handleProfileInputChange}
                />
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <Button
                type="submit"
                className="bg-primary-500 hover:bg-primary-600"
                disabled={isUpdatingProfile}
              >
                {isUpdatingProfile ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Save Profile
                  </>
                )}
              </Button>
            </div>
          </form>
        </Card>

        {/* Change Email */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <Mail className="w-5 h-5 text-primary-500" />
            <h3 className="text-xl font-semibold text-gray-900">
              Change Email
            </h3>
          </div>
          <form onSubmit={handleEmailSubmit}>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="currentEmail">Current Email</Label>
                <Input
                  id="currentEmail"
                  value={currentUser?.email || ""}
                  disabled
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new_email">New Email</Label>
                <Input
                  id="new_email"
                  type="email"
                  placeholder="Enter new email address"
                  value={emailData.new_email}
                  onChange={handleEmailInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_email">Confirm New Email</Label>
                <Input
                  id="confirm_email"
                  type="email"
                  placeholder="Confirm new email address"
                  value={emailData.confirm_email}
                  onChange={handleEmailInputChange}
                  required
                />
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <Button
                type="submit"
                className="bg-primary-500 hover:bg-primary-600"
                disabled={isChangingEmail}
              >
                {isChangingEmail ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Sending Link...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Update Email
                  </>
                )}
              </Button>
            </div>
          </form>
        </Card>

        {/* Change Password */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <Lock className="w-5 h-5 text-primary-500" />
            <h3 className="text-xl font-semibold text-gray-900">
              Change Password
            </h3>
          </div>
          <form onSubmit={handlePasswordSubmit}>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current_password">Current Password</Label>
                <Input
                  id="current_password"
                  type="password"
                  placeholder="Enter current password"
                  value={passwordData.current_password}
                  onChange={handlePasswordInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new_password">New Password</Label>
                <Input
                  id="new_password"
                  type="password"
                  placeholder="Enter new password"
                  value={passwordData.new_password}
                  onChange={handlePasswordInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirm New Password</Label>
                <Input
                  id="confirm_password"
                  type="password"
                  placeholder="Confirm new password"
                  value={passwordData.confirm_password}
                  onChange={handlePasswordInputChange}
                  required
                />
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <Button
                type="submit"
                className="bg-primary-500 hover:bg-primary-600"
                disabled={isChangingPassword}
              >
                {isChangingPassword ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Changing...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Change Password
                  </>
                )}
              </Button>
            </div>
          </form>
        </Card>

        {/* Help & Support */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <HelpCircle className="w-5 h-5 text-primary-500" />
            <h3 className="text-xl font-semibold text-gray-900">
              Help & Support
            </h3>
          </div>
          <div className="space-y-4">
            <Button variant="outline" className="w-full justify-start">
              📋 User Guide & FAQ
            </Button>
            <Button variant="outline" className="w-full justify-start">
              💬 Contact Support
            </Button>
            <Button variant="outline" className="w-full justify-start">
              🔒 Privacy Policy
            </Button>
            <Button variant="outline" className="w-full justify-start">
              📄 Terms of Service
            </Button>
          </div>
          <div className="flex justify-end mt-6"></div>
        </Card>

        {/* Account Actions */}
        <Card className="p-6 border-red-200">
          <div className="space-y-4">
            <div className="mb-4">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Account Actions
              </h3>
              <p className="text-gray-600 text-sm">
                These actions will affect your account permanently
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                variant="outline"
                className="border-orange-300 text-orange-600 hover:bg-orange-50"
                onClick={() => setShowDeactivateModal(true)}
              >
                <UserX className="w-4 h-4 mr-2" />
                Deactivate Account
              </Button>

              <Button
                variant="outline"
                className="border-red-300 text-red-600 hover:bg-red-50"
                onClick={() => setShowDeleteModal(true)}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Account
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Deactivate Account Modal */}
      <AlertDialog
        open={showDeactivateModal}
        onOpenChange={setShowDeactivateModal}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Deactivate Account</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to deactivate your account? This will:
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Hide your profile from other users</li>
                <li>Disable your login access temporarily</li>
                <li>Preserve your data for future reactivation</li>
                <li>Allow you to reactivate anytime by contacting support</li>
              </ul>
              <p className="mt-3 text-sm">
                You can reactivate your account later if you change your mind.
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-orange-600 hover:bg-orange-700"
              onClick={handleDeactivateAccount}
              disabled={isDeactivating}
            >
              {isDeactivating ? "Deactivating..." : "Deactivate Account"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Account Modal */}
      <AlertDialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Account</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to permanently delete your account? This
              will:
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Permanently delete all your data</li>
                <li>Remove your profile completely</li>
                <li>Cancel any active subscriptions</li>
                <li>Cannot be undone or recovered</li>
              </ul>
              <p className="mt-3 text-sm font-semibold text-red-600">
                This action is irreversible. All your data will be lost forever.
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-600 hover:bg-red-700"
              onClick={handleDeleteAccount}
            >
              Delete Account
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Settings;
