# Tests

## What to test

- **Test features at the system's edge, not loose functions.** matklad: "test features, not code! Test at the boundaries." A test that calls a private helper breaks on every refactor without having found a bug. Source: https://matklad.github.io/2021/05/31/how-to-test.html
- **Make adding a test cost one line.** matklad: "work hard on making adding new tests trivial". In practice, a `check(input, expected)` function, and every test is one call. Source: same page.
- **Separate logic from I/O so you can test it without disk or network.** matklad: "keep as much as possible sans io". Source: same page.
- **rust-analyzer writes data-driven tests that do not touch the internal API**: "tests are data driven and do not test the API". That way it can rewrite the implementation without touching the tests. Source: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md

## How to write them

- **Snapshots for long outputs.** Every large project uses one: `insta` in uv and ruff, `snapbox`/`trycmd` in cargo and clap, `expect-test` in rust-analyzer. They regenerate with one command (`cargo insta review`, `SNAPSHOTS=overwrite cargo test`, `UPDATE_EXPECT=1`). Sources: https://github.com/astral-sh/uv/blob/main/CONTRIBUTING.md, https://github.com/rust-lang/cargo/blob/master/doc/contrib/src/tests/writing.md
- **Multiline fixtures as unindented raw strings.** Source: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md
- **No `#[should_panic]`:** check for `None` or `Err` explicitly. A `should_panic` also passes if the panic comes from somewhere else. Source: rust-analyzer guide.
- **No `#[ignore]`:** if the behavior is wrong, the test asserts the current behavior with a `// FIXME`, and that way you find out when it changes. Source: rust-analyzer guide.
- **Coverage marks** (`cov_mark::hit!` in the code, `cov_mark::check!` in the test) to prove that a test goes through the branch it claims. Source: rust-analyzer guide.
- **The test for the bug goes in a commit before the fix.** Cargo and clap ask for this: that way the history shows the test red and then green. Sources: https://github.com/rust-lang/cargo/blob/master/doc/contrib/src/process/working-on-cargo.md, https://github.com/clap-rs/clap/blob/master/CONTRIBUTING.md

## Organization

- **Unit tests in a `mod tests` with `#[cfg(test)]` in the same file;** they can test private functions. Source: https://doc.rust-lang.org/book/ch11-03-test-organization.html
- **Integration tests in `tests/`, which only see the public API.** For that, the logic lives in `src/lib.rs` and `main.rs` is thin. Source: same page.
- **Shared helpers in `tests/common/mod.rs`**, not in `tests/common.rs`, so it does not compile as one more test. Source: same page.
- **A single integration crate with several modules, not one file per test.** Every file in `tests/` is a binary that links separately. matklad: "large projects should have only one integration test crate with several modules"; in his case it went from 20 to 13 seconds. Source: https://matklad.github.io/2021/02/27/delete-cargo-integration-tests.html. The pattern: `tests/it/main.rs` with `mod foo; mod bar;`.
- **tokio, tracing and axum avoid unit tests** and prefer integration tests and doctests. tokio: "Tokio avoids unit tests as much as possible". Source: https://github.com/tokio-rs/tokio/blob/master/docs/contributing/pull-requests.md

## Concurrency and unsafe

- **`loom` to explore interleavings of low-level concurrent code.** tokio runs it with `RUSTFLAGS="--cfg loom -C debug_assertions"`. Source: https://github.com/tokio-rs/tokio/blob/master/docs/contributing/pull-requests.md
- **`cargo miri test` for code with `unsafe`,** with `-Zmiri-strict-provenance` like tokio and serde. Miri does not see FFI into the real libc, so it works for pointer logic, not for syscalls. Source: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-miri-to-check-unsafe-code
- **A test that touches the process's environment variables goes in its own binary with a lock**, because `set_var` affects the threads running other tests; in edition 2024 `set_var` is also `unsafe`. Source: https://doc.rust-lang.org/edition-guide/rust-2024/newly-unsafe-functions.html

## Tools

- `cargo nextest` runs every test in its own process, and faster; uv and tokio use it. Source: https://github.com/astral-sh/uv/blob/main/CONTRIBUTING.md
- `clippy.toml` with `allow-unwrap-in-tests = true` and `allow-expect-in-tests = true` if you enable `unwrap_used`/`expect_used`. Source: https://github.com/clap-rs/clap/blob/master/.clippy.toml
