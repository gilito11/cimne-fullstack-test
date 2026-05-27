import { useAuth } from "../auth/AuthContext";

export function MainPage() {
  const { user } = useAuth();
  if (!user) return null;
  return (
    <div className="container">
      <div className="card">
        <h1>Welcome, {user.username}</h1>
        <p className="muted">You are signed in with role <strong>{user.role}</strong>.</p>
        <ul>
          <li><strong>Email:</strong> {user.email}</li>
          <li><strong>ID:</strong> <code>{user.id}</code></li>
        </ul>
        <p className="muted">
          Use the navigation above to manage users or view buildings on the map.
        </p>
      </div>
    </div>
  );
}
