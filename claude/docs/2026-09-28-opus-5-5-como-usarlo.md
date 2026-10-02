# Opus 5.5, cómo usarlo en tu forma de trabajar

Borrador del 2026-09-28. Nada de esto está aplicado. Cada cambio de la sección 4 espera tu visto bueno.

Fuente: "Getting the most out of Opus 5.5 in Claude and Claude Code", Addy Osmani, blog de claude.dev, publicado el 22 de septiembre de 2026. URL: https://claude.dev/blog/getting-the-most-out-of-opus-5-5/

Lo leí entero. WebFetch devolvió un resumen, así que bajé el HTML con curl y saqué el texto completo. Las citas de abajo salen de ese texto, en inglés y literales.

## 1. Qué dice el artículo

Resumen por secciones. Lo que va aquí es del artículo. Mis lecturas están en la sección 2.

### La tesis

El artículo abre con tres diferencias respecto a Opus 5: "it works for longer on its own, it tells you plainly what it did, and it thinks before every reply." Todo lo demás se deriva de esas tres.

Las tres cosas que pide probar primero:

- "Hand over the whole task. Say what "done" looks like and when you want it to stop and ask. Then let it work."
- "Delete "think carefully" lines. Opus 5.5 already thinks before every reply."
- "When a long run ends, read what it needs from you first."

### Cómo pedir

- **Decir qué es "hecho" y dejarlo correr.** Tarea entera en un mensaje, con la línea de meta. El ejemplo: "Done means: every endpoint uses the new client, the old client is deleted, and the test suite passes. Stop and ask me only if a test fails for a reason you can't explain." La razón que da es que sus mayores mejoras están en trabajo de varios pasos y que "Early testers had it run long coding tasks for hours with little oversight."
- **Quitar "think hard".** "Opus 5.5 always thinks before it replies, and it decides how much." En sus pruebas en un producto de chat, quitar un "think carefully" hizo que las respuestas empezaran antes "with no clear drop in quality." Para respuestas rápidas, "Answer directly." Para cambiar cuánto piensa en Claude Code, "change effort."
- **Añadir cosas a un run en marcha** escribiendo mientras trabaja, porque reiniciar cuesta más ahora que los runs son largos.
- **En diseño, nombrar los estilos que no quieres.** Sin dirección vuelve a unos pocos estilos por defecto, y "A general instruction like "avoid a generic look" mostly swaps one default for another." Una lista de patrones concretos funciona mejor. Si lo que elige después tampoco te gusta, se añade a la lista.

### Runs largos en Claude Code

- **Decirle qué paradas quieres.** A veces se detiene a informar sin necesidad: "a summary that names the next step without taking it, an offer to continue, or a list of choices that don't block the work." Propone esta regla para CLAUDE.md:

  > When a step doesn't need my input, keep going. Put status notes in the same message as your next action.
  > Stop and ask only when you can't continue without me, or before anything destructive: deleting data, force-pushing, or changing anything outside this repository.

  Avisa de que menos paradas exigen conservar tus propios frenos: "Keep permission prompts on for destructive commands too." Para pair programming sugiere lo contrario, un plan de una línea antes y un resumen corto al final.
- **Repartir trabajo grande entre subagentes y revisar la evidencia de cada uno.** El ejemplo pide: "When a subagent reports back, check its evidence before you accept it. Finish with one table: service, affected yes or no, and the evidence."
- **La lista de tareas en un fichero.** Claude Code resume los turnos viejos cuando se llena el contexto, y una lista en fichero sobrevive a eso. Prompt: "Keep a checklist in TASKS.md. Tick each item when it's done, and add anything new you find."

### Revisar el resultado

- **Leer primero lo que necesita de ti.** Para fijar el formato del resumen final, propone en CLAUDE.md: "End every run with three headings: Blocked on me, Changed, Found."
- **Pedirle que revise el código antes que una persona.** Cita a un tester: Opus 5.5 "at its lowest effort caught more bugs than Opus 5 at high effort, with fewer false alarms." Prompt: "List only problems you'd block the merge for. For each one, give the file and line, why it's wrong, and how to show it fails."
- **Marcar lo no confirmado.** "Mark anything you couldn't confirm, and say where you looked."

