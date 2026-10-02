# Rendimiento

## Primero medir

- **Perfila para saber qué código está caliente.** Sin perfil, se optimiza lo que no importa. Fuente: https://nnethercote.github.io/perf-book/profiling.html
- **Mide en release.** El Perf Book: "10-100x speedups over dev builds are common!" Fuente: https://nnethercote.github.io/perf-book/build-configuration.html#release-builds
- **Deja info de línea en release para perfilar:** `debug = "line-tables-only"` en `[profile.release]`. uv lo usa en dev y midió un 20% menos de tiempo total. Fuentes: https://nnethercote.github.io/perf-book/profiling.html, https://github.com/astral-sh/uv/blob/main/Cargo.toml
- **Algoritmos y estructuras de datos ganan a los micro-trucos.** "The biggest performance improvements often come from changes to algorithms or data structures". Fuente: https://nnethercote.github.io/perf-book/general-tips.html

## Perfil de release para un binario

```toml
[profile.release]
lto = "fat"          # o "thin" si el tiempo de build importa
codegen-units = 1
panic = "abort"      # solo si nada depende de catch_unwind
```

ripgrep, uv y clap usan esta combinación. Fuentes: https://nnethercote.github.io/perf-book/build-configuration.html, https://github.com/BurntSushi/ripgrep/blob/master/Cargo.toml. `overflow-checks = true` en release hace que el desbordamiento entre en pánico en lugar de dar la vuelta; decide según el dominio: https://doc.rust-lang.org/cargo/reference/profiles.html#overflow-checks

## Asignaciones

- **Cada asignación cuesta** un lock global, gestión de estructuras y a veces una syscall. Fuente: https://nnethercote.github.io/perf-book/heap-allocations.html
- **`Vec::with_capacity` cuando conoces el tamaño; `clear()` para reutilizar un buffer en un bucle.** Fuente: misma página.
- **No asignes un `Vec` donde vale un iterador,** y no hagas `collect` para iterar otra vez. Devuelve `impl Iterator`. Fuentes: https://nnethercote.github.io/perf-book/iterators.html, guía de rust-analyzer ("Don't allocate a `Vec` where an iterator would do").
- **Empuja la asignación al llamador:** si la función va a guardar un `String`, recibe `String` y no `&str`. Fuente: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md
- **En recursión, un parámetro acumulador** en lugar de devolver una colección nueva en cada nivel. Fuente: misma guía.

## Tipos y hashing

- **`SipHash`, el hasher por defecto, es lento con claves cortas.** `FxHashMap` (`rustc-hash`) es mucho más rápido pero no resiste HashDoS; úsalo solo con claves que no controla un atacante. Fuente: https://nnethercote.github.io/perf-book/hashing.html. rust-analyzer y cargo lo imponen con `disallowed-types` en `clippy.toml`.
- **Mete en `Box` la variante grande y rara de un enum** para no inflar las demás. `clippy::large_enum_variant` lo señala. Fuente: https://nnethercote.github.io/perf-book/type-sizes.html
- **Itera en lugar de indexar** para que el compilador quite comprobaciones de rango. Fuente: https://nnethercote.github.io/perf-book/bounds-checks.html

## I/O

- **`println!` bloquea stdout en cada llamada.** En un bucle, toma `stdout().lock()` una vez. Fuente: https://nnethercote.github.io/perf-book/io.html
- **`BufReader`/`BufWriter` para lecturas y escrituras pequeñas.** Fuente: misma página.
- **Llama a `flush()` sobre el `BufWriter` al final:** el `Drop` ignora el error de flush. Fuente: misma página.

## Tiempo de compilación

- **Cuida el build antes de que duela.** matklad: arréglalo "before they become a problem"; en CI cachea dependencias, no los crates propios. Fuente: https://matklad.github.io/2021/09/04/fast-rust-builds.html
- **Nada de código genérico en las fronteras entre crates** y `#[inline]` solo en funciones pequeñas no genéricas de librería. Fuentes: la misma, y https://matklad.github.io/2021/07/09/inline-in-rust.html
