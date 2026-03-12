import { Link, Outlet, useLocation } from "react-router-dom";

export default function Layout() {
  const location = useLocation();

  return (
    <div style={pageStyle}>
      <aside style={sidebarStyle}>
        <h2 style={logoStyle}>Wallet Privacy</h2>

        <nav style={navStyle}>
          <NavItem to="/" label="Dashboard" active={location.pathname === "/"} />
          <NavItem
            to="/sessions"
            label="Sessions"
            active={location.pathname.startsWith("/sessions")}
          />
        </nav>
      </aside>

      <main style={contentStyle}>
        <Outlet />
      </main>
    </div>
  );
}

function NavItem({
  to,
  label,
  active,
}: {
  to: string;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      to={to}
      style={{
        ...navItemStyle,
        background: active ? "#2563eb" : "transparent",
        color: active ? "#fff" : "#d1d5db",
      }}
    >
      {label}
    </Link>
  );
}

const pageStyle: React.CSSProperties = {
  display: "flex",
  minHeight: "100vh",
  background: "#111827",
};

const sidebarStyle: React.CSSProperties = {
  width: "240px",
  background: "#0f172a",
  borderRight: "1px solid #1f2937",
  padding: "24px 16px",
};

const logoStyle: React.CSSProperties = {
  color: "#fff",
  fontSize: "24px",
  fontWeight: 700,
  marginBottom: "32px",
};

const navStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "10px",
};

const navItemStyle: React.CSSProperties = {
  padding: "12px 16px",
  borderRadius: "10px",
  textDecoration: "none",
  fontWeight: 600,
};

const contentStyle: React.CSSProperties = {
  flex: 1,
};