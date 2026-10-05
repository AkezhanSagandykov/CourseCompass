import { useEffect, useState } from "react";
import { api } from "../api.js";

const MAX_COMMENT = 500;

export default function ReviewForm({ professorId, onSaved }) {
  const [courses, setCourses] = useState([]);
  const [course, setCourse] = useState("");
  const [rating, setRating] = useState(null);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api("/courses/")
      .then((data) => {
        setCourses(data);
        setCourse(data[0]?.id ?? "");
      })
      .catch((apiError) => setError(apiError.message));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    if (rating === null) {
      setError("Choose a rating from 1 to 5.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const data = await api("/reviews/", {
        method: "POST",
        body: { professor: Number(professorId), course: Number(course), rating, comment },
      });
      onSaved(data.detail);
    } catch (apiError) {
      setError(apiError.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="review-form" onSubmit={handleSubmit}>
      <h2>Rate this professor</h2>
      <p className="form-note">
        Your review is anonymous. It appears on the site after a moderator approves it.
      </p>

      <label>
        Course you took with this professor
        <select value={course} onChange={(event) => setCourse(event.target.value)}>
          {courses.map((item) => (
            <option key={item.id} value={item.id}>{item.code} {item.title}</option>
          ))}
        </select>
      </label>

      <fieldset className="rating-field">
        <legend>Rating <small>1 is poor, 5 is excellent</small></legend>
        <div className="rating-options">
          {[1, 2, 3, 4, 5].map((value) => (
            <label key={value} className={rating === value ? "selected" : ""}>
              <input type="radio" name="rating" value={value} checked={rating === value} onChange={() => setRating(value)} />
              {value}
            </label>
          ))}
        </div>
      </fieldset>

      <label className="comment-field">
        Comment (optional)
        <textarea
          rows={4}
          maxLength={MAX_COMMENT}
          value={comment}
          placeholder="What should the next student know about this professor?"
          onChange={(event) => setComment(event.target.value)}
        />
        <span className="counter">{comment.length} / {MAX_COMMENT}</span>
      </label>

      {error && <p className="error" role="alert">{error}</p>}
      <button type="submit" className="button-primary" disabled={saving}>
        {saving ? "Sending…" : "Send review"}
      </button>
    </form>
  );
}
