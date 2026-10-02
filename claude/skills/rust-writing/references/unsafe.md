# Unsafe

## Antes de escribirlo

- **Busca primero la versión segura.** `std::os::fd::OwnedFd` y `BorrowedFd` en lugar de `c_int`; `nix` o `rustix` en lugar de `libc` directo cuando la dependencia es aceptable; `std::fs` en lugar de `open(2)`. Cada bloque que no escribes es uno que no auditas.
- **Si el crate no necesita `unsafe`, prohíbelo:** `unsafe_code = "forbid"` en `[lints.rust]`. axum lo hace. uv y ruff lo dejan en `"warn"` para que cada uso destaque. Fuentes: https://github.com/tokio-rs/axum/blob/main/Cargo.toml, https://github.com/astral-sh/uv/blob/main/Cargo.toml

## Reglas del bloque

- **Bloques pequeños.** El Book: "Keep `unsafe` blocks small; you'll be thankful later when you investigate memory bugs." Un bloque por operación insegura, no uno que envuelve la función entera. Fuente: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#performing-unsafe-superpowers
- **Cada bloque lleva `// SAFETY:` justo encima** con la condición que lo hace correcto, no con lo que hace la llamada. Fuente: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html. Actívalo con `clippy::undocumented_unsafe_blocks`, del grupo restriction, que se activa lint por lint: https://rust-lang.github.io/rust-clippy/master/index.html#undocumented_unsafe_blocks
- **Una `unsafe fn` documenta `# Safety`** con todo lo que el llamador debe cumplir, porque el compilador no lo comprueba. Fuentes: https://rust-lang.github.io/api-guidelines/documentation.html#function-docs-include-error-panic-and-safety-considerations-c-failure, https://doc.rust-lang.org/reference/unsafe-keyword.html
- **Dentro de una `unsafe fn`, cada operación insegura va en su propio bloque `unsafe`.** En edition 2024 `unsafe_op_in_unsafe_fn` avisa por defecto. Fuente: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html
- **En edition 2024 los bloques `extern` se escriben `unsafe extern "C" { ... }`** y `std::env::set_var`/`remove_var` son `unsafe`. Fuente: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html

## La frontera es el módulo

- **Envuelve el `unsafe` en una API segura.** El Book: "it's best to enclose such code within a safe abstraction and provide a safe API". Fuente: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html
- **La privacidad del módulo es lo único que acota el `unsafe`.** Rustonomicon: "the only bullet-proof way to limit the scope of unsafe code is at the module boundary with privacy." Un campo privado que el `unsafe` da por válido no debe poder cambiarse desde fuera del módulo. Fuente: https://doc.rust-lang.org/nomicon/working-with-unsafe.html
- **Audita el módulo entero, no solo el bloque.** "The soundness of our unsafe operations necessarily depends on the state established by otherwise 'safe' operations." Fuente: misma página.
- **No confíes en código seguro genérico.** Un `Ord` o un `Hash` del usuario puede estar mal y tu `unsafe` no puede provocar UB por eso. Fuente: https://doc.rust-lang.org/nomicon/safe-unsafe-meaning.html
- **El código seguro que llama al tuyo nunca debe poder provocar UB.** La lista de UB de la Reference "is not exhaustive"; producir un valor inválido ya es UB, aunque no se lea. Fuente: https://doc.rust-lang.org/reference/behavior-considered-undefined.html

## FFI y syscalls

- **Comprueba el retorno de cada syscall y convierte con `std::io::Error::last_os_error()`** en el mismo sitio, antes de cualquier otra llamada que pueda pisar `errno`.
- **Un descriptor tiene un solo dueño.** `OwnedFd::from_raw_fd` justo después de `open`, y préstamos con `BorrowedFd<'_>` ligados a la vida del dueño. Un `c_int` guardado en un struct no dice quién lo cierra ni cuándo deja de ser válido. Fuente: https://doc.rust-lang.org/std/os/fd/index.html
- **Funciones no reentrantes de libc** (`getpwuid`, `strerror`, `readdir` compartido) necesitan que el SAFETY diga por qué no hay otro thread llamándolas, o una variante `_r`.

## Verificación

- `cargo miri test` detecta UB en lógica de punteros y aliasing; no ejecuta FFI real. Fuente: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-miri-to-check-unsafe-code
- tokio y serde corren miri en CI con `-Zmiri-strict-provenance`. Fuentes: https://github.com/tokio-rs/tokio/blob/master/.github/workflows/ci.yml, https://github.com/serde-rs/serde/blob/master/.github/workflows/ci.yml
