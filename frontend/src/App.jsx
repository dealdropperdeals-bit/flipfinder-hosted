import { useEffect, useMemo, useState } from "react";
import ListingCard from "./components/ListingCard";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function App() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [priceMax, setPriceMax] = useState(10000);
  const [maxJunkScore, setMaxJunkScore] = useState(45);
  const [bucket, setBucket] = useState("best");

  const queryString = useMemo(() => {
    const params = new URLSearchParams();
    params.set("max_price", String(priceMax));
    params.set("max_junk_score", String(maxJunkScore));
    params.set("hide_stale", "true");
    if (bucket) params.set("bucket", bucket);
    return params.toString();
  }, [priceMax, maxJunkScore, bucket]);

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/listings?${queryString}`, { signal: controller.signal });
        const data = await res.json();
        setListings(Array.isArray(data) ? data : []);
      } catch (error) {
        if (error.name !== "AbortError") console.error(error);
      } finally {
        setLoading(false);
      }
    }
    load();
    return () => controller.abort();
  }, [queryString]);

  return (
    <div className="page-shell">
      <header className="topbar">
        <div>
          <div className="brand">FlipFinder</div>
          <div className="subbrand">Hosted beta starter</div>
        </div>
        <div className="status-dot">{loading ? "Loading..." : `${listings.length} results`}</div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <h1>Find real underpriced cars, not obvious bait.</h1>
          <p>This starter is wired for a hosted backend and a shared collector. It is intentionally lean so you can get to a real beta fast.</p>
        </div>

        <div className="panel">
          <div className="filters">
            <label>
              <span>Max price</span>
              <input type="range" min="1000" max="15000" step="500" value={priceMax} onChange={(e) => setPriceMax(Number(e.target.value))} />
              <strong>${priceMax.toLocaleString()}</strong>
            </label>

            <label>
              <span>Max suspicion</span>
              <input type="range" min="0" max="100" step="5" value={maxJunkScore} onChange={(e) => setMaxJunkScore(Number(e.target.value))} />
              <strong>{maxJunkScore}</strong>
            </label>

            <label>
              <span>Bucket</span>
              <select value={bucket} onChange={(e) => setBucket(e.target.value)}>
                <option value="best">Best opportunities</option>
                <option value="review">Needs review</option>
                <option value="junk">Likely junk</option>
              </select>
            </label>
          </div>
        </div>
      </section>

      <main className="grid">
        {listings.map((listing) => <ListingCard key={listing.id} listing={listing} />)}
      </main>
    </div>
  );
}
