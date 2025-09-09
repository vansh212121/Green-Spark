import { Link, NavLink, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import {
  BarChart3,
  FileText,
  Lightbulb,
  Settings,
  Zap,
  User,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { selectCurrentUser, selectRefreshToken } from "@/features/authSlice";
import { useLogoutMutation } from "@/features/api/authApi";

const navigation = [
  { name: "Overview", href: "/", icon: BarChart3 },
  { name: "Bills & Data", href: "/bills", icon: FileText },
  { name: "Appliance Insights", href: "/appliances", icon: Zap },
  { name: "Smart Insights", href: "/insights", icon: Lightbulb },
  { name: "Settings", href: "/settings", icon: Settings },
];

const getInitials = (firstName, lastName) => {
  return `${firstName?.[0] || ""}${lastName?.[0] || ""}`.toUpperCase();
};

export const Sidebar = () => {
  const currentUser = useSelector(selectCurrentUser);
  const refreshToken = useSelector(selectRefreshToken);
  const [logout] = useLogoutMutation();
  const navigate = useNavigate();

  const handleLogout = () => {
    if (refreshToken) {
      // THE REFINEMENT: Using toast.promise for cleaner UX feedback.
      const promise = logout({ refresh_token: refreshToken }).unwrap();

      toast.promise(promise, {
        loading: "Signing out...",
        success: () => {
          // This function is called after the API succeeds and onQueryStarted cleans up state.
          // We can now safely navigate the user away.
          navigate("/auth"); // Redirect to login page on successful logout
          return "You have been signed out successfully!";
        },
        error: () => {
          // This is called if the API call fails. onQueryStarted still cleans up state.
          navigate("/auth"); // Still redirect, as the user is logged out locally
          return "Logout failed on the server, but you are now signed out.";
        },
      });
    }
  };

  return (
    <aside className="fixed inset-y-0 left-0 w-72 bg-white shadow-sm border-r border-gray-200">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center gap-3 p-6 pb-8">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-semibold text-gray-900">GreenSpark</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-6 space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              end={item.href === "/"}
              className={({ isActive }) =>
                cn(
                  "group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                  isActive
                    ? "bg-primary-50 text-primary-700 border border-primary-100"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                )
              }
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5",
                  "group-[.active]:text-primary-600"
                )}
              />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* User Profile Section */}
        <div className="p-6 border-t border-gray-200">
          {currentUser ? (
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-700">
                    {getInitials(currentUser.first_name, currentUser.last_name)}
                  </span>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900 truncate">{`${currentUser.first_name} ${currentUser.last_name}`}</p>
                  <p className="text-xs text-gray-500 truncate">
                    {currentUser.email}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start text-gray-600 hover:text-gray-900"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign Out
              </Button>
            </div>
          ) : (
            <Link to="/auth">
              <Button className="w-full bg-primary-500 hover:bg-primary-600">
                <User className="w-4 h-4 mr-2" />
                Sign In or Sign Up
              </Button>
            </Link>
          )}
        </div>
      </div>
    </aside>
  );
};
