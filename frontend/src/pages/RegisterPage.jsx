import { useState } from "react";
import { api } from "../api.js";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      const data = await api("/auth/register/", { method: "POST", body: { email, password } });
      setDone(data.detail);
    } catch (apiError) {
      setError(apiError.message);
    }
  }

  if (done) {
    return (
      <div className="auth-form">
        <h1>Almost there</h1>
        <p>{done}</p>
      </div>
    );
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h1>Sign up</h1>
      <p className="form-note">Only @kbtu.kz emails can join, so every review comes from a real student.</p>
      <label>
        KBTU email
        <input type="email" autoComplete="email" placeholder="name_surname@kbtu.kz" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
      <label>
        Password
        <input type="password" autoComplete="new-password" minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} required />
      </label>
      {error && <p className="error" role="alert">{error}</p>}
      <button type="submit" className="button-primary">Create account</button>
    </form>
  );
}
