import { Link, NavLink } from "react-router-dom";
import { ShieldCheck, Menu, X, ChevronRight } from "lucide-react";
import { useState, type PropsWithChildren } from "react";

const navItems = [
  { label: "Analyze", href: "/" },
  { label: "History", href: "/history" },
  { label: "Documents", href: "/documents" },
];

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-blue-600" />
            <span className="text-xl font-bold text-navy-900 tracking-tight">ClauseClear</span>
          </div>

          <div className="hidden md:flex items-center gap-6">
            {navItems.map((item) => (
              <NavLink
                key={item.label}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "text-sm font-medium transition-colors",
                    isActive
                      ? "text-blue-600"
                      : "text-gray-600 hover:text-blue-600",
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <Link to="/" className="px-3.5 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
              New Analysis
            </Link>
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden p-2 text-gray-600 hover:text-blue-600"
              aria-label="Open menu"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile drawer backdrop */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
      )}
      {/* Mobile drawer panel */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-gray-200 transform transition-transform duration-300",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <span className="font-bold text-navy-900">ClauseClear</span>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="p-2 text-gray-600 hover:text-gray-900"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.label}
              to={item.href}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors border-r-2",
                  isActive
                    ? "border-blue-600 bg-blue-50 text-blue-600"
                    : "border-transparent text-gray-600 hover:bg-gray-50 hover:text-blue-600",
                )
              }
            >
              <ChevronRight className="w-4 h-4 text-gray-400" />
              {item.label}
            </NavLink>
          ))}
        </div>
        <div className="p-4 border-t border-gray-200">
          <Link to="/" className="w-full px-4 py-3 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors text-center">
            New Analysis
          </Link>
        </div>
      </div>
    </nav>
  );
}

export function Layout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}
