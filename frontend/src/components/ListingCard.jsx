export default function ListingCard({ listing }) {
  const bucket = listing.junk_score <= 20 ? "Strong candidate" : listing.junk_score <= 45 ? "Review carefully" : "Likely junk";
  const badgeClass = listing.junk_score <= 20 ? "badge best" : listing.junk_score <= 45 ? "badge review" : "badge junk";
  return (
    <article className="card">
      <div className="thumb-wrap">
        <img className="thumb" src={listing.thumb_url || listing.image_url || "https://placehold.co/640x420?text=No+Image"} alt={listing.title || "Listing image"} />
      </div>
      <div className="card-body">
        <div className="card-top">
          <span className={badgeClass}>{bucket}</span>
          <span className="score">Score {listing.junk_score ?? 0}</span>
        </div>
        <div className="price">${listing.price?.toLocaleString?.() ?? listing.price ?? "N/A"}</div>
        <div className="title">{listing.title || "Untitled listing"}</div>
        <div className="meta">
          <span>{listing.year || "Year N/A"}</span><span>•</span>
          <span>{listing.mileage ? `${listing.mileage.toLocaleString()} mi` : "Mileage N/A"}</span>
        </div>
        <div className="location">{listing.location || "Unknown location"}</div>
        {listing.junk_flags ? <div className="flags">{listing.junk_flags}</div> : null}
        <div className="actions">
          <a className="button primary" href={listing.url || "#"} target="_blank" rel="noreferrer">Open Listing</a>
          <button className="button secondary" type="button">Save</button>
        </div>
      </div>
    </article>
  );
}
