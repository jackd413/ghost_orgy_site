const TIKTOK_CALLBACK_PATH = "/tiktok/callback";
const TIKTOK_LOCAL_CALLBACK = "http://localhost:8768/tiktok/callback";

function relayTikTokOAuthCallback(url) {
  const destination = new URL(TIKTOK_LOCAL_CALLBACK);
  for (const field of ["code", "state", "error", "error_description"]) {
    const value = url.searchParams.get(field);
    if (value !== null) {
      destination.searchParams.set(field, value);
    }
  }
  return Response.redirect(destination.toString(), 302);
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname !== TIKTOK_CALLBACK_PATH) {
      return new Response("Not found", { status: 404 });
    }
    if (request.method !== "GET") {
      return new Response("Method not allowed", { status: 405, headers: { allow: "GET" } });
    }
    return relayTikTokOAuthCallback(url);
  },
};
