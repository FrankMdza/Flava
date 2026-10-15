# Dependencies and Cargo

## Adding a crate

- **Few dependencies, and none to save ten lines.** rust-analyzer: "Don't use small "helper" crates (exception: `itertools` and `either` are allowed)." BurntSushi, on Jiff: "my philosophy on adding new dependencies in an ecosystem crate like Jiff is very conservative". Sources: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md, https://github.com/BurntSushi/jiff
- **Before adding one, look at the tree it drags in:** `cargo tree -e normal -i <crate>` and `cargo tree -d` for duplicates.
- **Disable the default features you do not use** (`default-features = false`). Less code, less build.
- **Established crates over new ones** for whatever is infrastructure: `serde`, `anyhow`/`thiserror`, `clap`, `tokio` if there is async. Endler, on async: "stick to Tokio and well-established libraries like reqwest and sqlx." Source: https://corrode.dev/blog/async/
- **`cargo deny`** for licenses, RustSec advisories and allowed sources; tokio, axum, clap, cargo, uv and ruff run it.

## Features

- **Features are additive:** enabling one never removes functionality and any combination compiles. Cargo unifies features across the whole graph. Source: https://doc.rust-lang.org/cargo/reference/features.html
- **Avoid mutually exclusive features;** if there is no other way, `compile_error!` with a clear message. Source: same page.
- **Moving public code behind a feature breaks semver.** Source: https://doc.rust-lang.org/cargo/reference/features.html#semver-compatibility

## Versions

- **Declare `rust-version`** and test it in CI. Sources: https://doc.rust-lang.org/cargo/reference/manifest.html#the-rust-version-field, https://doc.rust-lang.org/cargo/reference/rust-version.html
- **With edition 2024 the resolver is version 3,** which picks versions compatible with your `rust-version`. Source: https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/
- **Raising the MSRV can break your users;** in a library treat it as a visible change. Source: https://doc.rust-lang.org/cargo/reference/semver.html#env-new-rust
- **`Cargo.lock` in git,** above all in binaries; `cargo new` already tracks it. Source: https://doc.rust-lang.org/cargo/faq.html#why-have-cargolock-in-version-control
- **Pin the toolchain with `rust-toolchain.toml`** in applications so CI and local machines compile the same way; uv pins `channel` to an exact version. Source: https://github.com/astral-sh/uv/blob/main/rust-toolchain.toml

## Workspaces

- **A workspace shares `Cargo.lock` and `target/`;** centralize versions in `[workspace.dependencies]` and lints in `[workspace.lints]`. Source: https://doc.rust-lang.org/cargo/reference/workspaces.html
- **Flat layout:** `crates/<name>` with the crate named the same as the folder, and the root as a virtual manifest. matklad: "the flat layout makes the most sense". Source: https://matklad.github.io/2021/08/22/large-rust-workspaces.html
- **Profiles only count in the root manifest.** Source: https://doc.rust-lang.org/cargo/reference/profiles.html
- **Migrate editions with `cargo fix --edition`.** Source: https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
