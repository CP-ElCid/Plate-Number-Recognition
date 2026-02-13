import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Vehicles from "./pages/Vehicles";
import Logs from "./pages/Logs";
import Reports from "./pages/Reports";
import type { JSX } from "react";
import Login from "./pages/Login";
import Layout from "./components/Layout";

function PrivateRoute({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem("token");
  return token ? <Layout>{children}</Layout> : <Navigate to="/login" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/vehicles" element={<PrivateRoute><Vehicles /></PrivateRoute>} />
        <Route path="/logs" element={<PrivateRoute><Logs /></PrivateRoute>} />
        <Route path="/reports" element={<PrivateRoute><Reports /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
