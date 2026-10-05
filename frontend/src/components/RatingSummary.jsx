// Average rating plus how many students gave 5, 4, 3, 2 and 1.
export default function RatingSummary({ professor }) {
  const { average_rating: average, review_count: count, rating_distribution: distribution } = professor;

  if (!count) {
    return (
      <section className="scorecard scorecard-empty">
        <p>No approved reviews yet. If you studied with this professor, yours can be the first.</p>
      </section>
    );
  }

  return (
    <section className="scorecard" aria-label="Rating summary">
      <div className="overall">
        <span className="overall-number">{average.toFixed(1)}</span>
        <span className="overall-caption">
          out of 5, from {count} {count === 1 ? "review" : "reviews"}
        </span>
      </div>
      <dl className="bars">
        {[5, 4, 3, 2, 1].map((stars) => {
          const votes = distribution[String(stars)] ?? 0;
          return (
            <div className="bar-row bar-row-compact" key={stars}>
              <dt>{stars} out of 5</dt>
              <dd>
                <span className="bar-track">
                  <span className="bar-fill" style={{ width: `${(votes / count) * 100}%` }} />
                </span>
                <span className="bar-value">{votes}</span>
              </dd>
            </div>
          );
        })}
      </dl>
    </section>
  );
}
