# Dependencias y Cargo

## Añadir un crate

- **Pocas dependencias, y ninguna para ahorrar diez líneas.** rust-analyzer: "Don't use small "helper" crates (exception: `itertools` and `either` are allowed)." BurntSushi, sobre Jiff: "my philosophy on adding new dependencies in an ecosystem crate like Jiff is very conservative". Fuentes: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md, https://github.com/BurntSushi/jiff
- **Antes de añadir, mira el árbol que arrastra:** `cargo tree -e normal -i <crate>` y `cargo tree -d` para duplicados.
- **Desactiva las features por defecto que no uses** (`default-features = false`). Menos código, menos build.
- **Crates asentados antes que nuevos** para lo que es infraestructura: `serde`, `anyhow`/`thiserror`, `clap`, `tokio` si hay async. Endler, sobre async: "stick to Tokio and well-established libraries like reqwest and sqlx." Fuente: https://corrode.dev/blog/async/
- **`cargo deny`** para licencias, avisos de RustSec y fuentes permitidas; lo corren tokio, axum, clap, cargo, uv y ruff.

## Features

- **Las features son aditivas:** activar una nunca quita funcionalidad y cualquier combinación compila. Cargo unifica features entre todo el grafo. Fuente: https://doc.rust-lang.org/cargo/reference/features.html
- **Evita features mutuamente excluyentes;** si no hay más remedio, `compile_error!` con un mensaje claro. Fuente: misma página.
- **Mover código público detrás de una feature rompe semver.** Fuente: https://doc.rust-lang.org/cargo/reference/features.html#semver-compatibility

## Versiones

- **Declara `rust-version`** y pruébalo en CI. Fuentes: https://doc.rust-lang.org/cargo/reference/manifest.html#the-rust-version-field, https://doc.rust-lang.org/cargo/reference/rust-version.html
- **Con edition 2024 el resolver es el 3,** que elige versiones compatibles con tu `rust-version`. Fuente: https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/
- **Subir la MSRV puede romper a tus usuarios;** en una librería trátalo como cambio visible. Fuente: https://doc.rust-lang.org/cargo/reference/semver.html#env-new-rust
- **`Cargo.lock` en git,** sobre todo en binarios; `cargo new` ya lo versiona. Fuente: https://doc.rust-lang.org/cargo/faq.html#why-have-cargolock-in-version-control
- **Fija el toolchain con `rust-toolchain.toml`** en aplicaciones para que CI y máquinas locales compilen igual; uv fija `channel` a una versión exacta. Fuente: https://github.com/astral-sh/uv/blob/main/rust-toolchain.toml

## Workspaces

- **Un workspace comparte `Cargo.lock` y `target/`;** centraliza versiones en `[workspace.dependencies]` y lints en `[workspace.lints]`. Fuente: https://doc.rust-lang.org/cargo/reference/workspaces.html
- **Diseño plano:** `crates/<nombre>` con el crate llamado igual que la carpeta, y la raíz como manifiesto virtual. matklad: "the flat layout makes the most sense". Fuente: https://matklad.github.io/2021/08/22/large-rust-workspaces.html
- **Los perfiles solo cuentan en el manifiesto raíz.** Fuente: https://doc.rust-lang.org/cargo/reference/profiles.html
- **Migra de edition con `cargo fix --edition`.** Fuente: https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
