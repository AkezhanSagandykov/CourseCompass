import { Link, NavLink, useNavigate } from "react-router-dom";
import { ADMIN_URL } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <header className="site-header">
      <Link to="/" className="wordmark">
        Course<span>Compass</span>
      </Link>
      <nav className="nav">
        <NavLink to="/" end>Find a professor</NavLink>
        {user?.is_staff && <a href={ADMIN_URL}>Moderate reviews</a>}
        {user ? (
          <>
            <span className="nav-user">{user.email}</span>
            <button type="button" className="link-button" onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <NavLink to="/login">Log in</NavLink>
            <NavLink to="/register" className="nav-cta">Sign up</NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
