---
name: rust-writing
description: Rules for writing idiomatic Rust, with sources. Use it when writing, reviewing or refactoring Rust code or a Cargo.toml.
---

# Writing Rust

Rules ordered by how many mistakes they prevent. Each one carries its reason in one line; the source and the detail are in `references/`. If the repo has its own rules (CLAUDE.md, CONTRIBUTING, `clippy.toml`, `[lints]`), those win.

## Rules

1. **Put the invariant in a type.** A newtype or an enum instead of a loose `String`, `bool` or `Option`; parse once at the edge and the compiler guarantees the rest. See [api-and-types](references/api-and-types.md).
2. **`Result` for what can fail, panic only for bugs.** An expected failure is a value the caller handles; a panic says the program has a bug. Use `expect("the invariant that broke")` over `unwrap()`. See [errors](references/errors.md).
3. **Choose the error type by what the caller will do.** If it will branch on the failure, give it a concrete type; if it only reports it, `anyhow` with `.context()` is enough. One error enum per crate that lumps everything together is the antipattern matklad and Sabrina Jewson criticize. See [errors](references/errors.md).
4. **Add context to every I/O operation.** `fs::read(&path).with_context(|| format!("reading {}", path.display()))`; a `No such file or directory` without a path cannot be debugged.
5. **Every `unsafe` block is minimal and carries `// SAFETY:`** with the condition that makes it correct, inside a safe API whose module protects the invariant. The correctness of `unsafe` depends on the safe code around it. See [unsafe](references/unsafe.md).
6. **Push `if`s up to the caller and `for`s down into the function.** Preconditions go in the parameter type, not in a check inside the callee; that way the control flow is visible and work is processed in batches.
7. **Take the most general borrowed type** (`&str`, `&[T]`, `Option<&T>`) and take ownership when the function is going to keep the value. A `clone()` to silence the borrow checker usually hides a wrong ownership design.
8. **A `bool` argument becomes an enum or two functions.** `open(true)` says nothing at the call site.
9. **Test behavior at the edge, not the implementation.** Data-driven tests with a `check(input, expected)` function, snapshots for long outputs, no `#[should_panic]` and no `#[ignore]`. See [tests](references/tests.md).
10. **Async only for concurrent I/O.** No more than 10 to 100 µs pass between two `.await`s; blocking work goes to `spawn_blocking` or to a thread. A `std::sync::Mutex` works in async if it does not cross an `.await`. See [async-and-concurrency](references/async-and-concurrency.md).
11. **Mutex or channels before atomics; `Acquire`/`Release` before `SeqCst`.** Mara Bos: `SeqCst` is almost never needed and usually means nobody analyzed the ordering.
12. **Document `# Errors`, `# Panics` and `# Safety`** on every public function that returns an error, can panic or is `unsafe`. The comment explains the why, not the what.
13. **Few dependencies, additive features, `Cargo.lock` committed in binaries, `rust-version` declared.** Every crate is code you audit and compile. See [dependencies](references/dependencies.md).
14. **Measure before optimizing, and measure in `--release`.** Changes to algorithms and allocations beat micro-tricks. See [performance](references/performance.md).
15. **Lints live in `[lints]` in Cargo.toml and CI raises them to errors.** Never `#![deny(warnings)]` in the code: it breaks the build with every new compiler version. See [tooling](references/tooling.md).

## Before calling the work done

Run these, in this order, and leave all four green:

```
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
cargo doc --no-deps   # only if you touched public docs
```

If the repo defines other commands (CONTRIBUTING, CI), use those. A new `#[allow(clippy::...)]` carries a comment with the reason.

## References

- [errors](references/errors.md): `anyhow` versus `thiserror` versus hand-written errors, context, logging, panics.
- [api-and-types](references/api-and-types.md): newtypes, naming, common traits, builders, visibility, semver.
- [tests](references/tests.md): organization, snapshots, fixtures, loom and miri.
- [async-and-concurrency](references/async-and-concurrency.md): threads versus async, blocking, mutexes, atomics, `Send`.
- [unsafe](references/unsafe.md): SAFETY, modules as the boundary, FFI, miri.
- [performance](references/performance.md): profiling, release profiles, allocations, hashing, I/O.
- [tooling](references/tooling.md): clippy, rustfmt, `[lints]`, CI.
- [dependencies](references/dependencies.md): criteria for adding crates, features, MSRV, lockfile.
- [sources](references/sources.md): annotated bibliography, disagreements between authors and how Hydra measures up against these rules.
