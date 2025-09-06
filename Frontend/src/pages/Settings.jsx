import React, { useState } from "react";
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
} from "lucide-react";

const Settings = () => {
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleDeactivateAccount = () => {
    // Handle deactivate account logic here
    console.log("Account deactivated");
    setShowDeactivateModal(false);
  };

  const handleDeleteAccount = () => {
    // Handle delete account logic here
    console.log("Account deleted");
    setShowDeleteModal(false);
  };

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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="firstName">First Name</Label>
              <Input id="firstName" defaultValue="John" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">Last Name</Label>
              <Input id="lastName" defaultValue="Doe" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input id="username" defaultValue="johndoe123" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input id="location" defaultValue="Mumbai, Maharashtra" />
            </div>
          </div>
          <div className="flex justify-end mt-6">
            <Button className="bg-primary-500 hover:bg-primary-600">
              <Save className="w-4 h-4 mr-2" />
              Save Profile
            </Button>
          </div>
        </Card>

        {/* Change Email */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <Mail className="w-5 h-5 text-primary-500" />
            <h3 className="text-xl font-semibold text-gray-900">
              Change Email
            </h3>
          </div>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="currentEmail">Current Email</Label>
              <Input
                id="currentEmail"
                defaultValue="john@example.com"
                disabled
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="newEmail">New Email</Label>
              <Input id="newEmail" placeholder="Enter new email address" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmEmail">Confirm New Email</Label>
              <Input
                id="confirmEmail"
                placeholder="Confirm new email address"
              />
            </div>
          </div>
          <div className="flex justify-end mt-6">
            <Button className="bg-primary-500 hover:bg-primary-600">
              <Save className="w-4 h-4 mr-2" />
              Update Email
            </Button>
          </div>
        </Card>

        {/* Change Password */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <Lock className="w-5 h-5 text-primary-500" />
            <h3 className="text-xl font-semibold text-gray-900">
              Change Password
            </h3>
          </div>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="currentPassword">Current Password</Label>
              <Input
                id="currentPassword"
                type="password"
                placeholder="Enter current password"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="newPassword">New Password</Label>
              <Input
                id="newPassword"
                type="password"
                placeholder="Enter new password"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm new password"
              />
            </div>
          </div>
          <div className="flex justify-end mt-6">
            <Button className="bg-primary-500 hover:bg-primary-600">
              <Save className="w-4 h-4 mr-2" />
              Change Password
            </Button>
          </div>
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
            >
              Deactivate Account
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
