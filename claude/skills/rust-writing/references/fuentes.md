# Fuentes

Consultadas el 2026-09-28. Las citas se comprobaron contra la página cargada; donde no se pudo, se dice.

## Documentación oficial

- **The Rust Programming Language (the Book).** https://doc.rust-lang.org/book/. El capítulo 9.3 da el criterio pánico o `Result` y la validación en tipos; el 11.3 la organización de tests; el 16 y el 17 threads frente a async; el 20.1 `unsafe`, SAFETY y miri. Es la base que todos los demás dan por sabida.
- **Rust API Guidelines.** https://rust-lang.github.io/api-guidelines/. Checklist con códigos (C-CONV, C-NEWTYPE, C-CUSTOM-TYPE, C-FAILURE...). Pensada para librerías publicadas; en un binario, las reglas de future-proofing pesan menos.
- **Rust Reference.** https://doc.rust-lang.org/reference/. Lista de comportamiento indefinido y contrato de `unsafe fn`. Su página de `unsafe` aún describe el comportamiento previo a edition 2024 dentro de `unsafe fn`; para eso vale la Edition Guide.
- **Edition Guide, Rust 2024.** https://doc.rust-lang.org/edition-guide/rust-2024/. `unsafe_op_in_unsafe_fn`, `unsafe extern`, `set_var` inseguro. La portada cargó; las subpáginas citadas también.
- **Rustonomicon.** https://doc.rust-lang.org/nomicon/. El argumento de que la frontera del `unsafe` es el módulo y no el bloque.
- **Clippy.** https://github.com/rust-lang/rust-clippy y https://doc.rust-lang.org/clippy/. Grupos, `clippy.toml`, `msrv`.
- **rustfmt y Style Guide.** https://github.com/rust-lang/rustfmt, https://doc.rust-lang.org/style-guide/. La Style Guide solo devolvió un resumen, no texto literal; las reglas de 4 espacios y 100 columnas coinciden con `tidy` de rustc.
- **Rust Design Patterns.** https://rust-unofficial.github.io/patterns/. Newtype, builder, RAII, `mem::take`, y los antipatrones `clone` para el borrow checker, `#![deny(warnings)]` y `Deref` como herencia. No es oficial del proyecto Rust.
- **Rust Performance Book** de Nicholas Nethercote. https://nnethercote.github.io/perf-book/. Perfiles, asignaciones, hashing, tamaños de tipo, I/O. Algunos enlaces internos apuntan a rust-lang.github.io/perf-book, posible mudanza.
- **Cargo Book.** https://doc.rust-lang.org/cargo/. Features, semver, `[lints]`, workspaces, perfiles, `rust-version`.
- **Blog oficial de Rust.** `async fn` en traits (https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/), 1.84 y el resolver MSRV (https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/), 1.85 y edition 2024 (https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/). Las URL con `.html` devuelven una redirección vacía; las de barra final cargan.

## Repos insignia

- **rust-analyzer.** Guía de estilo en https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md; la ruta antigua `docs/dev/style.md` ya no existe. Es la guía de estilo de código más concreta que existe en Rust: precondiciones en tipos, sin `should_panic`, sin setters, `anyhow` en todo el proyecto, pocas dependencias, tests guiados por datos con `expect-test`.
- **rust-lang/rust.** https://github.com/rust-lang/rust/blob/master/src/doc/rustc-dev-guide/src/conventions.md y `tidy`. Estados irrepresentables, match exhaustivo, comentarios que dicen por qué, `FIXME` y no `TODO`.
- **cargo.** https://github.com/rust-lang/cargo/tree/master/doc/contrib. `anyhow` con contexto obligatorio en `std::fs`, snapshots con `snapbox`, test en un commit previo al arreglo, `disallowed-methods` en `clippy.toml`.
- **ripgrep, regex, bstr (BurntSushi).** `main` que devuelve `ExitCode` y trata `BrokenPipe`; errores de librería escritos a mano; `max_width = 79`; no corre clippy en CI.
- **tokio.** https://github.com/tokio-rs/tokio/blob/master/docs/contributing/pull-requests.md. Evita unit tests, usa loom y miri, documenta cancel safety, CI con MSRV, semver, cargo-deny, minimal-versions.
- **serde.** `pedantic` en CI con una lista de allows agrupada por motivo en `lib.rs`.
- **clap.** La plantilla de lints de Ed Page en `[workspace.lints]`, la lista curada más completa de las revisadas.
- **axum.** `unsafe_code = "forbid"`, handlers con error `Infallible`, lints que empujan `#[must_use]`.
- **uv y ruff (Astral).** `pedantic` con allows, `disallowed-methods` para forzar `fs-err`, `thiserror` y `anyhow` en el mismo workspace, snapshots con `insta`, toolchain fijado.
- **tracing.** Copia las convenciones de tokio; umbrales en `clippy.toml`.