### Apps de Claude

Adjuntar el gráfico o la captura en vez de transcribirlo. Pedirle que revise documentos largos buscando contradicciones de números, fechas y nombres. Pedir el fichero terminado y no un esquema. En proyectos con chats largos, declarar las respuestas anteriores como cerradas, porque a veces "goes back over an earlier answer while it thinks about a short follow-up", salvo en análisis largos donde un paso posterior puede corregir uno anterior.

### Mensajes marcados

Es el primer Opus con salvaguardas de bio y ciber "Fable-level". Un mensaje marcado pasa a un modelo más viejo y la sesión sigue ahí. "Finding security vulnerabilities in source code is allowed." La revisión cubre toda la conversación, ficheros y resultados de búsqueda incluidos. En Claude Code: `/model` para volver, Esc dos veces para editar el último mensaje, `/config` para que pregunte antes de cambiar, `/feedback` si el flag fue un error.

Pedirle que reproduzca su razonamiento interno en la respuesta "can be declined. It's one of the flag categories." La alternativa: "Explain why you chose this approach in three sentences."

### Velocidad

`/fast` es el mismo modelo con salida más rápida, en research preview, y cuesta más por token. Sirve cuando lees cada respuesta antes de mandar la siguiente.

## 2. Cómo aplicarlo a tu forma de trabajar

