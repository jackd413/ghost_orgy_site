# Ghost Orgy homepage recenter

This package contains the complete replacement `index.html` and a PowerShell publisher that applies it on a clean checkout, runs repository QA, commits it on a focused branch, pushes it, and opens a draft PR when GitHub CLI is available.

## Apply and open the draft PR

From PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\publish-homepage-pr.ps1 -RepoPath "C:\path\to\ghost_orgy_site" -InstallQaDependencies
```

The script uses:

- base branch: `main`
- feature branch: `agent/recenter-homepage`
- commit: `Recenter homepage on Salt and the Orchard`
- draft PR title: `Recenter the homepage on Salt and the Orchard`

It refuses to proceed with a dirty working tree and stores the previous homepage in the package's `backups` folder before replacement.

## Apply without pushing

```powershell
.\publish-homepage-pr.ps1 -RepoPath "C:\path\to\ghost_orgy_site" -SkipPush -SkipPullRequest
```

## Homepage structure

1. Full-viewport Orchard entry with two actions only: **Hear Salt** and **Enter the Orchard**.
2. Salt as the primary release, with direct listening destinations and a restrained Suffering signal.
3. Three recovered fragments that establish the visual world without explaining it to death.
4. The Nine as a full-bleed encounter.
5. The Orchard statement and mantra.
6. Quiet secondary doors for Shop, Artifacts, Licensing, and Press.

The replacement preserves existing public destinations and legacy anchors, including `#start-here`, `#conversion`, `#signal`, `#fragments`, `#sisters`, `#nine`, `#orchard`, `#traces`, and `#effects`.
