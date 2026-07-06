const DEFAULT_BASE_URL = "https://unholyghost.org/";

const EXPECTED_HEADERS = [
  {
    name: "strict-transport-security",
    label: "HSTS",
    validate: (value) => /^max-age=31536000\b/i.test(value) && /includesubdomains/i.test(value),
  },
  {
    name: "x-content-type-options",
    label: "X-Content-Type-Options",
    validate: (value) => value.toLowerCase() === "nosniff",
  },
  {
    name: "referrer-policy",
    label: "Referrer-Policy",
    validate: (value) => value.toLowerCase() === "strict-origin-when-cross-origin",
  },
  {
    name: "permissions-policy",
    label: "Permissions-Policy",
    validate: (value) =>
      ["camera=()", "geolocation=()", "microphone=()", "payment=()", "usb=()"].every((item) =>
        value.toLowerCase().includes(item),
      ),
  },
  {
    name: "content-security-policy-report-only",
    label: "Content-Security-Policy-Report-Only",
    validate: (value) =>
      [
        "default-src 'self'",
        "object-src 'none'",
        "frame-src https://open.spotify.com https://w.soundcloud.com https://www.googletagmanager.com",
      ].every((item) => value.includes(item)),
  },
];

async function main() {
  const baseUrl = new URL(process.env.LIVE_BASE_URL || DEFAULT_BASE_URL);
  const response = await fetch(baseUrl, {
    method: "HEAD",
    redirect: "follow",
    headers: {
      "User-Agent": "ghost-orgy-header-smoke/1.0",
    },
  });

  if (!response.ok) {
    throw new Error(`${baseUrl} returned HTTP ${response.status}.`);
  }

  const failures = [];
  const observed = {};

  for (const expected of EXPECTED_HEADERS) {
    const value = response.headers.get(expected.name) || "";
    observed[expected.name] = value;
    if (!value) {
      failures.push(`${expected.label} header is missing.`);
      continue;
    }
    if (!expected.validate(value)) {
      failures.push(`${expected.label} header has unexpected value: ${value}`);
    }
  }

  if (failures.length) {
    console.error(JSON.stringify({ ok: false, url: baseUrl.toString(), observed, failures }, null, 2));
    process.exitCode = 1;
    return;
  }

  console.log(JSON.stringify({ ok: true, url: baseUrl.toString(), observed }, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
