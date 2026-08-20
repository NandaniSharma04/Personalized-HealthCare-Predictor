import React from "react";
import { useAuth } from "../context/AuthContext";
import UserDashboard from "../dashboards/user/UserDashboard";
import AdminDashboard from "../dashboards/admin/AdminDashboard";

export default function Dashboard({ defaultTab = "dashboard" }) {
  const { user } = useAuth();
  const role = user?.role?.toLowerCase() || "user";

  if (role === "admin") {
    return <AdminDashboard />;
  }

  return <UserDashboard initialTab={defaultTab} />;
}
