import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Vehicles from "./pages/Vehicles";
import Logs from "./pages/Logs";
import Reports from "./pages/Reports";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: "1rem", padding: "1rem", background: "#222", color: "#fff" }}>
        <Link to="/">Dashboard</Link>
        <Link to="/vehicles">Vehicles</Link>
        <Link to="/logs">Logs</Link>
        <Link to="/reports">Reports</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/vehicles" element={<Vehicles />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </BrowserRouter>
  );
}
