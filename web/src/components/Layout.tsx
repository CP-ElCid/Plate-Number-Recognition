import { Link, useLocation } from "react-router-dom";
import pcuLogo from "../img/pcu_logo.png";

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", path: "/" },
    { name: "Vehicles", path: "/vehicles" },
    { name: "Logs", path: "/logs" },
    { name: "Reports", path: "/reports" },
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Navigation Bar */}
      <nav className="bg-gray-800 shadow-lg">
        <div className="mx-auto px-6">
          <div className="flex items-center gap-6 py-4">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <img
                src={pcuLogo}
                alt="PCU Logo"
                className="w-12 h-12 max-w-12 max-h-12 object-contain"
              />
              <div className="flex flex-col">
                {/* <span className="text-white font-bold text-lg leading-tight">Plate Recognition</span>
                <span className="text-gray-400 text-xs">System</span> */}
              </div>
            </div>

            {/* Nav Links */}
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-lg font-medium transition-colors ${
                  location.pathname === item.path
                    ? "text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="mx-auto px-6 py-6">
        {children}
      </main>
    </div>
  );
}
