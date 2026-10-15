# Sources

Consulted on 2026-09-28. I checked the quotes against the loaded page; where I could not, the entry says so.

## Official documentation

- **The Rust Programming Language (the Book).** https://doc.rust-lang.org/book/. Chapter 9.3 gives the panic-or-`Result` criterion and validation in types; 11.3 test organization; 16 and 17 threads versus async; 20.1 `unsafe`, SAFETY and miri. It is the base everyone else takes for granted.
- **Rust API Guidelines.** https://rust-lang.github.io/api-guidelines/. A checklist with codes (C-CONV, C-NEWTYPE, C-CUSTOM-TYPE, C-FAILURE...). Meant for published libraries; in a binary, the future-proofing rules weigh less.
- **Rust Reference.** https://doc.rust-lang.org/reference/. The list of undefined behavior and the contract of `unsafe fn`. Its `unsafe` page still describes the pre-edition-2024 behavior inside `unsafe fn`; for that, the Edition Guide is the one to use.
- **Edition Guide, Rust 2024.** https://doc.rust-lang.org/edition-guide/rust-2024/. `unsafe_op_in_unsafe_fn`, `unsafe extern`, unsafe `set_var`. The front page loaded; so did the cited subpages.
- **Rustonomicon.** https://doc.rust-lang.org/nomicon/. The argument that the `unsafe` boundary is the module, not the block.
- **Clippy.** https://github.com/rust-lang/rust-clippy and https://doc.rust-lang.org/clippy/. Groups, `clippy.toml`, `msrv`.
- **rustfmt and Style Guide.** https://github.com/rust-lang/rustfmt, https://doc.rust-lang.org/style-guide/. The Style Guide only returned a summary, not literal text; the 4-space and 100-column rules match rustc's `tidy`.
- **Rust Design Patterns.** https://rust-unofficial.github.io/patterns/. Newtype, builder, RAII, `mem::take`, and the antipatterns `clone` for the borrow checker, `#![deny(warnings)]` and `Deref` as inheritance. Not official to the Rust project.
- **Rust Performance Book** by Nicholas Nethercote. https://nnethercote.github.io/perf-book/. Profiles, allocations, hashing, type sizes, I/O. Some internal links point at rust-lang.github.io/perf-book, a possible move.
- **Cargo Book.** https://doc.rust-lang.org/cargo/. Features, semver, `[lints]`, workspaces, profiles, `rust-version`.
- **Official Rust blog.** `async fn` in traits (https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/), 1.84 and the MSRV resolver (https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/), 1.85 and edition 2024 (https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/). The URLs ending in `.html` return an empty redirect; the ones with a trailing slash load.

## Flagship repos

- **rust-analyzer.** Style guide at https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md; the old path `docs/dev/style.md` no longer exists. It is the most concrete code style guide that exists in Rust: preconditions in types, no `should_panic`, no setters, `anyhow` across the whole project, few dependencies, data-driven tests with `expect-test`.
- **rust-lang/rust.** https://github.com/rust-lang/rust/blob/master/src/doc/rustc-dev-guide/src/conventions.md and `tidy`. Unrepresentable states, exhaustive match, comments that say why, `FIXME` not `TODO`.
- **cargo.** https://github.com/rust-lang/cargo/tree/master/doc/contrib. `anyhow` with mandatory context on `std::fs`, snapshots with `snapbox`, the test in a commit before the fix, `disallowed-methods` in `clippy.toml`.
- **ripgrep, regex, bstr (BurntSushi).** A `main` that returns `ExitCode` and handles `BrokenPipe`; hand-written library errors; `max_width = 79`; does not run clippy in CI.
- **tokio.** https://github.com/tokio-rs/tokio/blob/master/docs/contributing/pull-requests.md. Avoids unit tests, uses loom and miri, documents cancel safety, CI with MSRV, semver, cargo-deny, minimal-versions.
- **serde.** `pedantic` in CI with a list of allows grouped by reason in `lib.rs`.
- **clap.** Ed Page's lint template in `[workspace.lints]`, the most complete curated list of those reviewed.
- **axum.** `unsafe_code = "forbid"`, handlers with `Infallible` as the error, lints that push `#[must_use]`.
- **uv and ruff (Astral).** `pedantic` with allows, `disallowed-methods` to force `fs-err`, `thiserror` and `anyhow` in the same workspace, snapshots with `insta`, pinned toolchain.
- **tracing.** Copies tokio's conventions; thresholds in `clippy.toml`.

## Authors

