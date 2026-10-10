import { createContext, useContext, useEffect, useState } from "react";
import { api, tokenStorage } from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(Boolean(tokenStorage.get()));

  // Restore the session after a page reload
  useEffect(() => {
    if (!tokenStorage.get()) return;
    api("/auth/me/")
      .then(setUser)
      .catch(() => tokenStorage.clear())
      .finally(() => setChecking(false));
  }, []);

  async function login(email, password) {
    const data = await api("/auth/login/", { method: "POST", body: { email, password } });
    tokenStorage.set(data.token);
    setUser(data.user);
  }

  async function logout() {
    try {
      await api("/auth/logout/", { method: "POST" });
    } finally {
      tokenStorage.clear();
      setUser(null);
    }
  }

  return <AuthContext.Provider value={{ user, checking, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
