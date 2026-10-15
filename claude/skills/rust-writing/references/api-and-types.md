# API and types

## Invariants in the type

- **Make invalid states unrepresentable.** It is a written convention of the Rust compiler. Source: https://github.com/rust-lang/rust/blob/master/src/doc/rustc-dev-guide/src/conventions.md
- **Validate once when constructing the type and trust it afterwards.** The Book, on a `Guess` type that can only be built between 1 and 100: "you can proceed with your code's logic knowing that the compiler has already ensured that you have a valid value." Source: https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html#custom-types-for-validation
- **Use newtypes to separate meanings that share a base type.** A `RunId(String)` and a `PolicyName(String)` cannot be mixed up in an argument. Zero runtime cost. Sources: https://rust-lang.github.io/api-guidelines/type-safety.html#newtypes-provide-static-distinctions-c-newtype, https://rust-unofficial.github.io/patterns/patterns/behavioural/newtype.html
- **A value from a closed set of strings is an enum with `FromStr`**, not a `String` compared against literals. A typo in `"resmue"` compiles; `Command::Resmue` does not.
- **Express preconditions in types and force the caller to provide them.** rust-analyzer: "Express function preconditions in types and force the caller to provide them (rather than checking in callee)". Its bad example takes `Option<Walrus>` and then checks for `None`. Source: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md
- **Push `if`s up and `for`s down.** matklad: "If there's an `if` condition inside a function, consider if it could be moved to the caller instead". Loops go inside the function that processes a batch. Source: https://matklad.github.io/2023/11/15/push-ifs-up-and-fors-down.html

## Arguments

- **`bool` and `Option` as arguments get replaced with a named type.** API Guidelines: "Core types like `bool` have many possible interpretations." rust-analyzer: if a function is always called with literal `true`, `false`, `Some` or `None`, "split the function in two". Sources: https://rust-lang.github.io/api-guidelines/type-safety.html#arguments-convey-meaning-through-types-not-bool-or-option-c-custom-type, rust-analyzer guide.
- **Take the borrowed type:** `&str` over `&String`, `&[T]` over `&Vec<T>`, `Option<&T>` over `&Option<T>`. Sources: https://rust-unofficial.github.io/patterns/idioms/coercion-arguments.html, rust-analyzer guide ("always prefer types on the left").
- **If the function needs ownership, take it** instead of asking for `&T` and cloning inside. The caller decides whether to clone. Source: https://rust-lang.github.io/api-guidelines/flexibility.html#caller-decides-where-to-copy-and-place-data-c-caller-control
- **Many parameters get grouped into a `Config` struct.** rust-analyzer also asks not to implement `Default` for that `Config`, so each caller decides every field. Source: rust-analyzer guide.
- **For incremental construction with many optionals, a builder.** Rust has no overloading and no default parameter values. Sources: https://rust-lang.github.io/api-guidelines/type-safety.html#builders-enable-construction-of-complex-values-c-builder, https://rust-unofficial.github.io/patterns/patterns/creational/builder.html
- **Generics in moderation at crate boundaries.** rust-analyzer: "Avoid making a lot of code type parametric, *especially* on the boundaries between crates", and "Avoid `AsRef` polymorphism", because every instance gets monomorphized and the build gets longer. This contrasts with API Guidelines C-GENERIC, which asks for generics to accept more inputs. See the disagreement in [sources](sources.md).

## Names

- Conversions: `as_` cheap and borrowed, `to_` expensive, `into_` consumes. Source: https://rust-lang.github.io/api-guidelines/naming.html
- Getters without a `get_` prefix. Source: same page, C-GETTER.
- Iterators: `iter`, `iter_mut`, `into_iter`. Source: same page, C-ITER.
- `UpperCamelCase` for types, `snake_case` for values. Source: same page, C-CASE.
- Local variables with long, boring names; conventions `res`, `it`, `n_foos`, `foo_idx`. Source: rust-analyzer guide.

## Traits

- **Implement the common traits early** where they apply: `Debug`, `Clone`, `PartialEq`, `Eq`, `Hash`, `Default`, `Display`. A public type without `Debug` is a nuisance for every user. Source: https://rust-lang.github.io/api-guidelines/interoperability.html#types-eagerly-implement-common-traits-c-common-traits
- **Implement `From`/`TryFrom`/`AsRef`, never `Into`.** Source: https://rust-lang.github.io/api-guidelines/interoperability.html#conversions-use-the-standard-traits-from-asref-asmut-c-conv-traits
- **`Default` does not invent fictional states.** rust-analyzer: "Avoid using "dummy" states to implement a `Default`", and prefers `Default` over a `new()` with no arguments. Source: rust-analyzer guide.
- **`Deref` is for smart pointers, not for simulating inheritance.** Source: https://rust-unofficial.github.io/patterns/anti_patterns/deref.html
- **Seal the traits other crates must not implement.** Source: https://rust-lang.github.io/api-guidelines/future-proofing.html#sealed-traits-protect-against-downstream-implementations-c-sealed

## Visibility and compatibility

- **Private fields by default.** "Making a field public is a strong commitment". Source: https://rust-lang.github.io/api-guidelines/future-proofing.html#structs-have-private-fields-c-struct-private
- **`#[non_exhaustive]` from the first version** on public structs and enums that may grow; adding it later breaks semver. Source: https://doc.rust-lang.org/cargo/reference/semver.html#attr-adding-non-exhaustive
- **Enable `unreachable_pub`** so `pub` only marks what really leaves the crate. rust-analyzer, tokio, tracing, axum, clap and uv use it. Sources: `[workspace.lints]` in https://github.com/rust-lang/rust-analyzer/blob/master/Cargo.toml and https://github.com/astral-sh/uv/blob/main/Cargo.toml
- **No setters.** rust-analyzer: "Never provide setters". Getters return borrowed data. Source: rust-analyzer guide.
- **No "doer" objects** (`FooProcessor::new(x).process()`) when a function is enough. Source: rust-analyzer guide.

## Small patterns

- `std::mem::take` and `mem::replace` to pull a value out of a `&mut` without cloning. Source: https://rust-unofficial.github.io/patterns/idioms/mem-replace.html
- RAII guards with `Drop` to release resources, descriptors too (`OwnedFd`). Source: https://rust-unofficial.github.io/patterns/patterns/behavioural/RAII.html
- A `clone()` that exists so the code compiles is the sign of the antipattern. Source: https://rust-unofficial.github.io/patterns/anti_patterns/borrow_clone.html
- Exhaustive match instead of `_ =>` unless the cost of listing is truly low: if someone adds a variant, the compiler takes you to every site. Source: https://github.com/rust-lang/rust/blob/master/src/doc/rustc-dev-guide/src/conventions.md
- Early returns instead of nesting. Source: rust-analyzer guide ("Do use early returns").
