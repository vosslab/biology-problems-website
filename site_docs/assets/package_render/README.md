# Browser package rendering assets

These are unmodified npm distribution files used only when a requested Blackboard package
needs table or molecule images. `source.json` records pinned package versions and SHA256 hashes.
The npm lockfile records registry tarball integrity.

- `modern_screenshot.mjs`: modern-screenshot 4.7.0, MIT; see `modern_screenshot_license.txt`.
- `rdkit.js` and `rdkit.wasm`: @rdkit/rdkit 2026.9.1, BSD 3-Clause;
  see `rdkit_license.txt`. The npm package omits the license text, so the vendor helper retrieves
  the RDKit upstream license from the exact revision recorded in `source.json`.

Refresh from the repository root:

```bash
npm ci --ignore-scripts --prefix devel/package_render_vendor
node devel/vendor_package_render.mjs
```

The small dependency directory is for asset refresh only. It adds no frontend framework or
build step to normal website generation. The table renderer uses the QPM wrapper with embedded
fonts, captures a measured block at scale 1, and resets cloned table height to `auto` so captions
retain natural row layout. Canvas images retain their authored dimensions.