## Autores

- **matklad (Alex Kladov).** Push ifs up and fors down; How to test; Delete cargo integration tests; Large Rust workspaces; Fast Rust builds; Inline in Rust; Study of std::io::Error. Todo en https://matklad.github.io/. Aporta las reglas de diseño de funciones y tests más citadas por otros.
- **BurntSushi (Andrew Gallant).** https://burntsushi.net/unwrap/ y https://burntsushi.net/rust-error-handling/. El criterio "un pánico es un bug" y la postura conservadora con dependencias (README de Jiff). No encontré un texto equivalente específico de ripgrep sobre dependencias.
- **dtolnay.** READMEs de `anyhow` y `thiserror`, la división aplicación frente a librería.
- **Luca Palmieri.** https://www.lpalmieri.com/posts/error-handling-rust/. La pregunta de control de flujo frente a reporte y dónde registrar el error.
- **Sabrina Jewson.** https://sabrinajewson.org/blog/errors. Errores por unidad de falla, contra el enum único.
- **withoutboats.** Why async Rust, Let futures be futures, Thread-per-core, From failure to Fehler, en https://without.boats/blog/. Defensa del modelo de futures y del work-stealing; recomendó un trait object (`anyhow::Error`) para aplicaciones. "The registers of Rust" cargó pero no pude verificar citas literales.
- **Niko Matsakis.** Serie del problema del bound `Send`, https://smallcultfollowing.com/babysteps/series/send-bound-problem/, y metas de async para 2024.
- **Alice Ryhl.** https://ryhl.io/blog/async-what-is-blocking/ y https://ryhl.io/blog/actors-with-tokio/, más el tutorial de estado compartido de tokio.
- **Mara Bos.** Rust Atomics and Locks, libro libre en https://mara.nl/atomics/ (marabos.nl redirige ahí). Orden de memoria y duración de locks.
- **fasterthanlime (Amos).** https://fasterthanli.me/articles/pin-and-suffering. "Surviving Rust async interfaces" y "The curse of strong typing" cargaron, pero el extractor devolvió paráfrasis y no las cito. No tiene un artículo dedicado a `color-eyre`/`miette`.
- **Matt Klein** (https://bitbashing.io/async-rust.html) y **Matthias Endler** (https://corrode.dev/blog/async/). Las críticas a async más citadas.

## Fuentes que no pude leer o citar

- **Rust for Rustaceans, Jon Gjengset.** O'Reilly devolvió 403; No Starch solo muestra el índice (cap. 3 Designing Interfaces, 4 Error Handling, 6 Testing, 8 Asynchronous Programming, 9 Unsafe Code). No cito su contenido. No pude confirmar que el capítulo 3 se organice en "unsurprising, flexible, obvious, constrained", aunque se repite en la web.
- **Zero to Production, Luca Palmieri.** No lo leí; cito su artículo de errores, que es un capítulo del libro publicado en su blog.
- **Rust Foundation.** No encontré publicaciones con reglas de estilo de código; no la cito.
- Artículos de fasterthanlime y withoutboats citados arriba como sin verificar.

## Dónde no están de acuerdo

1. **`anyhow` en librerías.** dtolnay: `thiserror` en librerías, `anyhow` en aplicaciones. Palmieri parte de otro criterio: si el llamador no va a ramificar, un error opaco sirve también en una librería. withoutboats recomendó un trait object para aplicaciones. Sabrina Jewson ni siquiera usaría `thiserror` en una librería: "it's really not that many lines of code saved for a whole extra dependency". BurntSushi escribe los errores a mano en `regex` e `ignore`, en línea con Jewson. **Qué hago:** en Hydra, que es un binario con una lib interna, `anyhow` más structs de error concretos donde el llamador ramifica es coherente con los cuatro.
2. **Un enum de error por crate frente a errores por función.** La práctica común es un `Error` por crate. matklad lo llama "kitchen-sink enum" y Jewson pide un tipo por unidad de falla. Nadie de los revisados defiende por escrito el enum único.
3. **`unwrap`.** BurntSushi: bien para invariantes, porque un pánico es un bug. El Book lo trata como marcador de prototipo. rust-analyzer va al otro extremo con `never!` para no caerse nunca. La regla popular "nunca `unwrap`" no la encontré firmada por nadie reconocido.
4. **Async.** withoutboats defiende futures sin pila y work-stealing. Klein y Endler dicen que el multithread por defecto trae complejidad que la mayoría no necesita y que los threads bastan. Niko reconoce el problema del bound `Send` como deuda abierta.
5. **Mutex en async.** tokio y Ryhl: `std::sync::Mutex` está bien si no cruza un `.await`; el error común es usar `tokio::sync::Mutex` siempre.
6. **Organización de tests.** El Book enseña `mod tests` por fichero más `tests/` con un fichero por test. matklad pide un único crate de integración con módulos y, en librerías, evitar unit tests. tokio, tracing y axum también evitan unit tests.
7. **Genéricos en la API.** API Guidelines C-GENERIC pide genéricos para aceptar más tipos de entrada. rust-analyzer pide evitarlos en fronteras entre crates y evitar el polimorfismo `AsRef`, por el coste de monomorfización en el build. Las Guidelines optimizan para el usuario de una librería; rust-analyzer para el tiempo de compilación de un proyecto grande.
8. **`#[must_use]`.** axum lo empuja con `must_use_candidate`; uv y serde desactivan ese mismo lint por ruidoso.
9. **Clippy en CI.** Casi todos corren `clippy -D warnings`. ripgrep no corre clippy.
10. **Dependencias.** BurntSushi y rust-analyzer son conservadores; Jewson rechaza `thiserror` por ser dependencia. dtolnay contesta que `thiserror` no aparece en la API pública, así que quitarlo luego no rompe nada. No encontré un texto firmado que defienda usar crates con libertad.

## Hydra frente a estas prácticas

Revisado el 2026-09-28 sobre `~/hydra` sin modificarlo. Rutas relativas a esa carpeta.

1. **No hay `[lints]` en `Cargo.toml` ni `clippy.toml`.** `Cargo.toml:1-24` solo tiene paquete y dependencias, y CI corre clippy con los grupos por defecto (`.github/workflows/ci.yml`, paso `cargo clippy --all-targets -- -D warnings`). Faltan los lints que repiten casi todos los repos insignia: `undocumented_unsafe_blocks`, `dbg_macro`, `todo`, `unreachable_pub`. `unsafe_op_in_unsafe_fn` ya avisa por defecto con edition 2024. Cumple lo importante: warnings a error en CI y no con `#![deny(warnings)]` en el código.
2. **Bloques `unsafe` sin `// SAFETY:`.** `src/pty.rs:216`, `226`, `343`, `348`, `400` y `404` (`poll`, `read`, `fcntl`) y `src/procinfo.rs:29` y `51` (`sysctl`) no llevan comentario. `src/env.rs:193` explica en `:192` por qué `getpwuid` es aceptable, pero sin la etiqueta `SAFETY` que busca el lint. En contraste, `src/worktree.rs:610-671` es el modelo a copiar: un SAFETY por bloque y `OwnedFd::from_raw_fd` inmediatamente después de `open` en `:622`.
3. **Un descriptor crudo en un struct.** `src/pty.rs:67` guarda `pty_fd: libc::c_int`, obtenido en `:131` de `pair.master.as_raw_fd()`. Es válido solo mientras vive `_master` en `:60`; nada en el tipo lo expresa. Un `BorrowedFd<'_>` o leer siempre a través de `_master` pondría esa dependencia en el tipo, como pide la regla de la frontera de módulo del Rustonomicon.
4. **Strings para conjuntos cerrados.** `src/run.rs:67` tiene `policy: String` y `src/run.rs:90` tiene `command: String` con comentario "`run` or `resume`"; los llamadores escriben el literal a mano en `src/main.rs:48`, `src/face.rs:364`, `src/interactive.rs:346`, `src/interactive.rs:464` y `src/resume.rs:123`. Un enum `Command { Run, Resume }` convertiría un typo en error de compilación. `Provider` ya lo hace bien: `src/provider/mod.rs:363` implementa `FromStr` y `main.rs` parsea en el borde.
5. **Errores: `anyhow` con structs concretos donde el llamador ramifica.** `src/run.rs:322-345` define `TooDeep` y `src/live.rs:424-453` define `TooManyLive`, ambos con `Display` y `std::error::Error`, y `tests/status.rs:517` hace `downcast_ref::<live::TooManyLive>()`. Es justo el patrón de Palmieri: opaco por defecto, concreto donde hace falta. Ninguno de los dos se consume con `downcast` dentro de `src/`, así que hoy solo los tests los distinguen.
6. **Pánico sin `# Panics`.** `src/run.rs:2039-2051`: `append_resume_args` es `pub` y hace `expect` sobre `hook_file` y sobre el `argv`, pero su doc comment en `:2039` no tiene sección `# Panics`. Los mensajes de `expect` sí nombran la invariante, como pide BurntSushi.
7. **Veintisiete binarios de tests de integración.** `tests/` tiene 27 ficheros `.rs` en la raíz más `tests/common/mod.rs`; cada uno se enlaza como binario aparte. Es el caso que matklad describe en "Delete cargo integration tests". CONTRIBUTING exige además `--test-threads=1`, lo que suma tiempo. `tests/common/mod.rs` sí sigue la forma que pide el Book.
8. **Doc de crate desactualizado.** `src/lib.rs:3` dice "It launches two providers, `claude` and `cursor-agent`", y `CLAUDE.md` describe cuatro. No es una regla de estilo de Rust pero sí la de rustc de que los comentarios digan la verdad del porqué; un doc que miente cuesta más que uno ausente.
9. **Todo es `pub mod`.** `src/lib.rs:20-54` expone los 35 módulos, porque los tests de integración en `tests/` necesitan verlos. No hay `unreachable_pub`, así que no se distingue lo que es API de lo que es público solo por los tests.
10. **Lo que ya cumple.** `edition = "2024"` y `rust-version = "1.88"` en `Cargo.toml:4-5`; `Cargo.lock` versionado; 11 dependencias directas sin crates de ayuda y sin runtime async, con I/O síncrono sobre `poll(2)` en `src/pty.rs`, que es lo que Endler recomienda para este tamaño de concurrencia; contexto en los errores de syscall (`src/pty.rs:222`, `:402`, `:406`); la lógica vive en la lib y `src/main.rs` solo parsea con clap y despacha, aunque su `match` ya ocupa 232 líneas. CONTRIBUTING pide `cargo clippy -- -D warnings` sin `--all-targets` y CI sí lo pasa, así que el documento se queda corto frente al CI.
