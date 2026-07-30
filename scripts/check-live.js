const { chromium } = require("playwright");

const DEFAULT_BASE_URL = "https://unholyghost.org/";
const DEFAULT_WWW_URL = "https://www.unholyghost.org/";
const SPOTIFY_EMBED = "https://open.spotify.com/embed/album/7ICbOrsiIRThJOoHafvEOu";
const SOUNDCLOUD_EMBED = "https://w.soundcloud.com/player/";
const SOUNDCLOUD_USER_TOKEN = "api.soundcloud.com%2Fusers%2F12663938";
const LIVE_BROWSER_USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36";
const RETIRED_ANALYTICS_MARKERS = [
  "googletagmanager.com",
  "google-analytics.com",
  "GTM-KQVXQND4",
  "google_tags_first_party",
  "connect.facebook.net",
  "facebook.com/tr",
  "/mipz/",
];
const RETIRED_ANALYTICS_URL_MARKERS = [
  "googletagmanager.com",
  "google-analytics.com",
  "connect.facebook.net",
  "facebook.com/tr",
  "/mipz/",
];

function normalizeUrl(rawUrl) {
  const url = new URL(rawUrl);
  if (!url.pathname.endsWith("/")) url.pathname += "/";
  return url;
}

function cacheBust(rawUrl, label) {
  const url = new URL(rawUrl);
  url.searchParams.set("live-smoke", `${Date.now()}-${label}`);
  return url.toString();
}

function requireStatus(response, expected, label) {
  if (!expected.includes(response.status)) {
    throw new Error(`${label} returned HTTP ${response.status}; expected ${expected.join(" or ")}.`);
  }
}

function requireNoRetiredAnalytics(text, label) {
  const matches = RETIRED_ANALYTICS_MARKERS.filter((marker) => text.includes(marker));
  if (matches.length) {
    throw new Error(`${label} contains retired analytics markers: ${matches.join(", ")}`);
  }
}

function isRetiredAnalyticsUrl(url) {
  const normalized = url.toLowerCase();
  return RETIRED_ANALYTICS_URL_MARKERS.some((marker) => normalized.includes(marker.toLowerCase()));
}

async function fetchText(url, label, options = {}) {
  const response = await fetch(url, {
    redirect: options.redirect || "follow",
    headers: {
      "User-Agent": options.userAgent || LIVE_BROWSER_USER_AGENT,
    },
  });
  requireStatus(response, options.expected || [200], label);
  return { response, text: await response.text() };
}

async function checkHttp(baseUrl, wwwUrl) {
  const homepageUrl = cacheBust(baseUrl, "home");
  const { text: homepage } = await fetchText(homepageUrl, "homepage");
  requireNoRetiredAnalytics(homepage, "Homepage response");

  for (const [label, needle] of [
    ["Spotify embed", SPOTIFY_EMBED],
    ["SoundCloud user embed", SOUNDCLOUD_USER_TOKEN],
  ]) {
    if (!homepage.includes(needle)) {
      throw new Error(`Homepage is missing ${label}: ${needle}`);
    }
  }

  const wwwCheckUrl = cacheBust(wwwUrl, "www");
  const wwwResponse = await fetch(wwwCheckUrl, {
    redirect: "manual",
    headers: {
      "User-Agent": LIVE_BROWSER_USER_AGENT,
    },
  });
  requireStatus(wwwResponse, [301, 302, 307, 308], "www redirect");

  const location = wwwResponse.headers.get("location") || "";
  if (!location.startsWith(baseUrl)) {
    throw new Error(`www redirect points to ${location || "(empty)"}, expected ${baseUrl}`);
  }

  const retiredDiscoveryUrls = [
    new URL("/.well-known/agent-service.json", baseUrl).toString(),
    new URL("/.well-known/agent-skills/index.json", baseUrl).toString(),
  ];
  for (const retiredUrl of retiredDiscoveryUrls) {
    await fetchText(cacheBust(retiredUrl, "retired"), retiredUrl, { expected: [404] });
  }

  return {
    homepageUrl,
    wwwCheckUrl,
    retiredDiscoveryUrls,
  };
}

async function checkPlayer(baseUrl) {
  const browser = await chromium.launch({ headless: true });
  const failures = [];
  const retiredAnalyticsRequests = [];
  const pageUrl = cacheBust(baseUrl, "player");

  try {
    const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
    page.on("request", (request) => {
      if (isRetiredAnalyticsUrl(request.url())) {
        retiredAnalyticsRequests.push(request.url());
      }
    });
    page.on("requestfailed", (request) => {
      const url = request.url();
      if (url.startsWith(baseUrl) || url.startsWith(SPOTIFY_EMBED) || url.startsWith(SOUNDCLOUD_EMBED)) {
        failures.push(`${url}: ${request.failure()?.errorText || "request failed"}`);
      }
    });

    const response = await page.goto(pageUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    if (!response || response.status() !== 200) {
      throw new Error(`Player page returned HTTP ${response ? response.status() : "(no response)"}.`);
    }
    requireNoRetiredAnalytics(await page.content(), "Browser-rendered homepage");

    await page.locator(".player-shell").waitFor({ timeout: 10000 });
    await page.waitForTimeout(2500);

    const spotifySrc = await page.locator("#playerSpotify iframe").getAttribute("src");
    const soundcloudDataSrc = await page.locator("#playerSoundcloud iframe").getAttribute("data-src");

    await page.locator("#tabSoundcloud").click({ timeout: 5000 });
    await page.waitForTimeout(2500);

    const soundcloudSrc = await page.locator("#playerSoundcloud iframe").getAttribute("src");
    const activePanel = await page.locator(".player-embed.is-active").getAttribute("id");

    if (!spotifySrc || !spotifySrc.startsWith(SPOTIFY_EMBED)) {
      throw new Error(`Spotify iframe did not have the expected src. Found: ${spotifySrc || "(empty)"}`);
    }

    if (!soundcloudDataSrc || !soundcloudDataSrc.includes(SOUNDCLOUD_USER_TOKEN)) {
      throw new Error(`SoundCloud iframe did not have the expected data-src. Found: ${soundcloudDataSrc || "(empty)"}`);
    }

    if (!soundcloudSrc || !soundcloudSrc.startsWith(SOUNDCLOUD_EMBED)) {
      throw new Error(`SoundCloud iframe did not load after tab click. Found: ${soundcloudSrc || "(empty)"}`);
    }

    if (activePanel !== "playerSoundcloud") {
      throw new Error(`SoundCloud tab did not become active. Active panel: ${activePanel || "(none)"}`);
    }

    if (failures.length) {
      throw new Error(`Live player request failures:\n${failures.join("\n")}`);
    }

    if (retiredAnalyticsRequests.length) {
      throw new Error(`Retired analytics requests observed:\n${retiredAnalyticsRequests.join("\n")}`);
    }

    return {
      pageUrl,
      spotifySrc,
      soundcloudSrc,
      activePanel,
      retiredAnalyticsRequests,
    };
  } finally {
    await browser.close();
  }
}

async function main() {
  const baseUrl = normalizeUrl(process.env.LIVE_BASE_URL || DEFAULT_BASE_URL).toString();
  const wwwUrl = normalizeUrl(process.env.LIVE_WWW_URL || DEFAULT_WWW_URL).toString();

  const http = await checkHttp(baseUrl, wwwUrl);
  const player = await checkPlayer(baseUrl);

  console.log(
    JSON.stringify(
      {
        ok: true,
        baseUrl,
        wwwUrl,
        http,
        player,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
