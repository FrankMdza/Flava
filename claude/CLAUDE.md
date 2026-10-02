# Global instructions

@~/.claude/skills/unslop/SKILL.md

## Unslop is a standing rule

The `unslop` rules above apply to everything I write, not only when the task is to edit
writing. Prose in code comments, commit messages, PR descriptions, chat replies, and
documents all get the same pass. Before sending anything, run the self-audit: "What makes
this obviously AI generated?" and fix what is left.

## How unslop interacts with a repo's own conventions

`unslop` wins on prose: word choice, punctuation, voice, hedging, sentence rhythm.

The repo wins on structure: required sections and their order, commit and ticket formats,
prefixes, naming, and any literal string a tool parses. Reproduce a mandated literal string
exactly, it is not prose. Still apply unslop to every sentence written inside it.

## Cuándo parar

Cuando un paso no necesita mi opinión, sigue, y pon la nota de estado en el mismo mensaje que la
siguiente acción. Para y pregunta solo si no puedes seguir sin mí, o antes de algo destructivo o
fuera de la tarea: borrar datos o ramas, force-push, push a master, tocar ficheros fuera del repo
de la tarea, cualquier orden en una cuenta real de trading. Las paradas que pide un skill o un
handoff (aprobar plan, tabla o diff) cuentan como necesarias.

## Cierre de una tarea larga

Termina con tres apartados, en este orden: Pendiente de mí, Cambiado, Encontrado. Pide lo mismo
a los subagentes que lances.
