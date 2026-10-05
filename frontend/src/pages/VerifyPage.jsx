import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api.js";

export default function VerifyPage() {
  const [params] = useSearchParams();
  const [result, setResult] = useState({ ok: null, message: "Confirming your email…" });

  useEffect(() => {
    const token = params.get("token") || "";
    api(`/auth/verify/?token=${encodeURIComponent(token)}`)
      .then((data) => setResult({ ok: true, message: data.detail }))
      .catch((apiError) => setResult({ ok: false, message: apiError.message }));
  }, [params]);

  return (
    <div className="auth-form">
      <h1>Email confirmation</h1>
      <p className={result.ok === false ? "error" : ""}>{result.message}</p>
      {result.ok && <Link className="button-primary" to="/login">Log in</Link>}
    </div>
  );
}
