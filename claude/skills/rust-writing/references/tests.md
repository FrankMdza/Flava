# Tests

## Qué probar

- **Prueba funcionalidades en el borde del sistema, no funciones sueltas.** matklad: "test features, not code! Test at the boundaries." Un test que llama a un helper privado se rompe en cada refactor sin haber encontrado un bug. Fuente: https://matklad.github.io/2021/05/31/how-to-test.html
- **Haz que añadir un test cueste una línea.** matklad: "work hard on making adding new tests trivial". En la práctica, una función `check(input, expected)` y cada test es una llamada. Fuente: misma página.
- **Separa la lógica del I/O para poder probarla sin disco ni red.** matklad: "keep as much as possible sans io". Fuente: misma página.
- **rust-analyzer escribe tests guiados por datos que no tocan la API interna**: "tests are data driven and do not test the API". Así puede reescribir la implementación sin tocar los tests. Fuente: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md

## Cómo escribirlos

- **Snapshots para salidas largas.** Cada proyecto grande usa uno: `insta` en uv y ruff, `snapbox`/`trycmd` en cargo y clap, `expect-test` en rust-analyzer. Se regeneran con un comando (`cargo insta review`, `SNAPSHOTS=overwrite cargo test`, `UPDATE_EXPECT=1`). Fuentes: https://github.com/astral-sh/uv/blob/main/CONTRIBUTING.md, https://github.com/rust-lang/cargo/blob/master/doc/contrib/src/tests/writing.md
- **Fixtures multilínea como raw strings sin indentar.** Fuente: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md
- **Sin `#[should_panic]`:** comprueba `None` o `Err` de forma explícita. Un `should_panic` pasa también si el pánico viene de otro sitio. Fuente: guía de rust-analyzer.
- **Sin `#[ignore]`:** si el comportamiento está mal, el test afirma el comportamiento actual con un `// FIXME` y así se entera cuando cambia. Fuente: guía de rust-analyzer.
- **Marcas de cobertura** (`cov_mark::hit!` en el código, `cov_mark::check!` en el test) para demostrar que un test recorre la rama que dice. Fuente: guía de rust-analyzer.
- **El test del bug va en un commit anterior al arreglo.** Cargo y clap lo piden: así el historial muestra el test en rojo y luego en verde. Fuentes: https://github.com/rust-lang/cargo/blob/master/doc/contrib/src/process/working-on-cargo.md, https://github.com/clap-rs/clap/blob/master/CONTRIBUTING.md

## Organización

- **Unit tests en `mod tests` con `#[cfg(test)]` en el mismo fichero;** pueden probar funciones privadas. Fuente: https://doc.rust-lang.org/book/ch11-03-test-organization.html
- **Tests de integración en `tests/`, que solo ven la API pública.** Para eso la lógica vive en `src/lib.rs` y `main.rs` es fino. Fuente: misma página.
- **Helpers compartidos en `tests/common/mod.rs`**, no en `tests/common.rs`, para que no se compile como un test más. Fuente: misma página.
- **Un solo crate de integración con varios módulos, no un fichero por test.** Cada fichero de `tests/` es un binario que se enlaza por separado. matklad: "large projects should have only one integration test crate with several modules"; en su caso bajó de 20 a 13 segundos. Fuente: https://matklad.github.io/2021/02/27/delete-cargo-integration-tests.html. El patrón: `tests/it/main.rs` con `mod foo; mod bar;`.
- **tokio, tracing y axum evitan unit tests** y prefieren tests de integración y doctests. tokio: "Tokio avoids unit tests as much as possible". Fuente: https://github.com/tokio-rs/tokio/blob/master/docs/contributing/pull-requests.md

## Concurrencia y unsafe

- **`loom` para explorar interleavings de código concurrente de bajo nivel.** tokio lo corre con `RUSTFLAGS="--cfg loom -C debug_assertions"`. Fuente: https://github.com/tokio-rs/tokio/blob/master/docs/contributing/pull-requests.md
- **`cargo miri test` para código con `unsafe`,** con `-Zmiri-strict-provenance` como tokio y serde. Miri no ve FFI a libc real, así que sirve para lógica de punteros, no para syscalls. Fuente: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-miri-to-check-unsafe-code
- **Un test que toca variables de entorno del proceso va en su propio binario con un lock**, porque `set_var` afecta a los threads que corren otros tests; en edition 2024 `set_var` además es `unsafe`. Fuente: https://doc.rust-lang.org/edition-guide/rust-2024/newly-unsafe-functions.html

## Herramientas

- `cargo nextest` corre cada test en su propio proceso y más rápido; lo usan uv y tokio. Fuente: https://github.com/astral-sh/uv/blob/main/CONTRIBUTING.md
- `clippy.toml` con `allow-unwrap-in-tests = true` y `allow-expect-in-tests = true` si activas `unwrap_used`/`expect_used`. Fuente: https://github.com/clap-rs/clap/blob/master/.clippy.toml
