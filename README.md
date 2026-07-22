# 🚀 Liftoff — one-click Blender cloud rendering

**Clean → Save → Render → launch to the cloud.** One button purges junk datablocks,
saves your `.blend`, renders the frame, and drops a self-contained copy into your
Google Drive folder — ready to render for free on GPU with
[Google Colab](https://github.com/ynshung/blender-colab). No OAuth, no setup.

Built for a "iterate fast, render clean" workflow where orphan data piles up and you
just want renders (and a cloud-ready file) to land straight in a synced Drive folder.

## Features

- **Clean, Save & Render** — runs the three steps in order:
  1. **Clean** — recursively purges orphan datablocks (meshes, materials, images, textures…).
  2. **Save** — `save_mainfile` on the current `.blend`.
  3. **Render** — renders the current frame with the active camera and writes a
     timestamped PNG (`<file>_<YYYYMMDD_HHMMSS>.png`).
- **Individual steps** — Clean / Save / Render buttons to run just one.
- **Save copy to Drive** — packs all external textures and writes `<file>_cloud.blend`
  into your Google Drive Desktop folder, which then uploads it automatically. No OAuth.
- **Go to Colab** — opens the blender-colab render notebook in your browser.
- Renders and the cloud copy are saved into a configurable **Google Drive folder**
  (default `G:\Mi unidad\RENDERS`), so everything syncs to the cloud on its own.

## Install

1. Download `clean_save_render.py`.
2. Blender → `Edit → Preferences → Add-ons → Install…` and pick the file.
3. Enable **"Clean, Save & Render"**.
4. Set your synced Drive folder in the add-on preferences (defaults to `G:\Mi unidad\RENDERS`).

## Usage

- **Sidebar**: press `N` in the 3D Viewport → **Pipeline** tab.
- **File menu**: entries added at the bottom.
- **Shortcut**: `Ctrl+Alt+S` runs Clean, Save & Render (kept off `Ctrl+S` on purpose —
  rendering on every save would be slow).

## Cloud rendering with Colab

1. Click **Save copy to Drive** → `<file>_cloud.blend` lands in your Drive folder and syncs.
2. Click **Go to Colab** → open the notebook.
3. In the notebook: pick a Blender build that matches your file's version, enable the GPU,
   point it at the `.blend` on your Drive, render.

## Notes

- The render step blocks Blender while it runs (a normal foreground render).
- Requires **Google Drive for Desktop** for the auto-upload button; without it the render
  step falls back to a local `renders/` folder.

## License

MIT — see [LICENSE](LICENSE).
