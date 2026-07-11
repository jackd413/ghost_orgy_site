const CRITICAL_LINKS = [
  {
    label: "Fourthwall storefront",
    url: "https://shop.unholyghost.org/",
    expected: [200],
    requiredText: "Ghost Orgy",
  },
  {
    label: "Fourthwall featured product",
    url: "https://shop.unholyghost.org/products/this-is-not-a-warning",
    expected: [200],
    requiredText: "This Is Not A Warning",
  },
  {
    label: "Bandcamp Salt album",
    url: "https://ghostorgy.bandcamp.com/album/salt",
    expected: [200],
    requiredText: "Salt",
  },
  {
    label: "YouTube channel",
    url: "https://www.youtube.com/@GhostOr9y",
    expected: [200],
    requiredText: "Ghost Orgy",
  },
  {
    label: "Spotify embed",
    url: "https://open.spotify.com/embed/album/7ICbOrsiIRThJOoHafvEOu?utm_source=generator",
    expected: [200],
    requiredText: "Spotify",
  },
  {
    label: "SoundCloud embed",
    url: "https://w.soundcloud.com/player/?visual=true&url=https%3A%2F%2Fapi.soundcloud.com%2Fusers%2F12663938&show_artwork=true",
    expected: [200],
    requiredText: "SoundCloud",
  },
];

const USER_AGENT = "ghost-orgy-external-link-smoke/1.0";

async function fetchWithTimeout(url, timeoutMs = 20000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, {
      redirect: "follow",
      signal: controller.signal,
      headers: {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      },
    });
  } finally {
    clearTimeout(timeout);
  }
}

async function checkLink(link) {
  const response = await fetchWithTimeout(link.url);
  const text = await response.text();

  if (!link.expected.includes(response.status)) {
    throw new Error(`${link.label} returned HTTP ${response.status}; expected ${link.expected.join(" or ")}.`);
  }

  if (link.requiredText && !text.toLowerCase().includes(link.requiredText.toLowerCase())) {
    throw new Error(`${link.label} response did not contain required text: ${link.requiredText}`);
  }

  return {
    label: link.label,
    url: response.url,
    status: response.status,
  };
}

async function main() {
  const results = [];
  const failures = [];

  for (const link of CRITICAL_LINKS) {
    try {
      results.push(await checkLink(link));
    } catch (error) {
      failures.push(`${link.label} (${link.url}): ${error.message}`);
    }
  }

  if (failures.length) {
    console.error(JSON.stringify({ ok: false, failures, results }, null, 2));
    process.exitCode = 1;
    return;
  }

  console.log(JSON.stringify({ ok: true, results }, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
