import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import RatingSummary from "../components/RatingSummary.jsx";
import ReviewForm from "../components/ReviewForm.jsx";
import ReviewList from "../components/ReviewList.jsx";

export default function ProfessorPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [professor, setProfessor] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState("");
  const [savedMessage, setSavedMessage] = useState("");

  useEffect(() => {
    Promise.all([api(`/professors/${id}/`), api(`/professors/${id}/reviews/`)])
      .then(([professorData, reviewData]) => {
        setProfessor(professorData);
        setReviews(reviewData.results);
      })
      .catch((apiError) => setError(apiError.status === 404 ? "This professor is not in the list." : apiError.message));
  }, [id]);

  if (error) return <p className="error" role="alert">{error}</p>;
  if (!professor) return <p className="notice">Loading…</p>;

  return (
    <article className="detail">
      <header className="detail-head">
        <p className="detail-code">{professor.faculty}</p>
        <h1>{professor.full_name}</h1>
      </header>

      <RatingSummary professor={professor} />

      {reviews.length > 0 && (
        <section className="detail-reviews">
          <h2>What students say</h2>
          <ReviewList reviews={reviews} />
        </section>
      )}

      <section className="detail-form">
        {savedMessage ? (
          <p className="success">{savedMessage}</p>
        ) : user ? (
          <ReviewForm professorId={id} onSaved={setSavedMessage} />
        ) : (
          <p className="notice">
            <Link to="/login">Log in</Link> with your KBTU email to rate this professor.
          </p>
        )}
      </section>
    </article>
  );
}
