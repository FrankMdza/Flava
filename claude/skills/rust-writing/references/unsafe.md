# Unsafe

## Before writing it

- **Look for the safe version first.** `std::os::fd::OwnedFd` and `BorrowedFd` instead of `c_int`; `nix` or `rustix` instead of raw `libc` when the dependency is acceptable; `std::fs` instead of `open(2)`. Every block you do not write is one you do not audit.
- **If the crate does not need `unsafe`, forbid it:** `unsafe_code = "forbid"` in `[lints.rust]`. axum does this. uv and ruff leave it at `"warn"` so every use stands out. Sources: https://github.com/tokio-rs/axum/blob/main/Cargo.toml, https://github.com/astral-sh/uv/blob/main/Cargo.toml

## Rules for the block

- **Small blocks.** The Book: "Keep `unsafe` blocks small; you'll be thankful later when you investigate memory bugs." One block per unsafe operation, not one wrapping the whole function. Source: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#performing-unsafe-superpowers
- **Every block carries `// SAFETY:` right above it** with the condition that makes it correct, not with what the call does. Source: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html. Enable it with `clippy::undocumented_unsafe_blocks`, from the restriction group, which is enabled lint by lint: https://rust-lang.github.io/rust-clippy/master/index.html#undocumented_unsafe_blocks
- **An `unsafe fn` documents `# Safety`** with everything the caller must uphold, because the compiler does not check it. Sources: https://rust-lang.github.io/api-guidelines/documentation.html#function-docs-include-error-panic-and-safety-considerations-c-failure, https://doc.rust-lang.org/reference/unsafe-keyword.html
- **Inside an `unsafe fn`, every unsafe operation goes in its own `unsafe` block.** In edition 2024 `unsafe_op_in_unsafe_fn` warns by default. Source: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html
- **In edition 2024 `extern` blocks are written `unsafe extern "C" { ... }`** and `std::env::set_var`/`remove_var` are `unsafe`. Source: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html

## The boundary is the module

- **Wrap the `unsafe` in a safe API.** The Book: "it's best to enclose such code within a safe abstraction and provide a safe API". Source: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html
- **Module privacy is the only thing that bounds `unsafe`.** Rustonomicon: "the only bullet-proof way to limit the scope of unsafe code is at the module boundary with privacy." A private field the `unsafe` assumes valid must not be changeable from outside the module. Source: https://doc.rust-lang.org/nomicon/working-with-unsafe.html
- **Audit the whole module, not just the block.** "The soundness of our unsafe operations necessarily depends on the state established by otherwise 'safe' operations." Source: same page.
- **Do not trust generic safe code.** A user's `Ord` or `Hash` may be wrong, and your `unsafe` must not cause UB because of it. Source: https://doc.rust-lang.org/nomicon/safe-unsafe-meaning.html
- **Safe code that calls yours must never be able to cause UB.** The Reference's UB list "is not exhaustive"; producing an invalid value is already UB, even if it is never read. Source: https://doc.rust-lang.org/reference/behavior-considered-undefined.html

## FFI and syscalls

- **Check the return of every syscall and convert with `std::io::Error::last_os_error()`** in the same place, before any other call that could clobber `errno`.
- **A descriptor has a single owner.** `OwnedFd::from_raw_fd` right after `open`, and borrows with `BorrowedFd<'_>` tied to the owner's lifetime. A `c_int` stored in a struct says neither who closes it nor when it stops being valid. Source: https://doc.rust-lang.org/std/os/fd/index.html
- **Non-reentrant libc functions** (`getpwuid`, `strerror`, shared `readdir`) need the SAFETY to say why no other thread is calling them, or an `_r` variant.

## Verification

- `cargo miri test` detects UB in pointer and aliasing logic; it does not run real FFI. Source: https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#using-miri-to-check-unsafe-code
- tokio and serde run miri in CI with `-Zmiri-strict-provenance`. Sources: https://github.com/tokio-rs/tokio/blob/master/.github/workflows/ci.yml, https://github.com/serde-rs/serde/blob/master/.github/workflows/ci.yml
