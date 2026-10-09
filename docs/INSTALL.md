# Install

This repo is a MkDocs site. An install is complete when you can run MkDocs to
serve or build the site from [site_docs/](../site_docs/) using
[mkdocs.yml](../mkdocs.yml).

## Requirements

- Python 3.12.
- pip for installing dependencies from [pip_requirements.txt](../pip_requirements.txt).
- The sibling `qti-package-maker-rs` checkout and its release `bbq-converter` binary to
  regenerate native self-tests with `build_site.py`.
- Node.js 24 or later and npm for browser asset refresh, Playwright tests, and screenshots.
- Rust/Cargo for the native converter and canonical WebAssembly package build.
- A JavaScript-enabled browser for on-demand package downloads. Vendored WebAssembly,
  modern-screenshot, and RDKit assets are served with the static site.

## Install steps

1. Clone the repository.
2. Clone `qti-package-maker-rs` beside this repository. From that checkout, build the
   converter required by content generation:
   ```bash
   cd ../qti-package-maker-rs
   cargo build --locked --release -p qti-cli --bins
   cd ../biology-problems-website
   ```
   The website build expects the executable at
   `../qti-package-maker-rs/target/release/bbq-converter` and stops if it is missing or not
   executable. There is no Python converter fallback.
3. From the website repo root, install dependencies:
   ```bash
   source source_me.sh && python3 -m pip install -r pip_requirements.txt
   ```
4. For browser tests and screenshot capture, install the development packages and
   Chromium:
   ```bash
   npm install
   npx playwright install chromium
   ```
Browser downloads render tables and molecules in the visitor's browser. Ordinary content
builds generate native self-tests and retain direct BBQ/PGML files.

## Refresh browser dependencies

The sibling `@vosslab/qti-wasm` package is private. This website consumes its complete built
`dist` as a vendored artifact dependency. After changing its Rust or TypeScript sources, run
its canonical build and then refresh the website copy:

```bash
cd ../qti-package-maker-rs/packages/qti-wasm
npm ci
npm run build
cd ../../../biology-problems-website
source source_me.sh && python3 devel/vendor_qti_wasm.py
```

The canonical build invokes wasm-pack for the release web target and compiles TypeScript.
The vendor helper copies the complete distribution and records consumed-file SHA256 hashes,
source path, and a null source revision when no revision receipt is supplied.

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
