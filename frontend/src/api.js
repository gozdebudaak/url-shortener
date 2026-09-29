// All requests use relative paths, so the same build works behind any host.

async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(errorMessage(body) ?? `Request failed (${response.status})`);
  }
  return response.json();
}

function errorMessage(body) {
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) return "Please enter a valid URL (including https://).";
  return null;
}

export function listLinks() {
  return request("/api/links");
}

export function createLink(targetUrl) {
  return request("/api/links", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_url: targetUrl }),
  });
}

export function shortUrl(code) {
  return `${window.location.origin}/r/${code}`;
}
