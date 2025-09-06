import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";

export const Layout = () => {
  return (
    <div className="min-h-screen bg-background w-full">
      <div className="flex w-full">
        <Sidebar />
        <main className="flex-1 ml-72">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
