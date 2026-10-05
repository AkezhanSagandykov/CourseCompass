import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";

function ScoreCell({ score, count }) {
  if (!count) return <span className="score score-none">No reviews</span>;
  return (
    <span className="score">
      <strong>{score.toFixed(1)}</strong>
      <small>{count} {count === 1 ? "review" : "reviews"}</small>
    </span>
  );
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [faculty, setFaculty] = useState("");
  const [ordering, setOrdering] = useState("name");
  const [faculties, setFaculties] = useState([]);
  const [professors, setProfessors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/professors/faculties/").then(setFaculties).catch(() => setFaculties([]));
  }, []);

  // Search waits 300 ms after the last keystroke, so we do not call the API on every letter
  useEffect(() => {
    const params = new URLSearchParams({ ordering });
    if (query.trim()) params.set("search", query.trim());
    if (faculty) params.set("faculty", faculty);

    setLoading(true);
    const timer = setTimeout(() => {
      api(`/professors/?${params}`)
        .then((data) => {
          setProfessors(data.results);
          setError("");
        })
        .catch((apiError) => setError(apiError.message))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [query, faculty, ordering]);

  return (
    <>
      <section className="hero">
        <h1>Who will teach your next course?</h1>
        <p>Ratings and comments from KBTU students who already studied with them.</p>
        <input
          type="search"
          className="search-input"
          placeholder="Professor name"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          aria-label="Search professors"
        />
      </section>

      <div className="toolbar">
        <select value={faculty} onChange={(event) => setFaculty(event.target.value)} aria-label="Faculty">
          <option value="">All faculties</option>
          {faculties.map((code) => (
            <option key={code} value={code}>{code}</option>
          ))}
        </select>
        <select value={ordering} onChange={(event) => setOrdering(event.target.value)} aria-label="Sort by">
          <option value="name">Sort by name</option>
          <option value="rating">Highest rating first</option>
          <option value="reviews">Most reviews first</option>
        </select>
      </div>

      {error && <p className="error" role="alert">{error}</p>}
      {!error && !loading && professors.length === 0 && (
        <p className="notice">No professor with that name. Try part of the surname.</p>
      )}

      <ul className={`results${loading ? " is-loading" : ""}`}>
        {professors.map((professor) => (
          <li key={professor.id}>
            <Link to={`/professors/${professor.id}`} className="result">
              <span className="result-main">
                <span className="result-title">{professor.full_name}</span>
                <span className="result-meta">{professor.faculty}</span>
              </span>
              <ScoreCell score={professor.average_rating} count={professor.review_count} />
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}
