# Local Asset Workflow

This repo stays public because it serves `https://unholyghost.org/`.

The Ghost Orgy canon/reference library can still live alongside the site locally,
but it should not be committed into this repository.

## Local-only folders

- `canon/`
- `source-assets/`

Those directories are intentionally ignored by git. They are safe to use for:

- lore and canon reference
- art exploration
- branding/source files
- social/share-package context

They are not part of the public repo and are not published by GitHub Pages unless
you deliberately copy files from them into tracked website paths.

## Website-published folders

- `index.html`
- `images/`

Only assets that should actually ship on the public site belong in `images/`.

## Refresh the local canon library

1. Create or update `canon-sync.local.json` with your machine-specific source paths.
2. Run:

```powershell
.\scripts\sync-canon.ps1 -Config .\canon-sync.local.json
```

That will re-import local canon/source material from your `C:\Ghost Orgy\...` folders
into the ignored local folders in this repo.

## Promote a chosen asset onto the website

When an image is ready to be public, copy it into tracked site assets with:

```powershell
.\scripts\promote-site-asset.ps1 ".\canon\sisters-watchers\02 - lust\hero-sister.jpg"
```

Or rename it on the way in:

```powershell
.\scripts\promote-site-asset.ps1 ".\source-assets\branding\02- logos\Logo - They Perished\Ghost Orgy Logo - They Perished.png" -Name "ghost-orgy-logo.png"
```

That copies the selected file into `images/`, where it can be referenced from `index.html`
and committed intentionally.
