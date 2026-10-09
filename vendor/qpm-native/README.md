# Vendored QPM native converter

BPW runs its own Git-tracked executable here. Normal site builds do not inspect or
build the QPM source repository. The supplied platform is `darwin-arm64` (macOS
ARM64); other platforms are reported as unsupported until a compatible artifact
is supplied.

Refresh explicitly from BPW on macOS ARM64:

```bash
source source_me.sh && python3 devel/vendor_qti_wasm.py --native-only
```

The source defaults to `../qti-package-maker-rs`; `QPM_ROOT` overrides it for refresh
only. Cargo builds the executable, and the helper copies it with executable mode,
its license, and a provenance receipt. Commit those files together. See
[INSTALL.md](../../docs/INSTALL.md) for the combined native/WASM refresh workflow.

QPM is distributed under LGPL-3.0-or-later. The accompanying license and
`source.json` identify the upstream source repository, checkout revision, dirty
state, binary version, target, build command, and artifact hash. The binary links
to macOS system libraries; Rust is not required to execute it.