Lo que sigue es interpretación mía. Revisé `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, los skills de `~/.claude/skills/`, `INDEX.md` y el handoff `2026-09-22-hydra-publish-and-launch.md`, el skill `puppets` y `CLAUDE.md` de Hydra, `src/provider/claude.rs`, el prompt de run `task-build-134.txt` y la memoria.

### Lo que ya haces bien, según el artículo

Esto no hay que cambiarlo, y conviene saberlo para no tocarlo de más.

- **Ningún "think hard".** Busqué "think hard", "think carefully", "step by step", "ultrathink" y "show your reasoning" en CLAUDE.md, skills, handoffs y los prompts de Hydra. No hay ninguno fuera de un test de Hydra, `tests/drift.rs`, que lo usa a propósito para medir tokens de thinking. Ese se queda.
- **La definición de "hecho".** La sección 1 del handoff exige "what "done" looks like", y el de Hydra la tiene escrita con dos partes. Es lo que pide el artículo en "Say what "done" looks like".
- **La lista en fichero.** La sección 3 del handoff, con `[x]` y `[ ]`, y los tickets con `Status:` en `.scratch/hydra/` cumplen la función de TASKS.md. Sobreviven a la compactación, que es el motivo que da el artículo.
- **Revisión de evidencia de subagentes.** El handoff pide un subagente Explore que verifique en frío, y Master of Puppets tiene tres jueces más tu lectura del diff. La memoria sobre composer, que "inventa números que no midió", es exactamente el caso para "check its evidence before you accept it".
- **Paradas antes de lo destructivo.** `settings.json` deniega `git push --force` y `-f`, y `guard_git.py` bloquea el push a master. El artículo pide mantener eso aunque se relajen las demás paradas.

### Cambios que sí propongo

**A. Regla de paradas en `~/.claude/CLAUDE.md`.**
Hoy tu CLAUDE.md global solo trata de unslop. No dice cuándo parar. El artículo da la regla de la sección "Tell it which stops you want". Tu versión tiene que reflejar dos cosas que ya son reglas tuyas y están dispersas en memoria y handoffs: las órdenes a la cuenta real de IBKR nunca, y el push lo haces tú. Propuesta, en español para que concuerde con la memoria:

> Cuando un paso no necesita mi opinión, sigue. Pon las notas de estado en el mismo mensaje que la siguiente acción.
> Para y pregunta solo si no puedes seguir sin mí, o antes de algo destructivo o fuera de la tarea: borrar datos o ramas, force-push, push a master, tocar ficheros fuera del repo de la tarea, cualquier orden en una cuenta real de trading.

Ojo con un conflicto. En sesiones de orquestador tú apruebas plan, tabla y cada diff, y el skill `puppets` exige esas paradas. La regla general no debe pisarlas. Por eso lleva "o fuera de la tarea" y conviene añadir una línea: "Las paradas que pide un skill cuentan como necesarias."

**B. Formato del resumen final en `~/.claude/CLAUDE.md`.**
El artículo sugiere "Blocked on me, Changed, Found". Tú trabajas como revisor con varios runs a la vez, así que leer primero lo que te bloquea ahorra más que en una sesión suelta. Propuesta: "Termina cada tarea larga con tres apartados: Pendiente de mí, Cambiado, Encontrado." Aplica igual al informe de los subagentes que lanzas.

**C. "Hecho significa" y formato de informe en los prompts de runs de Hydra.**
`task-build-134.txt` ya dice qué incluir en el informe y cuándo parar, que es bueno. Le falta una línea "Done means" explícita, que hoy vive en el ticket, y un orden de informe que ponga delante lo que el run no pudo cerrar. Cambio concreto en la plantilla de `task-build-NNN.txt`, y en el texto equivalente que genere `puppets.py launch`: una línea "Done means: <criterio del ticket>" justo después de "Your ticket is", y que el informe empiece por "Not confirmed / blocked". Respaldo: "Say what "done" looks like" y "Mark anything you couldn't confirm, and say where you looked". Esto ataca el problema que ya tienes medido de agentes que afirman mediciones que no hicieron.

**D. Esfuerzo por tarea en Hydra.**
`claude --help` en la 2.1.283 tiene `--effort <level>`. `src/provider/claude.rs` pasa `--model` y nunca `--effort`, y ni `puppets.py` ni `vendors.json` lo mencionan. El artículo dice que el control de cuánto piensa es effort, no el prompt, y cita el caso de Opus 5.5 con effort mínimo encontrando más bugs que Opus 5 en alto. Propuesta: un ticket de mapa para añadir `effort` como columna de la tabla de asignación, junto a provider, model y policy, que el proveedor claude traduzca a `--effort`. Así un juez de diffs puede correr en bajo y una tarea `high` en alto. Esto es lo único de la lista que toca código. No sé qué niveles acepta la CLI ni cómo se comporta en `--print`. Hay que medirlo antes de escribir el ticket.

**E. Instrucción de subagentes en `handoff-frank` y en tu forma de delegar.**
El skill ya delega la verificación. Lo que añadiría es la frase del artículo al prompt con el que tú, como orquestador, lanzas subagentes de lectura o auditoría: revisar su evidencia antes de aceptarla y cerrar con una tabla. En `handoff-frank/SKILL.md` no cambia nada del verificador, porque su diseño en frío ya es más estricto que lo que pide el artículo.

**F. Checklist en fichero para sesiones largas de Hermes Quant.**
El handoff de Hydra ya lo resuelve. En Hermes Quant, las rondas de supervisión duran horas y el estado vive en la conversación hasta que escribes el handoff. Pedir al inicio de cada ronda "Mantén un checklist en `docs/tickets/<fecha>/TASKS.md`, marca lo hecho y añade lo nuevo" te da la lista antes de llegar a COMPACT, y el handoff pasa a apuntar a ella. Respaldo: "Keep the task list in a file".

**G. Qué decir de los flags en el handoff de Hydra.**
La sección 5 del handoff dice que "Un clasificador corta respuestas que describen el detalle de un fallo de seguridad". El artículo explica el mecanismo: la sesión cambia a un modelo más viejo y la revisión cubre toda la conversación, ficheros incluidos. Dos consecuencias. Una sesión de orquestador que lee `SECURITY.md` o informes de hallazgos puede acabar en otro modelo sin que lo notes, así que conviene mirar la notificación y volver con `/model`. Y en runs de Hydra con `--print` no hay nadie que vea el aviso. Vale la pena comprobar si el modelo cambiado aparece en el record del run, y si no, abrir un ticket. Sin medir: no sé qué escribe la CLI en stream-json cuando cambia de modelo.

**H. Razonamiento en los prompts de jueces.**
Los prompts de jueces en `puppets.py` piden veredicto y "the strongest reason", no que reproduzcan su pensamiento. Eso está bien según el artículo. El único punto a vigilar es `showThinkingSummaries` en `claude.rs`, que devuelve el texto de thinking al stream. Es un setting, no una petición en el prompt, así que el artículo no dice nada de él. Lo menciono para que no se confunda con lo que sí desaconseja.

**I. Lista de estilos prohibidos en el prompt de la web.**
El prompt de sesión B, `2026-09-26-hephaestuslab-web-prompt.md`, reconstruye hephaestuslab.co. Es el caso exacto de "name the styles you don't want". Añadir una lista concreta: fondo crema, palabras en cursiva en títulos, etiquetas "01 / 02 / 03", etiquetas en monoespaciada, botones píldora, más lo que ya no te guste de la web actual. Si lo que salga tampoco te gusta, se suma a la lista.

## 3. Lo que el artículo no cubre o donde no aplica

- **Modelos que no son Opus 5.5.** El artículo solo habla de Opus 5.5. Hydra lanza codex, cursor-agent, agy y Claude sonnet. Nada de esto se transfiere tal cual a ellos. Tu memoria dice que codex y agy necesitan especificaciones más cerradas, no menos. Dejar correr con poca supervisión es consejo para Opus 5.5, no para tus workers.
- **"Let it cook" frente a tu regla de revisar cada diff.** El artículo empuja a menos paradas. Tu diseño de Master of Puppets tiene tres aprobaciones humanas por decisión, y el skill las exige. No veo razón para quitar ninguna: el artículo habla de paradas que "don't block the work", y las tuyas sí bloquean.
- **Máquina de 8 GB.** El artículo habla de subagentes en paralelo sin mencionar recursos. Tu límite real es swap y un run con cargo a la vez. Repartir en subagentes vale para lecturas y auditorías, no para builds en paralelo.
- **Contexto.** No da números de contexto ni de degradación. Tu `CONTEXT-PLAYBOOK.md` sigue siendo la referencia, y el artículo solo confirma que la compactación borra detalle, que es el motivo de los handoffs.
- **Coste.** No habla de tokens salvo que `/fast` cuesta más. El blog tiene dos posts relacionados que no leí: "Using Claude Code: Spending your effort" y "What a task costs on Opus 5.5", ambos del 25 de septiembre. El primero probablemente responde a la duda del cambio D.
- **Trading.** Nada del artículo toca decisiones con dinero. Tus reglas de riesgo de Hermes Quant no cambian.
- **Idioma.** Los ejemplos están en inglés. No hay nada que diga que las instrucciones en español funcionen peor, pero tampoco lo prueba.
- **Apps de Claude.** La sección 4 casi no aplica, porque trabajas en Claude Code. Lo único útil es la revisión de documentos largos, que puede servir para el Show HN o el README antes de publicar.

## 4. Cambios propuestos, por impacto

Apruébalos uno por uno. Ninguno está aplicado.

1. **Regla de paradas en `~/.claude/CLAUDE.md`**, con las paradas de trading real, push y skills incluidas. Es lo que más cambia el día a día y cuesta tres líneas. Sección 2.A.
2. **"Done means" y "Not confirmed" en los prompts de runs de Hydra**, en la plantilla `task-build-NNN.txt` y en lo que genera `puppets.py`. Ataca el fallo más caro que tienes documentado, agentes que inventan mediciones. Sección 2.C.
3. **Formato de cierre "Pendiente de mí, Cambiado, Encontrado" en `~/.claude/CLAUDE.md`.** Te ahorra leer informes enteros para encontrar la decisión que te toca. Sección 2.B.
4. **Medir `--effort` en la CLI y abrir un ticket de mapa para una columna `effort` en la tabla de Master of Puppets.** El impacto potencial es alto, pero depende de una medición que nadie hizo. Sección 2.D.
5. **Comprobar qué deja un run de Hydra cuando un mensaje se marca y cambia de modelo.** Si el record no lo dice, el ranking de proveedores aprende de un modelo que no era el pedido. Sección 2.G.
6. **Lista de estilos prohibidos en el prompt de la web de hephaestuslab.** Barato y concreto. Sección 2.I.
7. **Checklist en fichero al empezar cada ronda de Hermes Quant.** Sección 2.F.
8. **Frase de "revisa la evidencia y cierra con una tabla" al delegar auditorías a subagentes.** Sección 2.E.
