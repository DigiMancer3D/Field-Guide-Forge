# Field Guide Forge (FGF)

A local-first **field guide editor and presenter** for source-aware episodes, script-driven layouts, OBS-safe broadcast views, and audience-facing public companion pages. Built for the DigiMancer Streamer Tools ecosystem.

> **Status:** experimental Alpha.4 / Studio Cues integration. Publish from a tested local installation. Third-party iframe behavior and local SBC/DMS integration depend on the user's system and browser.

## Features
- Edit `.fgf` projects, import compatible SWAR `.script` inputs, arrange pages, blocks, sources and proof displays.
- Export a host/broadcaster HTML for live use, or a separate privacy-reviewed public-web HTML for distribution.
- Studio Cues: assign Deck Card Widget cards and Streamer Board & Console `.sboard` boards at page/source/block level; enable or disable Auto Cues.
- Pair the private broadcaster with DMS Live Switcher over an authenticated loopback bridge; DMS validates selected assets against its registered rails.
- Presenter hotkeys: **W** next, **S** previous, **A** first, **D** last. Middle-click can toggle QR-Data after pairing.
- Compact broadcaster controls, Fullscreen/Return Screen, OBS-View/Full-Proof, optional Chat Thank You page, scene Escape and configurable OBS fullscreen background.
- Optional C++/Qt6 **FGF-BCL** launcher scans show folders and chooses the latest qualified private/broadcast FGF page without selecting public-web output.
- Local buttstore discovery from a shared user data folder without embedding collection paths in exported files.

## Running FGF locally

Expected default installation: `~/SBC_Streamer_Apps/FGF/`. Its existing `launch.sh` also acts as the SBC launcher entrypoint:

```bash
bash ./launch.sh
```

The local server helper starts detached and opens the editor in a preferred browser (LibreWolf first, where available). Avoid opening raw `index.html` when you need local collection discovery. A stop helper is included in `studio_cues_alpha4/stop_fgf.sh`.

**Typical source layout:**

```text
index.html                    # editor application
launch.sh                     # SBC entrypoint
browser.sh                    # optional existing browser launcher
studio_cues_alpha4/
  fgf_app_launcher.py         # local launcher helper
  launch_fgf.py               # local HTTP catalog service
  stop_fgf.sh
FGF_BCL/                      # Qt6/C++20 broadcaster selection utility
```

The shared `user_data/buttstores` folder is a **local dependency, not part of this GitHub repository**. Select collections through the Studio Cues panel and save only sanitized identifiers in the project.

## FGF-BCL

The optional FGF Broadcaster Launcher (`FGF_BCL/`) provides an editable search configuration and show-specific `.sh` launchers such as `3DCP_BCLaunch.sh`. It recognizes host/broadcast filename variants, excludes public-web variants, and ranks episode numbers without converting them to machine-sized integers. Build with C++20, CMake, and Qt6 development packages on your machine. See `FGF_BCL/build.sh` and `FGF_BCL/install.sh`.

## Integration

- [Streamer Board & Console](https://github.com/DigiMancer3D/Streamer-Board-Console) — app startup, profile control and pinboards.
- [DMS Live Switcher](https://github.com/DigiMancer3D/DMS-Live-Switcher) — local QR display switch and studio cue validator.
- [Deck Card Widget](https://github.com/DigiMancer3D/Deck-Card-Widget) — OBS deck cards with separate Full-Data/QR-Data layouts.
- [DMST](https://github.com/DigiMancer3D/DMST) — parent project hub.

See [Integration notes](docs/INTEGRATION.md) and [November 2026 update](docs/UPDATE_2026-11-08.md).

## Privacy, data, and publishing

**Never publish a private/host broadcaster HTML as an ordinary public webpage.** Export the dedicated public-web version after the privacy review and manually check its contents. Do not commit `.fgf`, `.buttstore`, `.sboard`, real episode outputs, pairing tokens, or local user data. This repository is for reusable application source, tools, sanitized examples and documentation.

