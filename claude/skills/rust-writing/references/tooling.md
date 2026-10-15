# Tooling: clippy, rustfmt, lints and CI

## Clippy

- **Default groups:** `correctness` on deny; `suspicious`, `style`, `complexity` and `perf` on warn; `pedantic`, `nursery` and `cargo` off. Source: https://github.com/rust-lang/rust-clippy/blob/master/README.md
- **Never the whole `restriction` group.** The README: "The `restriction` category should, _emphatically_, not be enabled as a whole." Pick individual lints. Source: same page.
- **Three styles in the flagship repos:**
  - `pedantic` enabled with justified allows: uv, ruff, serde.
  - A curated list of individual lints: clap and axum.
  - Minimal: cargo (`all = allow` plus `correctness`) and rust-analyzer (default groups, `perf` on deny).
  For a small project, the curated list gives more signal per lint. Sources: https://github.com/astral-sh/uv/blob/main/Cargo.toml, https://github.com/clap-rs/clap/blob/master/Cargo.toml, https://github.com/rust-lang/cargo/blob/master/Cargo.toml
- **Every `allow` carries its reason in a comment.** serde groups its allows by reason: "clippy bug", "noisy", "preference", "false positive". Source: https://github.com/serde-rs/serde/blob/master/serde/src/lib.rs
- **`clippy.toml` is for `disallowed-methods` and `disallowed-types` with a reason,** and that way it forces the project's wrapper: `std::env::var` banned in cargo ("use `Config::get_env` instead"), `std::fs` banned in uv to force `fs-err`, `HashMap` banned in rust-analyzer in favor of `FxHashMap`. Sources: https://github.com/rust-lang/cargo/blob/master/clippy.toml, https://github.com/astral-sh/uv/blob/main/clippy.toml
- **Declare `msrv` or `rust-version`** so clippy does not suggest APIs newer than your minimum. Source: https://doc.rust-lang.org/clippy/configuration.html

## Lints in Cargo.toml

- **Levels go in `[lints]` in Cargo.toml**, not as `#![warn(...)]` scattered through the code; Cargo applies them to the package and not to the dependencies. `priority` orders groups against individual lints. Source: https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section
- **Never `#![deny(warnings)]` in the source code:** a new compiler version adds a warning and your crate stops compiling for everyone. Raise warnings to errors in CI with `-D warnings`. Source: https://rust-unofficial.github.io/patterns/anti_patterns/deny-warnings.html

A starting point for a binary, taken from the lints that repeat across rust-analyzer, clap, axum and uv:

```toml
[lints.rust]
unsafe_op_in_unsafe_fn = "warn"
unreachable_pub = "warn"
unused_qualifications = "warn"

[lints.clippy]
dbg_macro = "warn"
todo = "warn"
print_stderr = "warn"          # remove it if the binary writes to stderr on purpose
undocumented_unsafe_blocks = "warn"
str_to_string = "warn"
use_self = "warn"
await_holding_lock = "warn"    # only if there is async
```

## rustfmt

- **Default formatting,** which follows the Rust Style Guide: 4 spaces, 100 columns, trailing commas in multiline lists. Sources: https://github.com/rust-lang/rustfmt/blob/master/README.md, https://doc.rust-lang.org/style-guide/index.html
- **Minimal `rustfmt.toml` or none.** cargo, uv and ruff only set `style_edition = "2024"`; tokio and serde have no file. rustc adds `group_imports = "StdExternalCrate"` and `imports_granularity = "Module"`, which require nightly. BurntSushi uses `max_width = 79`. Sources: https://github.com/rust-lang/rust/blob/master/rustfmt.toml, https://github.com/BurntSushi/ripgrep/blob/master/rustfmt.toml

## CI

The CI that tokio, axum, clap, cargo, uv and ruff share:

```
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo test --workspace --locked
```

Plus, depending on the project:

- An MSRV job that compiles with the version in `rust-version`.
- `cargo deny check` for licenses, security advisories and duplicates (tokio, axum, clap, cargo, uv, ruff).
- `-Z minimal-versions` to check that the declared minimums compile (serde, clap, tokio, tracing).
- `cargo semver-checks` in published libraries (cargo, tokio).
- miri if there is `unsafe` with pointers (tokio, serde).

`--all-targets` matters: without it clippy does not look at tests, benches or examples. ripgrep is the known exception: it does not run clippy in CI. Sources: https://github.com/tokio-rs/tokio/blob/master/.github/workflows/ci.yml, https://github.com/tokio-rs/axum/blob/main/.github/workflows/CI.yml, https://github.com/BurntSushi/ripgrep/blob/master/.github/workflows/ci.yml

## Comment conventions

- **Comments say why.** "Write comments that say *why*." Source: https://github.com/rust-lang/rust/blob/master/src/doc/rustc-dev-guide/src/conventions.md
- **`// FIXME` for pending work;** `tidy` rejects `TODO` in rustc. Source: same page.
- **A pure refactor goes in its own commit.** Source: same page.
