---
name: rust-writing
description: Reglas para escribir Rust idiomático, con fuente. Úsalo al escribir, revisar o refactorizar código Rust o un Cargo.toml.
---

# Escribir Rust

Reglas ordenadas por cuántos errores evitan. Cada una lleva su porqué en una línea; la fuente y el detalle están en `references/`. Si el repo tiene sus propias reglas (CLAUDE.md, CONTRIBUTING, `clippy.toml`, `[lints]`), mandan ellas.

## Reglas

1. **Pon la invariante en un tipo.** Un newtype o un enum en lugar de `String`, `bool` o `Option` sueltos; parsea una vez en el borde y el compilador garantiza el resto. Ver [api-y-tipos](references/api-y-tipos.md).
2. **`Result` para lo que puede fallar, pánico solo para bugs.** Un fallo esperado es un valor que el llamador maneja; un pánico dice que el programa tiene un bug. Usa `expect("la invariante que se rompió")` antes que `unwrap()`. Ver [errores](references/errores.md).
3. **Elige el tipo de error por lo que hará el llamador.** Si va a ramificar según el fallo, dale un tipo concreto; si solo lo reporta, `anyhow` con `.context()` basta. Un enum de error por crate que lo junta todo es el antipatrón que critican matklad y Sabrina Jewson. Ver [errores](references/errores.md).
4. **Añade contexto a cada operación de I/O.** `fs::read(&path).with_context(|| format!("reading {}", path.display()))`; un `No such file or directory` sin ruta no se puede depurar.
5. **Cada bloque `unsafe` es mínimo y lleva `// SAFETY:`** con la condición que lo hace correcto, dentro de una API segura cuyo módulo protege la invariante. La corrección de `unsafe` depende del código seguro que lo rodea. Ver [unsafe](references/unsafe.md).
6. **Sube los `if` al llamador y baja los `for` a la función.** Las precondiciones van en el tipo del parámetro, no en un chequeo dentro del callee; así se ve el flujo de control y se procesa en lote.
7. **Recibe el tipo prestado más general** (`&str`, `&[T]`, `Option<&T>`) y toma ownership cuando la función lo va a guardar. Un `clone()` para callar al borrow checker suele esconder un diseño de ownership equivocado.
8. **Un `bool` como argumento se convierte en enum o en dos funciones.** `open(true)` no dice nada en el sitio de la llamada.
9. **Prueba comportamiento en el borde, no la implementación.** Tests guiados por datos con una función `check(input, expected)`, snapshots para salidas largas, sin `#[should_panic]` ni `#[ignore]`. Ver [tests](references/tests.md).
10. **Async solo para I/O concurrente.** Entre dos `.await` no pasan más de 10 a 100 µs; lo bloqueante va a `spawn_blocking` o a un thread. Un `std::sync::Mutex` sirve en async si no cruza un `.await`. Ver [async-y-concurrencia](references/async-y-concurrencia.md).
11. **Mutex o canales antes que atomics; `Acquire`/`Release` antes que `SeqCst`.** Mara Bos: `SeqCst` casi nunca hace falta y suele indicar que nadie analizó el orden.
12. **Documenta `# Errors`, `# Panics` y `# Safety`** en toda función pública que devuelva error, pueda entrar en pánico o sea `unsafe`. El comentario explica el porqué, no el qué.
13. **Pocas dependencias, features aditivas, `Cargo.lock` versionado en binarios, `rust-version` declarado.** Cada crate es código que auditas y compilas. Ver [dependencias](references/dependencias.md).
14. **Mide antes de optimizar, y mide en `--release`.** Los cambios de algoritmo y de asignaciones ganan a los micro-trucos. Ver [rendimiento](references/rendimiento.md).
15. **Los lints viven en `[lints]` de Cargo.toml y CI los sube a error.** Nunca `#![deny(warnings)]` en el código: rompe el build con cada versión nueva del compilador. Ver [tooling](references/tooling.md).

## Antes de dar el trabajo por hecho

Corre, en este orden, y deja los cuatro en verde:

```
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
cargo doc --no-deps   # solo si tocaste docs públicas
```

Si el repo define otros comandos (CONTRIBUTING, CI), usa los suyos. Un `#[allow(clippy::...)]` nuevo lleva un comentario con el motivo.

## Referencias

- [errores](references/errores.md): `anyhow` frente a `thiserror` frente a errores a mano, contexto, logging, pánicos.
- [api-y-tipos](references/api-y-tipos.md): newtypes, nombres, traits comunes, builders, visibilidad, semver.
- [tests](references/tests.md): organización, snapshots, fixtures, loom y miri.
- [async-y-concurrencia](references/async-y-concurrencia.md): threads frente a async, bloqueo, mutex, atomics, `Send`.
- [unsafe](references/unsafe.md): SAFETY, módulos como frontera, FFI, miri.
- [rendimiento](references/rendimiento.md): perfilado, perfiles de release, asignaciones, hashing, I/O.
- [tooling](references/tooling.md): clippy, rustfmt, `[lints]`, CI.
- [dependencias](references/dependencias.md): criterio para añadir crates, features, MSRV, lockfile.
- [fuentes](references/fuentes.md): bibliografía comentada, desacuerdos entre autores y cómo queda Hydra frente a estas reglas.
