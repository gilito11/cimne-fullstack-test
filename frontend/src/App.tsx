import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { MainPage } from "./pages/MainPage";
import { UsersPage } from "./pages/UsersPage";
import { BuildingsPage } from "./pages/BuildingsPage";

export function App() {
  const { user, logout } = useAuth();

  return (
    <div className="layout">
      <nav className="nav">
        <strong>CIMNE</strong>
        {user && (
          <>
            <NavLink to="/" end>Home</NavLink>
            <NavLink to="/users">Users</NavLink>
            <NavLink to="/buildings">Buildings</NavLink>
          </>
        )}
        <span className="spacer" />
        {user ? (
          <>
            <span style={{ fontSize: "0.85rem", color: "#cbd5e1" }}>
              {user.username} · {user.role}
            </span>
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <>
            <NavLink to="/login">Login</NavLink>
            <NavLink to="/register">Register</NavLink>
          </>
        )}
      </nav>

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={<ProtectedRoute><MainPage /></ProtectedRoute>} />
        <Route path="/users" element={<ProtectedRoute><UsersPage /></ProtectedRoute>} />
        <Route path="/buildings" element={<ProtectedRoute><BuildingsPage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
