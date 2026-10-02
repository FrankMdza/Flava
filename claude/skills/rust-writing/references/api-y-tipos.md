# API y tipos

## Invariantes en el tipo

- **Haz irrepresentables los estados inválidos.** Es una convención escrita del compilador de Rust. Fuente: https://github.com/rust-lang/rust/blob/master/src/doc/rustc-dev-guide/src/conventions.md
- **Valida una vez al construir el tipo y confía en él después.** El Book, sobre un tipo `Guess` que solo se construye entre 1 y 100: "you can proceed with your code's logic knowing that the compiler has already ensured that you have a valid value." Fuente: https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html#custom-types-for-validation
- **Usa newtypes para separar significados del mismo tipo base.** Un `RunId(String)` y un `PolicyName(String)` no se confunden en un argumento. Coste en runtime cero. Fuentes: https://rust-lang.github.io/api-guidelines/type-safety.html#newtypes-provide-static-distinctions-c-newtype, https://rust-unofficial.github.io/patterns/patterns/behavioural/newtype.html
- **Un valor de un conjunto cerrado de strings es un enum con `FromStr`**, no un `String` comparado con literales. Un typo en `"resmue"` compila; en `Command::Resmue` no.
- **Expresa las precondiciones en los tipos y obliga al llamador a darlas.** rust-analyzer: "Express function preconditions in types and force the caller to provide them (rather than checking in callee)". Su ejemplo malo recibe `Option<Walrus>` para luego comprobar `None`. Fuente: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md
- **Sube los `if` y baja los `for`.** matklad: "If there's an `if` condition inside a function, consider if it could be moved to the caller instead". Los bucles van dentro de la función que procesa un lote. Fuente: https://matklad.github.io/2023/11/15/push-ifs-up-and-fors-down.html

## Argumentos

- **`bool` y `Option` como argumento se sustituyen por un tipo con nombre.** API Guidelines: "Core types like `bool` have many possible interpretations." rust-analyzer: si una función siempre se llama con `true`, `false`, `Some` o `None` literales, "split the function in two". Fuentes: https://rust-lang.github.io/api-guidelines/type-safety.html#arguments-convey-meaning-through-types-not-bool-or-option-c-custom-type, guía de rust-analyzer.
- **Recibe el tipo prestado:** `&str` sobre `&String`, `&[T]` sobre `&Vec<T>`, `Option<&T>` sobre `&Option<T>`. Fuentes: https://rust-unofficial.github.io/patterns/idioms/coercion-arguments.html, guía de rust-analyzer ("always prefer types on the left").
- **Si la función necesita ownership, tómalo** en lugar de pedir `&T` y clonar dentro. El llamador decide si clona. Fuente: https://rust-lang.github.io/api-guidelines/flexibility.html#caller-decides-where-to-copy-and-place-data-c-caller-control
- **Muchos parámetros se agrupan en un struct `Config`.** rust-analyzer además pide no implementar `Default` para ese `Config`, así cada llamador decide cada campo. Fuente: guía de rust-analyzer.
- **Para construcción incremental con muchos opcionales, un builder.** Rust no tiene sobrecarga ni valores por defecto en parámetros. Fuentes: https://rust-lang.github.io/api-guidelines/type-safety.html#builders-enable-construction-of-complex-values-c-builder, https://rust-unofficial.github.io/patterns/patterns/creational/builder.html
- **Genéricos con moderación en fronteras entre crates.** rust-analyzer: "Avoid making a lot of code type parametric, *especially* on the boundaries between crates", y "Avoid `AsRef` polymorphism", porque cada instancia se monomorfiza y el build se alarga. Contrasta con API Guidelines C-GENERIC, que pide genéricos para aceptar más entradas. Ver el desacuerdo en [fuentes](fuentes.md).

## Nombres

- Conversiones: `as_` barato y prestado, `to_` caro, `into_` consume. Fuente: https://rust-lang.github.io/api-guidelines/naming.html
- Getters sin prefijo `get_`. Fuente: misma página, C-GETTER.
- Iteradores: `iter`, `iter_mut`, `into_iter`. Fuente: misma página, C-ITER.
- `UpperCamelCase` para tipos, `snake_case` para valores. Fuente: misma página, C-CASE.
- Variables locales con nombres largos y aburridos; convenciones `res`, `it`, `n_foos`, `foo_idx`. Fuente: guía de rust-analyzer.

## Traits

- **Implementa pronto los traits comunes** que apliquen: `Debug`, `Clone`, `PartialEq`, `Eq`, `Hash`, `Default`, `Display`. Un tipo público sin `Debug` es un fastidio para cualquier usuario. Fuente: https://rust-lang.github.io/api-guidelines/interoperability.html#types-eagerly-implement-common-traits-c-common-traits
- **Implementa `From`/`TryFrom`/`AsRef`, nunca `Into`.** Fuente: https://rust-lang.github.io/api-guidelines/interoperability.html#conversions-use-the-standard-traits-from-asref-asmut-c-conv-traits
- **`Default` no inventa estados ficticios.** rust-analyzer: "Avoid using "dummy" states to implement a `Default`", y prefiere `Default` a un `new()` sin argumentos. Fuente: guía de rust-analyzer.
- **`Deref` es para punteros inteligentes, no para simular herencia.** Fuente: https://rust-unofficial.github.io/patterns/anti_patterns/deref.html
- **Sella los traits que otros crates no deben implementar.** Fuente: https://rust-lang.github.io/api-guidelines/future-proofing.html#sealed-traits-protect-against-downstream-implementations-c-sealed

## Visibilidad y compatibilidad

- **Campos privados por defecto.** "Making a field public is a strong commitment". Fuente: https://rust-lang.github.io/api-guidelines/future-proofing.html#structs-have-private-fields-c-struct-private
- **`#[non_exhaustive]` desde la primera versión** en structs y enums públicos que puedan crecer; añadirlo después rompe semver. Fuente: https://doc.rust-lang.org/cargo/reference/semver.html#attr-adding-non-exhaustive
- **Activa `unreachable_pub`** para que `pub` solo marque lo que de verdad sale del crate. Lo usan rust-analyzer, tokio, tracing, axum, clap y uv. Fuentes: `[workspace.lints]` de https://github.com/rust-lang/rust-analyzer/blob/master/Cargo.toml y https://github.com/astral-sh/uv/blob/main/Cargo.toml
- **Sin setters.** rust-analyzer: "Never provide setters". Los getters devuelven datos prestados. Fuente: guía de rust-analyzer.
- **Nada de objetos "doer"** (`FooProcessor::new(x).process()`) cuando una función basta. Fuente: guía de rust-analyzer.

## Patrones pequeños

- `std::mem::take` y `mem::replace` para sacar un valor de un `&mut` sin clonar. Fuente: https://rust-unofficial.github.io/patterns/idioms/mem-replace.html
- Guardas RAII con `Drop` para liberar recursos, también descriptores (`OwnedFd`). Fuente: https://rust-unofficial.github.io/patterns/patterns/behavioural/RAII.html
- Un `clone()` que existe para que compile es la señal del antipatrón. Fuente: https://rust-unofficial.github.io/patterns/anti_patterns/borrow_clone.html
- Match exhaustivo en lugar de `_ =>` salvo que el coste de listar sea bajo de verdad: si alguien añade una variante, el compilador te lleva a cada sitio. Fuente: https://github.com/rust-lang/rust/blob/master/src/doc/rustc-dev-guide/src/conventions.md
- Retornos tempranos en lugar de anidar. Fuente: guía de rust-analyzer ("Do use early returns").
