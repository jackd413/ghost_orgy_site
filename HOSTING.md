# Hosting and Caching

`https://unholyghost.org/` is served by **GitHub Pages** with **Cloudflare**
sitting in front as DNS + CDN. The repo has no `_headers`, `netlify.toml`, or
`wrangler.toml` — none of those formats apply to this stack.

## Deployment path

GitHub Pages is configured in **GitHub Actions workflow** mode, not legacy
branch-deploy mode. The production deploy path is:

- `.github/workflows/deploy-pages.yml` runs on every push to `main` and can be
  run manually with `workflow_dispatch`.
- The `build` job runs local QA with `npm run check:all`, prepares a clean
  Pages artifact in `_site` from an explicit public allowlist, preserves
  dotfiles such as `.nojekyll` and `.well-known`, then uploads the artifact.
  Repo-only docs, CI/tooling scripts, Cloudflare API config, local sync config,
  and authoring/source folders are intentionally excluded from the published
  artifact.
- The `deploy` job publishes the artifact with `actions/deploy-pages` and then
  runs `npm run check:live` against `https://unholyghost.org/`.
- `.github/workflows/site-qa.yml` runs the same local QA on pull requests and
  pushes.
- `.github/workflows/live-smoke.yml` runs the live smoke test twice daily and
  can also be run manually.

If the final GitHub Pages deploy step fails with `Deployment failed, try again
later`, rerun the failed job first. That failure has previously come from the
GitHub Pages backend after a valid artifact was already built and uploaded.
Do not switch back to legacy branch deploy unless intentionally reverting the
workflow-mode setup.

## Security headers

Security headers must be applied in Cloudflare, not in this repo, because this
site is GitHub Pages behind Cloudflare rather than a platform that reads
checked-in header files.

Desired Cloudflare response-header transform configuration lives in
`cloudflare/security-headers-transform-ruleset.json`. It sets:

- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `Content-Security-Policy-Report-Only`

The CSP is intentionally report-only first because the live site uses
Google Tag Manager plus Spotify and SoundCloud embeds. After the report-only
policy has been observed cleanly, move toward an enforcing CSP in a separate
change.

Current live state: the response-header transform ruleset has been applied in
Cloudflare as ruleset `ce9f430a974b4f008f276374f9fb3363`. `npm run
check:headers` verifies the live headers on `https://unholyghost.org/`.

To apply the Cloudflare rule by API:

```powershell
$env:CLOUDFLARE_API_TOKEN = "<token with Zone Transform Rules Write>"
.\scripts\apply-cloudflare-security-headers.ps1
```

The Wrangler OAuth token on this machine can read the account and zone, but it
did not have Rulesets access for response header transforms during setup. Use a
Cloudflare API token with Zone Transform Rules Write permission for
`unholyghost.org`.

To verify the live headers after applying:

```powershell
npm run check:headers
```

## Where cache headers live

Cache headers are configured in the **Cloudflare dashboard** for the
`unholyghost.org` zone, not in this repo. Current setup:

- Browser cache behavior should be verified live before cache-sensitive launches.
  During this update, live responses returned `Cache-Control: max-age=86400` for
  HTML and `.well-known` JSON.
- **Caching → Cache Rules → "Long cache for static assets"**:
  - Match: URI Path starts with `/images/` **or** `/fonts/`
  - Current live browser TTL: **1 year** (`Cache-Control: max-age=31536000`)
  - Edge TTL: **1 month**

This is what cut the Lighthouse "efficient cache lifetimes" warning.

## The rename-on-update rule

The year-long browser cache on `/images/*` means **if you overwrite an image
with the same filename, returning visitors will keep the old one for up to a
year**. Cloudflare can purge its own edge cache; it cannot reach into people's
browsers.

Therefore: **always rename an image on the way in.** Add a size suffix
(`-800`, `-1280`), a version (`-v2`), or a content hash. Examples already in
the repo:

- `hero-orchard-watcher.webp` + `hero-orchard-watcher-800.webp` + `-1280.webp`
  (responsive variants — different filenames, no cache collision)
- `cover-salt-final-20260526-1500.webp` + `-960.webp` + `-768.webp` + `-640.webp`

The same applies to fonts, though those rarely change.

## Implication for the asset-promote script

`scripts/promote-site-asset.ps1` already supports `-Name` to rename on the way
in (see [LOCAL_ASSETS.md](LOCAL_ASSETS.md)). If a promoted asset would collide
with an existing filename in `images/`, give it a new name rather than
overwriting.