- **matklad (Alex Kladov).** Push ifs up and fors down; How to test; Delete cargo integration tests; Large Rust workspaces; Fast Rust builds; Inline in Rust; Study of std::io::Error. All at https://matklad.github.io/. Supplies the function design and test rules most cited by others.
- **BurntSushi (Andrew Gallant).** https://burntsushi.net/unwrap/ and https://burntsushi.net/rust-error-handling/. The "a panic is a bug" criterion and the conservative stance on dependencies (Jiff README). I found no equivalent text specific to ripgrep about dependencies.
- **dtolnay.** The `anyhow` and `thiserror` READMEs, the application versus library split.
- **Luca Palmieri.** https://www.lpalmieri.com/posts/error-handling-rust/. The control-flow versus reporting question and where to log the error.
- **Sabrina Jewson.** https://sabrinajewson.org/blog/errors. Errors per unit of fallibility, against the single enum.
- **withoutboats.** Why async Rust, Let futures be futures, Thread-per-core, From failure to Fehler, at https://without.boats/blog/. Defense of the futures model and of work-stealing; recommended a trait object (`anyhow::Error`) for applications. "The registers of Rust" loaded but I could not verify literal quotes.
- **Niko Matsakis.** The `Send` bound problem series, https://smallcultfollowing.com/babysteps/series/send-bound-problem/, and the async goals for 2024.
- **Alice Ryhl.** https://ryhl.io/blog/async-what-is-blocking/ and https://ryhl.io/blog/actors-with-tokio/, plus the tokio shared-state tutorial.
- **Mara Bos.** Rust Atomics and Locks, free book at https://mara.nl/atomics/ (marabos.nl redirects there). Memory ordering and lock duration.
- **fasterthanlime (Amos).** https://fasterthanli.me/articles/pin-and-suffering. "Surviving Rust async interfaces" and "The curse of strong typing" loaded, but the extractor returned paraphrases and I do not quote them. He has no article dedicated to `color-eyre`/`miette`.
- **Matt Klein** (https://bitbashing.io/async-rust.html) and **Matthias Endler** (https://corrode.dev/blog/async/). The most cited critiques of async.

## Sources I could not read or quote

- **Rust for Rustaceans, Jon Gjengset.** O'Reilly returned 403; No Starch only shows the table of contents (ch. 3 Designing Interfaces, 4 Error Handling, 6 Testing, 8 Asynchronous Programming, 9 Unsafe Code). I do not quote its content. I could not confirm that chapter 3 is organized around "unsurprising, flexible, obvious, constrained", although that is repeated around the web.
- **Zero to Production, Luca Palmieri.** I did not read it; I quote his errors article, which is a chapter of the book published on his blog.
- **Rust Foundation.** I found no publications with code style rules; I do not cite it.
- Articles by fasterthanlime and withoutboats listed above as unverified.

## Where they disagree

1. **`anyhow` in libraries.** dtolnay: `thiserror` in libraries, `anyhow` in applications. Palmieri starts from a different criterion: if the caller is not going to branch, an opaque error works in a library too. withoutboats recommended a trait object for applications. Sabrina Jewson would not even use `thiserror` in a library: "it's really not that many lines of code saved for a whole extra dependency". BurntSushi writes the errors by hand in `regex` and `ignore`, in line with Jewson. **What I do:** in Hydra, which is a binary with an internal lib, `anyhow` plus concrete error structs where the caller branches is consistent with all four.
2. **One error enum per crate versus errors per function.** Common practice is one `Error` per crate. matklad calls it the "kitchen-sink enum" and Jewson asks for one type per unit of fallibility. None of those reviewed defends the single enum in writing.
3. **`unwrap`.** BurntSushi: fine for invariants, because a panic is a bug. The Book treats it as a prototype marker. rust-analyzer goes to the other extreme with `never!` so it never crashes. I did not find the popular rule "never `unwrap`" signed by anyone recognized.
4. **Async.** withoutboats defends stackless futures and work-stealing. Klein and Endler say multithreading by default brings complexity most people do not need and that threads are enough. Niko acknowledges the `Send` bound problem as open debt.
5. **Mutex in async.** tokio and Ryhl: `std::sync::Mutex` is fine if it does not cross an `.await`; the common mistake is always using `tokio::sync::Mutex`.
6. **Test organization.** The Book teaches `mod tests` per file plus `tests/` with one file per test. matklad asks for a single integration crate with modules and, in libraries, avoiding unit tests. tokio, tracing and axum also avoid unit tests.
7. **Generics in the API.** API Guidelines C-GENERIC asks for generics to accept more input types. rust-analyzer asks to avoid them at crate boundaries and to avoid `AsRef` polymorphism, because of the monomorphization cost in the build. The Guidelines optimize for a library's user; rust-analyzer for the compile time of a large project.
8. **`#[must_use]`.** axum pushes it with `must_use_candidate`; uv and serde disable that same lint as noisy.
9. **Clippy in CI.** Almost everyone runs `clippy -D warnings`. ripgrep does not run clippy.
10. **Dependencies.** BurntSushi and rust-analyzer are conservative; Jewson rejects `thiserror` for being a dependency. dtolnay replies that `thiserror` does not appear in the public API, so removing it later breaks nothing. I found no signed text that defends using crates freely.

## Hydra against these practices

Reviewed on 2026-09-28 on `~/hydra` without modifying it. Paths are relative to that folder.

1. **No `[lints]` in `Cargo.toml` and no `clippy.toml`.** `Cargo.toml:1-24` only has the package and dependencies, and CI runs clippy with the default groups (`.github/workflows/ci.yml`, step `cargo clippy --all-targets -- -D warnings`). Missing are the lints almost every flagship repo repeats: `undocumented_unsafe_blocks`, `dbg_macro`, `todo`, `unreachable_pub`. `unsafe_op_in_unsafe_fn` already warns by default with edition 2024. It gets the important part right: warnings raised to errors in CI and not with `#![deny(warnings)]` in the code.
2. **`unsafe` blocks without `// SAFETY:`.** `src/pty.rs:216`, `226`, `343`, `348`, `400` and `404` (`poll`, `read`, `fcntl`) and `src/procinfo.rs:29` and `51` (`sysctl`) carry no comment. `src/env.rs:193` explains at `:192` why `getpwuid` is acceptable, but without the `SAFETY` tag the lint looks for. By contrast, `src/worktree.rs:610-671` is the model to copy: one SAFETY per block and `OwnedFd::from_raw_fd` right after `open` at `:622`.
3. **A raw descriptor in a struct.** `src/pty.rs:67` stores `pty_fd: libc::c_int`, obtained at `:131` from `pair.master.as_raw_fd()`. It is valid only while `_master` at `:60` lives; nothing in the type expresses that. A `BorrowedFd<'_>` or always reading through `_master` would put that dependency in the type, as the Rustonomicon's module-boundary rule asks.
4. **Strings for closed sets.** `src/run.rs:67` has `policy: String` and `src/run.rs:90` has `command: String` with the comment "`run` or `resume`"; callers write the literal by hand at `src/main.rs:48`, `src/face.rs:364`, `src/interactive.rs:346`, `src/interactive.rs:464` and `src/resume.rs:123`. An enum `Command { Run, Resume }` would turn a typo into a compile error. `Provider` already does it right: `src/provider/mod.rs:363` implements `FromStr` and `main.rs` parses at the edge.
5. **Errors: `anyhow` with concrete structs where the caller branches.** `src/run.rs:322-345` defines `TooDeep` and `src/live.rs:424-453` defines `TooManyLive`, both with `Display` and `std::error::Error`, and `tests/status.rs:517` does `downcast_ref::<live::TooManyLive>()`. That is exactly Palmieri's pattern: opaque by default, concrete where needed. Neither is consumed with `downcast` inside `src/`, so today only the tests tell them apart.
6. **Panic without `# Panics`.** `src/run.rs:2039-2051`: `append_resume_args` is `pub` and does `expect` on `hook_file` and on the `argv`, but its doc comment at `:2039` has no `# Panics` section. The `expect` messages do name the invariant, as BurntSushi asks.
7. **Twenty-seven integration test binaries.** `tests/` has 27 `.rs` files at the root plus `tests/common/mod.rs`; each one links as a separate binary. It is the case matklad describes in "Delete cargo integration tests". CONTRIBUTING also requires `--test-threads=1`, which adds time. `tests/common/mod.rs` does follow the form the Book asks for.
8. **Outdated crate doc.** `src/lib.rs:3` says "It launches two providers, `claude` and `cursor-agent`", and `CLAUDE.md` describes four. It is not a Rust style rule, but it is rustc's rule that comments tell the truth about the why; a doc that lies costs more than a missing one.
9. **Everything is `pub mod`.** `src/lib.rs:20-54` exposes all 35 modules, because the integration tests in `tests/` need to see them. There is no `unreachable_pub`, so nothing distinguishes what is API from what is public only for the tests.
10. **What it already gets right.** `edition = "2024"` and `rust-version = "1.88"` at `Cargo.toml:4-5`; `Cargo.lock` committed; 11 direct dependencies with no helper crates and no async runtime, with synchronous I/O over `poll(2)` in `src/pty.rs`, which is what Endler recommends for this amount of concurrency; context on syscall errors (`src/pty.rs:222`, `:402`, `:406`); the logic lives in the lib and `src/main.rs` only parses with clap and dispatches, although its `match` already takes 232 lines. CONTRIBUTING asks for `cargo clippy -- -D warnings` without `--all-targets` and CI does pass it, so the document falls short of the CI.
