# Errores

## Result o pánico

- **`Result` es el valor por defecto de una función que puede fallar.** El Book: "Returning `Result` is a good default choice when you're defining a function that might fail." Fuente: https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html
- **Si el fallo es esperable, devuelve `Result`; si el código podría quedar en un estado inválido, entra en pánico.** Fuente: https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html#guidelines-for-error-handling
- **Un pánico es un bug, y `unwrap`/`expect` sirven para afirmar invariantes.** BurntSushi: "Panicking should not be used for error handling in either applications or libraries" y "correct Rust programs don't panic". Por eso "it is fine to use unwrap(), expect() and slice index syntax" cuando el pánico solo ocurre si hay un bug. Fuente: https://burntsushi.net/unwrap/
- **Prefiere `expect` a `unwrap` y escribe en el mensaje la invariante, no el síntoma.** BurntSushi: "Prefer expect() to unwrap(), since it gives more descriptive messages". `expect("the parser only emits non-empty names")` le dice al lector por qué no puede fallar. Fuente: https://burntsushi.net/unwrap/
- **En ejemplos y prototipos, `unwrap` es un marcador de lo que falta.** El Book lo llama "a placeholder for the way you'd want your application to handle errors". Fuente: https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html#examples-prototype-code-and-tests
- **En los ejemplos de documentación usa `?`, no `unwrap`.** La gente copia los ejemplos tal cual. Fuente: https://rust-lang.github.io/api-guidelines/documentation.html#examples-use--not-try-not-unwrap-c-question-mark
- **rust-analyzer va más lejos: `never!` en lugar de `assert!` y `catch_unwind` por petición**, porque un IDE no puede caerse por un bug. Aplica a servidores de larga vida, no a una CLI. Fuente: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md

## Qué tipo de error

La pregunta que decide, según Luca Palmieri: "Do you expect the caller to behave differently based on the failure mode they encountered?" Si la respuesta es no, "Use an opaque error". Fuente: https://www.lpalmieri.com/posts/error-handling-rust/

| Situación | Tipo | Fuente |
|---|---|---|
| Binario o capa de aplicación que solo reporta | `anyhow::Result` con `.context()` | anyhow README, https://github.com/dtolnay/anyhow |
| Librería cuyo llamador ramifica según el fallo | enum o struct propio, con `thiserror` o a mano | thiserror README, https://github.com/dtolnay/thiserror |
| Un solo fallo que el llamador sí distingue, dentro de una app con `anyhow` | struct propio y `err.downcast_ref::<T>()` | Palmieri, enlace arriba |
| Análisis que produce resultado parcial más diagnósticos | `(T, Vec<Error>)` en lugar de `Result<T, Error>` | rust-analyzer architecture.md |

- **dtolnay:** "Use thiserror if you care about designing your own dedicated error type(s) so that the caller receives exactly the information that you choose", y "Use Anyhow if you don't care what error type your functions return". `thiserror` "deliberately does not appear in your public API", así que cambiarlo por una impl a mano no rompe semver. Fuente: https://github.com/dtolnay/thiserror
- **Pon el error cerca de la unidad que falla.** Sabrina Jewson: "Error types should be located near to their unit of fallibility", y critica "just stick everything in a big enum". matklad llama antipatrón al "kitchen-sink enum" y pregunta primero "how the error will be used?". Fuentes: https://sabrinajewson.org/blog/errors, https://matklad.github.io/2020/10/15/study-of-std-io-error.html
- **Los tipos de error implementan `std::error::Error`, `Send` y `Sync`.** Sin `Send + Sync` no cruzan threads ni caben en `anyhow::Error`. Fuente: https://rust-lang.github.io/api-guidelines/interoperability.html#error-types-are-meaningful-and-well-behaved-c-good-err
- **Las librerías fundacionales escriben su error a mano.** `ignore` (de ripgrep) y `regex` implementan `std::error::Error` sin `thiserror`. Fuente: https://github.com/BurntSushi/ripgrep/blob/master/crates/ignore/src/lib.rs
- **axum no deja escapar errores del handler:** todo servicio tiene `Infallible` como error y el `Result` se convierte en `Response` con `IntoResponse`. Fuente: https://github.com/tokio-rs/axum/blob/main/axum/src/docs/error_handling.md

## Contexto y reporte

- **Cada llamada a `std::fs` y a otras rutinas de bajo nivel lleva contexto.** Cargo: "When using any low-level routines, such as `std::fs`, *always* add error context". Fuente: https://github.com/rust-lang/cargo/blob/master/doc/contrib/src/implementation/console.md
- **Registra el error donde lo manejas, no donde lo propagas.** Palmieri: "errors should be logged when they are handled"; una función que solo hace `?` "should not log the error". Si no, el mismo fallo aparece tres veces en el log. Fuente: https://www.lpalmieri.com/posts/error-handling-rust/
- **Imprime la cadena completa con `{:#}` en `main`.** ripgrep hace `run() -> anyhow::Result<ExitCode>`, recorre `err.chain()` para tratar `BrokenPipe` como salida limpia y si no imprime `{:#}` y sale con código 2. Fuente: https://github.com/BurntSushi/ripgrep/blob/master/crates/core/main.rs
- **Los mensajes de error empiezan en minúscula y no terminan en punto**, porque `anyhow` los encadena con `: `. rust-analyzer lo pide en su guía. Fuente: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md
- **Para lanzar un error, `return Err(e)` o `bail!`.** rust-analyzer prefiere el `return` explícito porque tiene tipo `!` y se lee como salida. Fuente: guía de estilo de rust-analyzer, enlace arriba.

## Documentación

- Toda función pública que devuelve error lleva `# Errors`, y la que puede entrar en pánico lleva `# Panics`. Aplica también a métodos de traits. Fuente: https://rust-lang.github.io/api-guidelines/documentation.html#function-docs-include-error-panic-and-safety-considerations-c-failure
- El lint `clippy::missing_errors_doc` y `clippy::missing_panics_doc` lo comprueban, pero uv y serde los desactivan por ruidosos en código que no es librería publicada. Decide según quién lee la API.
