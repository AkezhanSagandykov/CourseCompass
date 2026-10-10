function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
}

export default function ReviewList({ reviews }) {
  if (reviews.length === 0) return null;

  return (
    <ul className="review-list">
      {reviews.map((review) => (
        <li key={review.id} className="review">
          <div className="review-head">
            <span className="review-rating">
              <strong>{review.rating}</strong> / 5
            </span>
            <span className="badge">{review.course.code} {review.course.title}</span>
            <span className="review-date">{formatDate(review.created_at)}</span>
          </div>
          {review.comment && <p className="review-comment">{review.comment}</p>}
        </li>
      ))}
    </ul>
  );
}
