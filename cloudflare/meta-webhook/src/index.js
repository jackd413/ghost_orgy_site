const WEBHOOK_PATH = "/instagram/webhook";
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
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === TIKTOK_CALLBACK_PATH) {
      return relayTikTokOAuthCallback(url);
    }
    if (url.pathname !== WEBHOOK_PATH) {
      return new Response("Not found", { status: 404 });
    }

    if (request.method === "GET") {
      const mode = url.searchParams.get("hub.mode");
      const token = url.searchParams.get("hub.verify_token");
      const challenge = url.searchParams.get("hub.challenge");
      if (mode === "subscribe" && token === env.META_VERIFY_TOKEN && challenge) {
        return new Response(challenge, {
          status: 200,
          headers: { "content-type": "text/plain; charset=utf-8" },
        });
      }
      return new Response("Forbidden", { status: 403 });
    }

    if (request.method === "POST") {
      // This publisher does not consume inbound Instagram events yet. Acknowledge
      // delivery without retaining payloads so Meta does not repeatedly retry.
      return new Response("EVENT_RECEIVED", { status: 200 });
    }

    return new Response("Method not allowed", {
      status: 405,
      headers: { allow: "GET, POST" },
    });
  },
};
