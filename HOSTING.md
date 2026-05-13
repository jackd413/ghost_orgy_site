# Hosting and Caching

`https://www.unholyghost.org/` is served by **GitHub Pages** with **Cloudflare**
sitting in front as DNS + CDN. The repo has no `_headers`, `netlify.toml`, or
`wrangler.toml` — none of those formats apply to this stack.

## Where cache headers live

Cache headers are configured in the **Cloudflare dashboard** for the
`unholyghost.org` zone, not in this repo. Current setup:

- **Caching → Configuration → Browser Cache TTL** → `Respect Existing Headers`
  (HTML inherits GitHub Pages' default ~10 minutes, so copy edits propagate
  quickly to returning visitors).
- **Caching → Cache Rules → "Long cache for static assets"**:
  - Match: URI Path starts with `/images/` **or** `/fonts/`
  - Browser TTL: **1 year**
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
- `cover-salt.webp` + `cover-salt-640.webp` + `-768.webp` + `-960.webp`

The same applies to fonts, though those rarely change.

## Implication for the asset-promote script

`scripts/promote-site-asset.ps1` already supports `-Name` to rename on the way
in (see [LOCAL_ASSETS.md](LOCAL_ASSETS.md)). If a promoted asset would collide
with an existing filename in `images/`, give it a new name rather than
overwriting.
