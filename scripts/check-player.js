const fs = require("fs");
const http = require("http");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const SPOTIFY_EMBED = "https://open.spotify.com/embed/album/7ICbOrsiIRThJOoHafvEOu";
const SOUNDCLOUD_EMBED = "https://w.soundcloud.com/player/";

const MIME_TYPES = new Map([
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".svg", "image/svg+xml"],
  [".webp", "image/webp"],
  [".woff", "font/woff"],
  [".woff2", "font/woff2"],
  [".ttf", "font/ttf"],
]);

function serveFile(request, response) {
  const requestUrl = new URL(request.url, "http://127.0.0.1");
  let pathname = decodeURIComponent(requestUrl.pathname);
  if (pathname.endsWith("/")) pathname += "index.html";

  const filePath = path.resolve(ROOT, `.${pathname}`);
  if (!filePath.startsWith(ROOT + path.sep) && filePath !== ROOT) {
    response.writeHead(403);
    response.end("Forbidden");
    return;
  }

  fs.readFile(filePath, (error, data) => {
    if (error) {
      response.writeHead(404);
      response.end("Not found");
      return;
    }

    response.writeHead(200, {
      "Content-Type": MIME_TYPES.get(path.extname(filePath).toLowerCase()) || "application/octet-stream",
    });
    response.end(data);
  });
}

function startServer() {
  const server = http.createServer(serveFile);
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

async function main() {
  const server = await startServer();
  const { port } = server.address();
  const baseUrl = `http://127.0.0.1:${port}/`;
  const failures = [];
  let browser;

  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
    page.on("requestfailed", (request) => {
      const url = request.url();
      if (url.startsWith(baseUrl) || url.startsWith(SPOTIFY_EMBED) || url.startsWith(SOUNDCLOUD_EMBED)) {
        failures.push(`${url}: ${request.failure()?.errorText || "request failed"}`);
      }
    });

    await page.goto(baseUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.locator(".player-shell").waitFor({ timeout: 5000 });

    const initialSpotifySrc = await page.locator("#playerSpotify iframe").getAttribute("src");
    if (!initialSpotifySrc || !initialSpotifySrc.startsWith(SPOTIFY_EMBED)) {
      throw new Error(`Spotify iframe did not have an immediate src. Found: ${initialSpotifySrc || "(empty)"}`);
    }

    await page.locator(".player-shell").scrollIntoViewIfNeeded();
    await page.waitForFunction(
      (spotifyEmbed) => window.frames.length > 1 && Array.from(document.querySelectorAll("iframe")).some((frame) => frame.src.startsWith(spotifyEmbed)),
      SPOTIFY_EMBED,
      { timeout: 10000 },
    );

    await page.locator("#tabSoundcloud").click();
    await page.waitForFunction(
      (soundcloudEmbed) => document.querySelector("#playerSoundcloud iframe")?.src.startsWith(soundcloudEmbed),
      SOUNDCLOUD_EMBED,
      { timeout: 10000 },
    );

    const activePanel = await page.locator(".player-embed.is-active").getAttribute("id");
    if (activePanel !== "playerSoundcloud") {
      throw new Error(`SoundCloud tab did not become active. Active panel: ${activePanel || "(none)"}`);
    }

    if (failures.length) {
      throw new Error(`Player request failures:\n${failures.join("\n")}`);
    }

    console.log("Player smoke passed.");
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
