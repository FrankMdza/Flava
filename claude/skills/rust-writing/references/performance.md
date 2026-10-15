# Performance

## Measure first

- **Profile to know which code is hot.** Without a profile, you optimize what does not matter. Source: https://nnethercote.github.io/perf-book/profiling.html
- **Measure in release.** The Perf Book: "10-100x speedups over dev builds are common!" Source: https://nnethercote.github.io/perf-book/build-configuration.html#release-builds
- **Keep line info in release for profiling:** `debug = "line-tables-only"` in `[profile.release]`. uv uses it in dev and measured 20% less total time. Sources: https://nnethercote.github.io/perf-book/profiling.html, https://github.com/astral-sh/uv/blob/main/Cargo.toml
- **Algorithms and data structures beat micro-tricks.** "The biggest performance improvements often come from changes to algorithms or data structures". Source: https://nnethercote.github.io/perf-book/general-tips.html

## Release profile for a binary

```toml
[profile.release]
lto = "fat"          # or "thin" if build time matters
codegen-units = 1
panic = "abort"      # only if nothing depends on catch_unwind
```

ripgrep, uv and clap use this combination. Sources: https://nnethercote.github.io/perf-book/build-configuration.html, https://github.com/BurntSushi/ripgrep/blob/master/Cargo.toml. `overflow-checks = true` in release makes overflow panic instead of wrapping; decide by the domain: https://doc.rust-lang.org/cargo/reference/profiles.html#overflow-checks

## Allocations

- **Every allocation costs** a global lock, bookkeeping and sometimes a syscall. Source: https://nnethercote.github.io/perf-book/heap-allocations.html
- **`Vec::with_capacity` when you know the size; `clear()` to reuse a buffer in a loop.** Source: same page.
- **Do not allocate a `Vec` where an iterator will do,** and do not `collect` to iterate again. Return `impl Iterator`. Sources: https://nnethercote.github.io/perf-book/iterators.html, rust-analyzer guide ("Don't allocate a `Vec` where an iterator would do").
- **Push the allocation to the caller:** if the function is going to keep a `String`, take `String` and not `&str`. Source: https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/style.md
- **In recursion, an accumulator parameter** instead of returning a new collection at every level. Source: same guide.

## Types and hashing

- **`SipHash`, the default hasher, is slow with short keys.** `FxHashMap` (`rustc-hash`) is much faster but does not resist HashDoS; use it only with keys an attacker does not control. Source: https://nnethercote.github.io/perf-book/hashing.html. rust-analyzer and cargo enforce it with `disallowed-types` in `clippy.toml`.
- **Box the large, rare variant of an enum** so it does not inflate the others. `clippy::large_enum_variant` flags it. Source: https://nnethercote.github.io/perf-book/type-sizes.html
- **Iterate instead of indexing** so the compiler removes bounds checks. Source: https://nnethercote.github.io/perf-book/bounds-checks.html

## I/O

- **`println!` locks stdout on every call.** In a loop, take `stdout().lock()` once. Source: https://nnethercote.github.io/perf-book/io.html
- **`BufReader`/`BufWriter` for small reads and writes.** Source: same page.
- **Call `flush()` on the `BufWriter` at the end:** `Drop` ignores the flush error. Source: same page.

## Compile time

- **Look after the build before it hurts.** matklad: fix it "before they become a problem"; in CI cache dependencies, not your own crates. Source: https://matklad.github.io/2021/09/04/fast-rust-builds.html
- **No generic code at crate boundaries** and `#[inline]` only on small non-generic library functions. Sources: the same, and https://matklad.github.io/2021/07/09/inline-in-rust.html
