# Tooling: clippy, rustfmt, lints y CI

## Clippy

- **Grupos por defecto:** `correctness` en deny; `suspicious`, `style`, `complexity` y `perf` en warn; `pedantic`, `nursery` y `cargo` apagados. Fuente: https://github.com/rust-lang/rust-clippy/blob/master/README.md
- **El grupo `restriction` nunca entero.** El README: "The `restriction` category should, _emphatically_, not be enabled as a whole." Se escogen lints sueltos. Fuente: misma página.
- **Tres estilos en los repos insignia:**
  - `pedantic` activado con allows justificados: uv, ruff, serde.
  - Lista curada de lints sueltos: clap y axum.
  - Mínimo: cargo (`all = allow` más `correctness`) y rust-analyzer (grupos por defecto, `perf` en deny).
  Para un proyecto pequeño, la lista curada da más señal por lint. Fuentes: https://github.com/astral-sh/uv/blob/main/Cargo.toml, https://github.com/clap-rs/clap/blob/master/Cargo.toml, https://github.com/rust-lang/cargo/blob/master/Cargo.toml
- **Cada `allow` lleva su motivo en un comentario.** serde agrupa sus allows por razón: "clippy bug", "noisy", "preference", "false positive". Fuente: https://github.com/serde-rs/serde/blob/master/serde/src/lib.rs
- **`clippy.toml` sirve para `disallowed-methods` y `disallowed-types` con motivo,** y así obliga a usar el wrapper del proyecto: `std::env::var` prohibido en cargo ("use `Config::get_env` instead"), `std::fs` prohibido en uv para forzar `fs-err`, `HashMap` prohibido en rust-analyzer a favor de `FxHashMap`. Fuentes: https://github.com/rust-lang/cargo/blob/master/clippy.toml, https://github.com/astral-sh/uv/blob/main/clippy.toml
- **Declara `msrv` o `rust-version`** para que clippy no sugiera APIs más nuevas que tu mínimo. Fuente: https://doc.rust-lang.org/clippy/configuration.html

## Lints en Cargo.toml

- **Los niveles van en `[lints]` de Cargo.toml**, no como `#![warn(...)]` repartidos por el código; Cargo los aplica al paquete y no a las dependencias. `priority` ordena grupos frente a lints sueltos. Fuente: https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section
- **Nunca `#![deny(warnings)]` en el código fuente:** una versión nueva del compilador añade un warning y tu crate deja de compilar para todos. Sube warnings a error en CI con `-D warnings`. Fuente: https://rust-unofficial.github.io/patterns/anti_patterns/deny-warnings.html

Punto de partida para un binario, sacado de los lints que se repiten en rust-analyzer, clap, axum y uv:

```toml
[lints.rust]
unsafe_op_in_unsafe_fn = "warn"
unreachable_pub = "warn"
unused_qualifications = "warn"

[lints.clippy]
dbg_macro = "warn"
todo = "warn"
print_stderr = "warn"          # quítalo si el binario escribe a stderr a propósito
undocumented_unsafe_blocks = "warn"
str_to_string = "warn"
use_self = "warn"
await_holding_lock = "warn"    # solo si hay async
```

## rustfmt

- **Formato por defecto,** que sigue la Rust Style Guide: 4 espacios, 100 columnas, comas finales en listas multilínea. Fuentes: https://github.com/rust-lang/rustfmt/blob/master/README.md, https://doc.rust-lang.org/style-guide/index.html
- **`rustfmt.toml` mínimo o ninguno.** cargo, uv y ruff solo fijan `style_edition = "2024"`; tokio y serde no tienen fichero. rustc añade `group_imports = "StdExternalCrate"` e `imports_granularity = "Module"`, que requieren nightly. BurntSushi usa `max_width = 79`. Fuentes: https://github.com/rust-lang/rust/blob/master/rustfmt.toml, https://github.com/BurntSushi/ripgrep/blob/master/rustfmt.toml

## CI

El CI que comparten tokio, axum, clap, cargo, uv y ruff:

```
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo test --workspace --locked
```

Más, según el proyecto:

- Un job de MSRV que compila con la versión de `rust-version`.
- `cargo deny check` para licencias, avisos de seguridad y duplicados (tokio, axum, clap, cargo, uv, ruff).
- `-Z minimal-versions` para comprobar que los mínimos declarados compilan (serde, clap, tokio, tracing).
- `cargo semver-checks` en librerías publicadas (cargo, tokio).
- miri si hay `unsafe` con punteros (tokio, serde).

`--all-targets` importa: sin él clippy no mira tests, benches ni ejemplos. ripgrep es la excepción conocida: no corre clippy en CI. Fuentes: https://github.com/tokio-rs/tokio/blob/master/.github/workflows/ci.yml, https://github.com/tokio-rs/axum/blob/main/.github/workflows/CI.yml, https://github.com/BurntSushi/ripgrep/blob/master/.github/workflows/ci.yml

## Convenciones de comentarios

- **Los comentarios dicen por qué.** "Write comments that say *why*." Fuente: https://github.com/rust-lang/rust/blob/master/src/doc/rustc-dev-guide/src/conventions.md
- **`// FIXME` para lo pendiente,** `tidy` rechaza `TODO` en rustc. Fuente: misma página.
- **Refactor puro en su propio commit.** Fuente: misma página.
