# Async y concurrencia

## Threads o async

- **Trabajo de CPU va a threads; trabajo de I/O muy concurrente va a async; se pueden mezclar.** El Book: si el trabajo es "very parallelizable (that is, CPU-bound)" usa threads, si es "very concurrent (that is, I/O-bound)" usa async, y "you don't have to choose between threads and async". Fuente: https://doc.rust-lang.org/book/ch17-06-futures-tasks-threads.html
- **Si no hay miles de conexiones, threads bastan.** Matthias Endler: "Traditional arguments against threads simply don't apply to Rust", y "Multi-threaded-by-default runtimes cause accidental complexity". Si hace falta async: "stick to Tokio and well-established libraries". Fuente: https://corrode.dev/blog/async/
- **Una CLI síncrona que vigila procesos puede quedarse síncrona.** `poll(2)` sobre unos pocos descriptores no necesita runtime. Esto es inferencia de las dos fuentes anteriores, no una cita.

## Async

- **No bloquees el executor.** Alice Ryhl: "Async code should never spend a long time without reaching an .await", con un límite de "no more than 10 to 100 microseconds between each .await". Lo que tarda más va a `tokio::task::spawn_blocking` o a un thread. Fuente: https://ryhl.io/blog/async-what-is-blocking/
- **Nada te avisa si bloqueas.** Matt Klein: "There's nothing keeping you from calling blocking code inside a future". `std::fs`, `std::thread::sleep` y un `Mutex` disputado compilan igual dentro de `async fn`. Fuente: https://bitbashing.io/async-rust.html
- **`std::sync::Mutex` es correcto en async si no cruza un `.await`.** Tokio: "using a synchronous mutex from within asynchronous code is fine as long as contention remains low and the lock is not held across calls to .await", y el async "is more expensive than an ordinary mutex". El lint `clippy::await_holding_lock` lo vigila. Fuente: https://tokio.rs/tokio/tutorial/shared-state
- **Documenta si un método es cancel safe.** Un future que se descarta en un `select!` pierde lo que tuviera a medias. tokio pone `/// # Cancel safety` en cada método relevante. Fuente: https://github.com/tokio-rs/tokio/blob/master/tokio/src/macros/select.rs
- **Actores: una tarea dueña del estado y un handle que le manda mensajes.** Ryhl: "An actor is split into two parts: the task and the handle", y evita "cycles of channels with bounded capacity" porque pueden bloquearse mutuamente. Fuente: https://ryhl.io/blog/actors-with-tokio/
- **`async fn` en traits públicos: deja que el usuario elija `Send`.** Desde Rust 1.75 compila, pero no es object safe y el compilador avisa en traits públicos. El blog oficial: "We recommend using the `trait_variant::make` proc macro to let your users choose". Fuente: https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/
- **El problema del bound `Send`.** Con un runtime work-stealing "the future can move between threads at any await point", así que un valor no `Send` vivo a través de un `.await` rompe el `spawn`. Fuente: https://smallcultfollowing.com/babysteps/blog/2023/02/01/async-trait-send-bounds-part-1-intro/
- **`Pin` sin sufrir: usa `pin-project`** en lugar de proyectar a mano. Fuente: https://fasterthanli.me/articles/pin-and-suffering

## Estado compartido y threads

- **`Arc` para compartir entre threads, `Rc` solo dentro de uno.** Fuente: https://doc.rust-lang.org/book/ch16-03-shared-state.html
- **Un `Arc<Mutex<_>>` en todas partes es un recolector de basura malo.** Klein: "Used pervasively, Arc gives you the world's worst garbage collector." Prefiere ownership claro o canales. Fuente: https://bitbashing.io/async-rust.html
- **Suelta el lock cuanto antes.** Mara Bos: "Keeping a mutex locked longer than necessary can completely nullify any benefits of parallelism". Ojo con `if let Some(x) = m.lock().unwrap().pop()`: el guard temporal "is not dropped until the end of the entire if let statement". Fuente: https://mara.nl/atomics/basics.html
- **El `Mutex` puede bloquearse mutuamente;** toma varios siempre en el mismo orden. Fuente: https://doc.rust-lang.org/book/ch16-03-shared-state.html
- **Implementar `Send`/`Sync` a mano es `unsafe`** y necesita la misma justificación que cualquier bloque `unsafe`. Fuente: https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html

## Atomics

- **Empieza por `Mutex`; pasa a atomics solo con una medición que lo pida.**
- **`Acquire`/`Release` bastan casi siempre.** Mara Bos: "SeqCst ordering is almost never necessary in practice. In nearly all cases, regular acquire and release ordering suffice." Ver `SeqCst` suele indicar que "the author did not take the time to analyze their memory ordering related assumptions." Fuente: https://mara.nl/atomics/memory-ordering.html
- **`Relaxed` sirve para contadores independientes** que no publican otros datos. Fuente: misma página.
- **Prueba el código lock-free con `loom`.** Ver [tests](tests.md).
