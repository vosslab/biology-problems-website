# Install

This repo is a MkDocs site. An install is complete when you can run MkDocs to
serve or build the site from [site_docs/](../site_docs/) using
[mkdocs.yml](../mkdocs.yml).

## Requirements

- Python 3.12.
- pip for installing dependencies from [pip_requirements.txt](../pip_requirements.txt).
- macOS ARM64 for native self-test generation with the Git-tracked converter.
  A normal build requires neither QPM source nor Rust/Cargo.
- Node.js 24 or later and npm for browser asset refresh, Playwright tests, and screenshots.
- Rust/Cargo and QPM source only when refreshing the vendored QPM dependencies.
- A JavaScript-enabled browser for on-demand package downloads. Vendored WebAssembly,
  modern-screenshot, and RDKit assets are served with the static site.

## Install steps

1. Clone the repository.
2. Keep the tracked [vendor/qpm-native/](../vendor/qpm-native/) directory, including
   the executable permission on `bbq-converter`. BPW selects the binary matching the
   host OS and CPU. Currently macOS ARM64 is supplied; other hosts receive a clear
   incompatibility message. No compilation occurs during ordinary site builds.
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

## Refresh QPM dependencies

QPM is a stable vendored dependency. Refresh deliberately when adopting an upstream fix.
On macOS ARM64, clone QPM beside BPW (or set `QPM_ROOT` to another checkout; relative
paths resolve from the BPW root). To build and refresh only the native executable:

```bash
source source_me.sh && python3 devel/vendor_qti_wasm.py --native-only
```

The helper runs Cargo with the `aarch64-apple-darwin` target and obtains the actual
executable path from Cargo's artifact messages. It verifies execution with `--help`, then copies
the binary, license, and `source.json` into
[vendor/qpm-native/darwin-arm64/](../vendor/qpm-native/darwin-arm64/).
The receipt records source revision and dirty state, target, Cargo package version, build command,
and binary hash. Commit all three files together. Prefer a clean upstream checkout
for releases; a dirty receipt does not claim that its commit reproduces the bytes.

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

With no flags, `vendor_qti_wasm.py` refreshes both native and WASM artifacts. Use
`--wasm-only` to refresh only the prebuilt browser package. The canonical WASM build
invokes wasm-pack for the release web target and compiles TypeScript.
The vendor helper copies the complete distribution and records consumed-file SHA256 hashes,
source path, and a null source revision when no revision receipt is supplied.

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
