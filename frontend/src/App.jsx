import { useEffect, useState } from "react";
import { createLink, listLinks, shortUrl } from "./api.js";

export default function App() {
  const [links, setLinks] = useState([]);
  const [targetUrl, setTargetUrl] = useState("");
  const [created, setCreated] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    try {
      setLinks(await listLinks());
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const link = await createLink(targetUrl.trim());
      setCreated(link);
      setTargetUrl("");
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header>
        <h1>URL Shortener</h1>
        <p className="muted">Paste a long link and get a short one.</p>
      </header>

      <form className="shorten-form" onSubmit={handleSubmit}>
        <input
          type="url"
          placeholder="https://example.com/a/very/long/link"
          value={targetUrl}
          onChange={(event) => setTargetUrl(event.target.value)}
          aria-label="Long URL"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Shortening…" : "Shorten"}
        </button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}
      {created && <CreatedLink link={created} />}

      <section>
        <div className="section-header">
          <h2>Recent links</h2>
          <button type="button" className="secondary" onClick={refresh}>
            Refresh
          </button>
        </div>
        <LinkTable links={links} />
      </section>
    </main>
  );
}

function CreatedLink({ link }) {
  const url = shortUrl(link.code);
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="created">
      <a href={url} target="_blank" rel="noreferrer">
        {url}
      </a>
      <button type="button" className="secondary" onClick={copy}>
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}

function LinkTable({ links }) {
  if (links.length === 0) {
    return <p className="muted">No links yet.</p>;
  }
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Short link</th>
            <th>Target</th>
            <th className="num">Clicks</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {links.map((link) => (
            <tr key={link.code}>
              <td>
                <a href={shortUrl(link.code)} target="_blank" rel="noreferrer">
                  /r/{link.code}
                </a>
              </td>
              <td className="target" title={link.target_url}>
                {link.target_url}
              </td>
              <td className="num">{link.clicks}</td>
              <td className="muted">{new Date(link.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
