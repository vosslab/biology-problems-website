# Install

This repo is a MkDocs site. An install is complete when you can run MkDocs to
serve or build the site from [site_docs/](../site_docs/) using
[mkdocs.yml](../mkdocs.yml).

## Requirements

- Python 3.12.
- pip for installing dependencies from [pip_requirements.txt](../pip_requirements.txt).
- Node.js 24 or later and npm for browser asset refresh, Playwright tests, and screenshots.
- Rust/Cargo and QPM source only when building a new vendored WASM package.
- A JavaScript-enabled browser for self-tests and on-demand package downloads. Vendored WebAssembly,
  modern-screenshot, and RDKit assets are served with the static site.

## Install steps

1. Clone the repository.
2. From the website repo root, install dependencies:
   ```bash
   source source_me.sh && python3 -m pip install -r pip_requirements.txt
   ```
3. For browser tests and screenshot capture, install the development packages and
   Chromium:
   ```bash
   npm install
   npx playwright install chromium
   ```
Browser downloads render tables and molecules in the visitor's browser. Ordinary content
builds retain direct BBQ/PGML files. Self-test HTML is generated in the browser from BBQ banks.

## Refresh QPM dependencies

QPM is a stable vendored dependency. Refresh deliberately when adopting an upstream fix.
Clone QPM beside BPW or set `QPM_ROOT` to another checkout; relative paths resolve
from the BPW root. Ordinary site builds require neither QPM source nor Rust/Cargo.

The sibling `@vosslab/qti-wasm` package is private. This website consumes its complete built
`dist` as a vendored artifact dependency. After updating the QPM checkout's Rust or
TypeScript sources, compile and refresh BPW with one command from the BPW root:

```bash
source source_me.sh && python3 devel/vendor_qti_wasm.py
```

The helper runs `npm ci` and QPM's canonical `npm run build`. That build invokes
wasm-pack for the release web target and compiles TypeScript. Only after it succeeds
does the helper replace BPW's browser package and record consumed-file SHA256 hashes.
If installation or compilation fails, fix the reported error and rerun the same
command; BPW's existing package remains untouched. The helper uses the current
local QPM sources without pulling Git changes. Local edits are included, so the
recorded source revision remains null and hashes identify the consumed bytes.

Run `mkdocs build` afterward to include the refreshed package in the built site.

## Refresh other browser dependencies

Refresh the browser renderer and molecule assets from their pinned package lock:

```bash
npm ci --ignore-scripts --prefix devel/package_render_vendor
node devel/vendor_package_render.mjs
```

The refresh helper copies modern-screenshot 4.7.0 and RDKit 2026.9.1, their licenses, and the
RDKit WebAssembly bytes into `site_docs/assets/package_render/`. Its `source.json` records
versions, hashes, and the pinned upstream RDKit license URL; refreshing that license requires
network access. Deployed pages use these local copies. Node/npm are maintainer tools.

## Verify install

Run:

```bash
source source_me.sh && python3 -m mkdocs --version
```

## Known gaps

- Confirm whether a virtual environment is required or preferred.
