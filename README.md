# bmihovski Kodi repository

Personal Kodi addon repository, published to <https://bmihovski.github.io/lukav-kodi-repo/> by GitHub Actions.
Forked from [lukavia/lukav-kodi-repo](https://github.com/lukavia/lukav-kodi-repo).

Addons (git submodules in `src/`, folder name = addon id):

- `src/plugin.video.sprinttv` → [bmihovski/plugin.video.mtelnow](https://github.com/bmihovski/plugin.video.mtelnow) (Sprint IPTV)

## Install in Kodi

1. Settings → System → Add-ons → enable **Unknown sources**.
2. File manager → Add source → `https://bmihovski.github.io/lukav-kodi-repo/` (name it e.g. `bmihovski`).
3. Add-ons → Install from zip file → `bmihovski` → `repository.bmihovski-*.zip`.
4. Add-ons → Install from repository → bmihovski Kodi Repository → Video add-ons → Sprint IPTV.

Kodi then auto-updates the addon when a new version is published.

## Publishing

`.github/workflows/publish.yml` runs on every push to `master`, daily, and on demand (Actions → Run workflow).
It pulls the latest commit of each submodule's branch, so a plugin release only needs a version bump in its `addon.xml`.

One-time setup: repo Settings → Pages → Source: **GitHub Actions**.

Build locally: `python3 build.py _site bmihovski lukav-kodi-repo`
