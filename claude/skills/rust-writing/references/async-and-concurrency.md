# Async and concurrency

## Threads or async

- **CPU work goes to threads; highly concurrent I/O work goes to async; you can mix them.** The Book: if the work is "very parallelizable (that is, CPU-bound)" use threads, if it is "very concurrent (that is, I/O-bound)" use async, and "you don't have to choose between threads and async". Source: https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- **If there are not thousands of connections, threads are enough.** Matthias Endler: "Traditional arguments against threads simply don't apply to Rust", and "Multi-threaded-by-default runtimes cause accidental complexity". If async is needed: "stick to Tokio and well-established libraries". Source: https://corrode.dev/blog/async/
- **A synchronous CLI that watches processes can stay synchronous.** `poll(2)` over a few descriptors needs no runtime. This is an inference from the two sources above, not a quote.

## Async

- **Do not block the executor.** Alice Ryhl: "Async code should never spend a long time without reaching an .await", with a limit of "no more than 10 to 100 microseconds between each .await". Anything that takes longer goes to `tokio::task::spawn_blocking` or to a thread. Source: https://ryhl.io/blog/async-what-is-blocking/
- **Nothing warns you if you block.** Matt Klein: "There's nothing keeping you from calling blocking code inside a future". `std::fs`, `std::thread::sleep` and a contended `Mutex` compile just the same inside an `async fn`. Source: https://bitbashing.io/async-rust.html
- **`std::sync::Mutex` is correct in async if it does not cross an `.await`.** Tokio: "using a synchronous mutex from within asynchronous code is fine as long as contention remains low and the lock is not held across calls to .await", and the async one "is more expensive than an ordinary mutex". The `clippy::await_holding_lock` lint watches for it. Source: https://tokio.rs/tokio/tutorial/shared-state
- **Document whether a method is cancel safe.** A future dropped in a `select!` loses whatever it had half done. tokio puts `/// # Cancel safety` on every relevant method. Source: https://github.com/tokio-rs/tokio/blob/master/tokio/src/macros/select.rs
- **Actors: one task that owns the state and a handle that sends it messages.** Ryhl: "An actor is split into two parts: the task and the handle", and avoid "cycles of channels with bounded capacity" because they can block each other. Source: https://ryhl.io/blog/actors-with-tokio/
- **`async fn` in public traits: let the user choose `Send`.** Since Rust 1.75 it compiles, but it is not object safe and the compiler warns on public traits. The official blog: "We recommend using the `trait_variant::make` proc macro to let your users choose". Source: https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/
- **The `Send` bound problem.** With a work-stealing runtime "the future can move between threads at any await point", so a non-`Send` value alive across an `.await` breaks the `spawn`. Source: https://smallcultfollowing.com/babysteps/blog/2023/02/01/async-trait-send-bounds-part-1-intro/
- **`Pin` without suffering: use `pin-project`** instead of projecting by hand. Source: https://fasterthanli.me/articles/pin-and-suffering

## Shared state and threads

- **`Arc` to share across threads, `Rc` only within one.** Source: https://doc.rust-lang.org/book/ch16-03-shared-state.html
- **An `Arc<Mutex<_>>` everywhere is a bad garbage collector.** Klein: "Used pervasively, Arc gives you the world's worst garbage collector." Prefer clear ownership or channels. Source: https://bitbashing.io/async-rust.html
- **Release the lock as soon as possible.** Mara Bos: "Keeping a mutex locked longer than necessary can completely nullify any benefits of parallelism". Watch out for `if let Some(x) = m.lock().unwrap().pop()`: the temporary guard "is not dropped until the end of the entire if let statement". Source: https://mara.nl/atomics/basics.html
- **Mutexes can deadlock each other;** always take several in the same order. Source: https://doc.rust-lang.org/book/ch16-03-shared-state.html
- **Implementing `Send`/`Sync` by hand is `unsafe`** and needs the same justification as any `unsafe` block. Source: https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html

## Atomics

- **Start with `Mutex`; move to atomics only with a measurement that calls for it.**
- **`Acquire`/`Release` are almost always enough.** Mara Bos: "SeqCst ordering is almost never necessary in practice. In nearly all cases, regular acquire and release ordering suffice." Seeing `SeqCst` usually means "the author did not take the time to analyze their memory ordering related assumptions." Source: https://mara.nl/atomics/memory-ordering.html
- **`Relaxed` works for independent counters** that do not publish other data. Source: same page.
- **Test lock-free code with `loom`.** See [tests](tests.md).
