# Errors

## Result or panic

- **`Result` is the default for a function that can fail.** The Book: "Returning `Result` is a good default choice when you're defining a function that might fail." Source: https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html
- **If the failure is expected, return `Result`; if the code could be left in an invalid state, panic.** Source: https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html#guidelines-for-error-handling
- **A panic is a bug, and `unwrap`/`expect` are for asserting invariants.** BurntSushi: "Panicking should not be used for error handling in either applications or libraries" and "correct Rust programs don't panic". That is why "it is fine to use unwrap(), expect() and slice index syntax" when the panic only happens if there is a bug. Source: https://burntsushi.net/unwrap/
- **Prefer `expect` to `unwrap` and write the invariant in the message, not the symptom.** BurntSushi: "Prefer expect() to unwrap(), since it gives more descriptive messages". `expect("the parser only emits non-empty names")` tells the reader why it cannot fail. Source: https://burntsushi.net/unwrap/
- **In examples and prototypes, `unwrap` is a marker for what is missing.** The Book calls it "a placeholder for the way you'd want your application to handle errors". Source: https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html#examples-prototype-code-and-tests
- **In documentation examples use `?`, not `unwrap`.** People copy examples as they are. Source: https://rust-lang.github.io/api-guidelines/documentation.html#examples-use--not-try-not-unwrap-c-question-mark
- **rust-analyzer goes further: `never!` instead of `assert!` and `catch_unwind` per request**, because an IDE cannot crash over a bug. This applies to long-lived servers, not to a CLI. Source: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md

## Which error type

The deciding question, according to Luca Palmieri: "Do you expect the caller to behave differently based on the failure mode they encountered?" If the answer is no, "Use an opaque error". Source: https://www.lpalmieri.com/posts/error-handling-rust/

| Situation | Type | Source |
|---|---|---|
| Binary or application layer that only reports | `anyhow::Result` with `.context()` | anyhow README, https://github.com/dtolnay/anyhow |
| Library whose caller branches on the failure | own enum or struct, with `thiserror` or by hand | thiserror README, https://github.com/dtolnay/thiserror |
| A single failure the caller does distinguish, inside an app on `anyhow` | own struct and `err.downcast_ref::<T>()` | Palmieri, link above |
| Analysis that yields a partial result plus diagnostics | `(T, Vec<Error>)` instead of `Result<T, Error>` | rust-analyzer architecture.md |

- **dtolnay:** "Use thiserror if you care about designing your own dedicated error type(s) so that the caller receives exactly the information that you choose", and "Use Anyhow if you don't care what error type your functions return". `thiserror` "deliberately does not appear in your public API", so replacing it with a hand-written impl does not break semver. Source: https://github.com/dtolnay/thiserror
- **Put the error near the unit that fails.** Sabrina Jewson: "Error types should be located near to their unit of fallibility", and criticizes "just stick everything in a big enum". matklad calls the "kitchen-sink enum" an antipattern and asks first "how the error will be used?". Sources: https://sabrinajewson.org/blog/errors, https://matklad.github.io/2020/10/15/study-of-std-io-error.html
- **Error types implement `std::error::Error`, `Send` and `Sync`.** Without `Send + Sync` they cannot cross threads or fit in `anyhow::Error`. Source: https://rust-lang.github.io/api-guidelines/interoperability.html#error-types-are-meaningful-and-well-behaved-c-good-err
- **Foundational libraries write their error by hand.** `ignore` (from ripgrep) and `regex` implement `std::error::Error` without `thiserror`. Source: https://github.com/BurntSushi/ripgrep/blob/master/crates/ignore/src/lib.rs
- **axum does not let errors escape the handler:** every service has `Infallible` as its error and the `Result` becomes a `Response` through `IntoResponse`. Source: https://github.com/tokio-rs/axum/blob/main/axum/src/docs/error_handling.md

## Context and reporting

- **Every call to `std::fs` and other low-level routines carries context.** Cargo: "When using any low-level routines, such as `std::fs`, *always* add error context". Source: https://github.com/rust-lang/cargo/blob/master/doc/contrib/src/implementation/console.md
- **Log the error where you handle it, not where you propagate it.** Palmieri: "errors should be logged when they are handled"; a function that only does `?` "should not log the error". Otherwise the same failure shows up three times in the log. Source: https://www.lpalmieri.com/posts/error-handling-rust/
- **Print the full chain with `{:#}` in `main`.** ripgrep does `run() -> anyhow::Result<ExitCode>`, walks `err.chain()` to treat `BrokenPipe` as a clean exit, and otherwise prints `{:#}` and exits with code 2. Source: https://github.com/BurntSushi/ripgrep/blob/master/crates/core/main.rs
- **Error messages start in lowercase and do not end in a period**, because `anyhow` chains them with `: `. rust-analyzer asks for this in its guide. Source: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md
- **To raise an error, `return Err(e)` or `bail!`.** rust-analyzer prefers the explicit `return` because it has type `!` and reads as an exit. Source: rust-analyzer style guide, link above.

## Documentation

- Every public function that returns an error carries `# Errors`, and one that can panic carries `# Panics`. This applies to trait methods too. Source: https://rust-lang.github.io/api-guidelines/documentation.html#function-docs-include-error-panic-and-safety-considerations-c-failure
- The `clippy::missing_errors_doc` and `clippy::missing_panics_doc` lints check this, but uv and serde disable them as noisy in code that is not a published library. Decide by who reads the API.
