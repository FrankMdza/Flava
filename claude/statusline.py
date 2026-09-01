#!/usr/bin/env python3
"""Claude Code statusline — two lines.

  Work Repos · feature/PROJ-123 · opus-5 1M  [██░░░░░░...]  90k/1M · 9%
  base 59k · convo 159k · tools 39% resp 54% · in 917k out 381k · $9.16 · 166 msgs

Contract verified on Claude Code 2.1.220: CC runs this script as an ephemeral process on
every refresh and hands it the payload on stdin. The payload already carries
`context_window`, built by CC from the model's EFFECTIVE window. This script NEVER hits
the network.

Graceful degradation (non-negotiable):
  window    payload.context_window.context_window_size → thresholds[model].window → 200k
  live      payload.context_window.total_input_tokens  → last usage in transcript → n/a
  line 2    transcript → if it cannot be read, the cost line survives
  global    any exception → minimal line and ALWAYS exit 0.
            The statusline must never break the prompt.
"""

import json
import os
import re
import sys

HOME = os.path.expanduser("~")
THRESHOLDS_PATH = os.path.join(HOME, ".claude", "model-thresholds.json")

BAR_CELLS = 20
NOMINAL_WINDOW = 200_000

# Fallback marks if model-thresholds.json cannot be read.
FALLBACK_MARKS = {"window": None, "hifi": 32_000, "compact": 150_000, "dump": 400_000}

# The model id arrives in several shapes: "claude-opus-5", "opus[1m]", "opus-5[1m]".
ALIASES = {
    "opus": "claude-opus-5",
    "sonnet": "claude-sonnet-5",
    "haiku": "claude-haiku-4-5",
    "fable": "claude-fable-5",
}

USE_COLOR = os.environ.get("NO_COLOR") is None

GREEN = "32"
YELLOW = "33"
ORANGE = "38;5;208"
RED = "31"
DIM = "2"


def paint(code, text):
    if not USE_COLOR:
        return text
    return "\033[{0}m{1}\033[0m".format(code, text)


def fmt(n):
    """90339 -> 90k · 3800000 -> 3.8M · 1000000 -> 1M"""
    n = int(n)
    if n >= 1_000_000:
        s = "{0:.1f}".format(n / 1_000_000)
        if s.endswith(".0"):
            s = s[:-2]
        return s + "M"
    if n >= 1_000:
        return "{0:.0f}k".format(n / 1_000)
    return str(n)


# --------------------------------------------------------------------------- marks


def load_thresholds():
    try:
        with open(THRESHOLDS_PATH, "r", encoding="utf-8") as fh:
            table = json.load(fh)
        if isinstance(table, dict):
            return table
    except Exception:
        pass
    return {"_default": dict(FALLBACK_MARKS)}


def resolve_marks(model_id, table):
    """Normalize the model id down to a table entry. Ends at _default."""
    candidates = []
    if model_id:
        raw = str(model_id).strip()
        stripped = re.sub(r"\[1m\]", "", raw, flags=re.IGNORECASE).strip()
        candidates += [raw, stripped, stripped.lower()]
        base = stripped.lower()
        for short, full in ALIASES.items():
            if base == short or base.startswith(short):
                candidates.append(full)

    for key in candidates:
        entry = table.get(key)
        if isinstance(entry, dict):
            return entry

    # prefix match in both directions: covers dated ids (claude-sonnet-5-20260101)
    for key in candidates:
        if not key:
            continue
        for name, entry in table.items():
            if name.startswith("_") or not isinstance(entry, dict):
                continue
            if name.startswith(key) or key.startswith(name):
                return entry

    entry = table.get("_default")
    return entry if isinstance(entry, dict) else dict(FALLBACK_MARKS)


def clamp_marks(marks, window):
    """Clip the marks to the effective window and keep them ordered."""
    def pick(name, default):
        v = marks.get(name)
        return v if isinstance(v, int) and v > 0 else default

    hifi = min(pick("hifi", FALLBACK_MARKS["hifi"]), window)
    compact = min(pick("compact", FALLBACK_MARKS["compact"]), window)
    dump = min(pick("dump", FALLBACK_MARKS["dump"]), window)
    compact = max(compact, hifi)
    dump = max(dump, compact)
    return {"hifi": hifi, "compact": compact, "dump": dump}


def band_of(value, marks):
    if value < marks["hifi"]:
        return GREEN
    if value < marks["compact"]:
        return YELLOW
    if value < marks["dump"]:
        return ORANGE
    return RED


# Color only says HOW bad it is (traffic light), not WHAT is happening. The emoji and the
# label say that.
# (threshold, label, color, emoji, next band)
#   🧠 the model reasons at full strength · below NoLiMa's 32k line
#   👍 normal working zone                · up to Anthropic's compaction trigger
#   🧹 time to compact                    · past that trigger
#   🗑️  dump zone                          · 40% of the window heuristic
BANDS = (
    ("hifi", "HIFI", GREEN, "🧠", "WORK"),
    ("compact", "WORK", YELLOW, "👍", "COMPACT"),
    ("dump", "COMPACT", ORANGE, "🧹", "DUMP"),
)

DUMP_BAND = ("DUMP", RED, "🗑️", None)


def band_label(value, marks):
    """Returns (emoji, label, color, warning about the next threshold)."""
    for key, name, color, emoji, following in BANDS:
        if value < marks[key]:
            return emoji, name, color, "→{0} in {1}".format(following, fmt(marks[key] - value))
    name, color, emoji, _ = DUMP_BAND
    return emoji, name, color, "dump zone"


def render_bar(live, window, marks):
    """Linear bar over the whole window. Bands show through color, not through a caret.

    Filled cells use a solid block and empty ones a faint shade, both in the color of
    THEIR band — so you see how far along you are and where the thresholds fall at once.
    """
    filled = 0
    if window > 0:
        filled = int(round(live / float(window) * BAR_CELLS))
    filled = max(0, min(BAR_CELLS, filled))

    # A single color: the band you are in RIGHT NOW. Painting each stretch of the bar in
    # its own threshold color looked like brown smears and competed with the signal instead
    # of adding to it — the emoji, the label and the text color already say the state.
    # The bar answers one question only: how far along are you.
    return "[{0}{1}]".format(
        paint(band_of(live, marks), "█" * filled),
        paint(DIM, "░" * (BAR_CELLS - filled)),
    )


# ----------------------------------------------------------------------- transcript


def scan_transcript(path):
    """Session totals plus branch. Returns None if the transcript cannot be read.

    Filters isSidechain: a subagent's usage is not main-thread context.
    Pre-filters by substring before json.loads — the transcript can weigh several MB and
    this runs on every refresh.
    """
    if not path or not os.path.isfile(path):
        return None

    acc = {
        "in": 0, "cache": 0, "out": 0, "msgs": 0, "branch": None, "last_usage": None,
        # Input total of the FIRST assistant message ≈ system prompt + tool definitions +
        # MCP + memory + first prompt. It is the session's fixed floor: what you were
        # already paying before typing anything.
        "first_total": None,
        "tool_chars": 0, "asst_chars": 0, "user_chars": 0,
    }
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"gitBranch"' in line:
                m = re.search(r'"gitBranch"\s*:\s*"([^"]*)"', line)
                if m:
                    acc["branch"] = m.group(1)

            # On compaction everything before it leaves the window: the composition counters
            # reset so the percentages describe the LIVE context and not the transcript's
            # history, which still holds what was already discarded.
            if '"subtype":"compact_boundary"' in line:
                acc["tool_chars"] = acc["asst_chars"] = acc["user_chars"] = 0
                continue

            # Context composition: classified by substring and measured by line size. Fully
            # parsing a multi-MB transcript on every refresh would be expensive, and for a
            # percentage the line size is a good enough proxy.
            if '"toolUseResult"' in line or '"tool_result"' in line or '"type":"attachment"' in line:
                acc["tool_chars"] += len(line)
            elif '"type":"assistant"' in line:
                acc["asst_chars"] += len(line)
            elif '"type":"user"' in line:
                acc["user_chars"] += len(line)

            if '"usage"' not in line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if not isinstance(entry, dict) or entry.get("type") != "assistant":
                continue
            if entry.get("isSidechain"):
                continue
            message = entry.get("message")
            if not isinstance(message, dict):
                continue
            usage = message.get("usage")
            if not isinstance(usage, dict):
                continue

            acc["msgs"] += 1
            acc["last_usage"] = usage
            acc["in"] += _int(usage.get("input_tokens")) + _int(usage.get("cache_creation_input_tokens"))
            acc["cache"] += _int(usage.get("cache_read_input_tokens"))
            acc["out"] += _int(usage.get("output_tokens"))
            if acc["first_total"] is None:
                acc["first_total"] = live_from_usage(usage)
    return acc


def _int(v):
    try:
        return int(v or 0)
    except Exception:
        return 0


def live_from_usage(usage):
    if not isinstance(usage, dict):
        return None
    return (
        _int(usage.get("input_tokens"))
        + _int(usage.get("cache_creation_input_tokens"))
        + _int(usage.get("cache_read_input_tokens"))
    )


# ---------------------------------------------------------------------------- render


def _obj(payload, key):
    value = payload.get(key)
    return value if isinstance(value, dict) else {}


def build(payload):
    context = _obj(payload, "context_window")
    model = _obj(payload, "model")
    workspace = _obj(payload, "workspace")
    cost = _obj(payload, "cost")

    marks_raw = resolve_marks(model.get("id") or model.get("display_name"), load_thresholds())

    try:
        transcript = scan_transcript(payload.get("transcript_path"))
    except Exception:
        transcript = None

    # window: payload -> table -> nominal
    window = context.get("context_window_size")
    if not isinstance(window, int) or window <= 0:
        window = marks_raw.get("window")
    if not isinstance(window, int) or window <= 0:
        window = NOMINAL_WINDOW

    # live context: payload -> last usage in the transcript -> n/a
    live = context.get("total_input_tokens")
    if not isinstance(live, int) or live < 0:
        live = live_from_usage(transcript.get("last_usage")) if transcript else None

    percent = context.get("used_percentage")
    if not isinstance(percent, int) and live is not None:
        percent = min(100, max(0, int(round(live / float(window) * 100))))

    # --- line 1
    current_dir = workspace.get("current_dir") or payload.get("cwd") or ""
    head_parts = [os.path.basename(str(current_dir).rstrip("/\\")) or "~"]

    branch = transcript.get("branch") if transcript else None
    if branch and branch not in ("HEAD", "master...", ""):
        head_parts.append(branch)

    # "Opus 5 (1M context)" eats 19 columns to say what "Opus 5 1M" says.
    model_name = str(model.get("display_name") or model.get("id") or "?")
    model_name = re.sub(r"\s*\((\d+[MK]) context\)", r" \1", model_name)
    head_parts.append(model_name)
    head = " · ".join(p for p in head_parts if p)

    if live is None:
        line1 = head + "  " + paint(DIM, "context n/a")
    else:
        marks = clamp_marks(marks_raw, window)
        emoji, label, color, hint = band_label(live, marks)
        readout = "{0}/{1} · {2}%".format(fmt(live), fmt(window), percent)
        # State first, number second: what you glance at is which zone you are in, not the
        # exact figure.
        line1 = "{0}  {1}  {2} {3} {4}".format(
            head,
            render_bar(live, window, marks),
            paint("1;" + color, emoji + " " + label),
            paint(DIM, "· " + readout),
            paint(DIM, hint),
        )

    # --- line 2: what is eating the context, not just how much
    parts = []
    if transcript:
        base = transcript.get("first_total")
        if isinstance(base, int) and live is not None:
            # base = fixed floor (system + tools + MCP + memory). Lowered by turning
            # connectors off. convo = everything accumulated since; lowered by compacting
            # or delegating to subagents.
            parts.append("base " + fmt(base))
            parts.append("convo " + fmt(max(0, live - base)))

        total_chars = transcript["tool_chars"] + transcript["asst_chars"] + transcript["user_chars"]
        if total_chars > 0:
            parts.append("tools {0}% resp {1}%".format(
                transcript["tool_chars"] * 100 // total_chars,
                transcript["asst_chars"] * 100 // total_chars,
            ))

        parts.append("in {0} out {1}".format(fmt(transcript["in"]), fmt(transcript["out"])))

        # Cache hit for the LAST turn, not cumulative: the cumulative figure averages the
        # whole session and does not react when caching breaks RIGHT NOW. Only shown when
        # it drops — in normal operation it sits at 99% and as a fixed field it would be a
        # constant. The first few turns are legitimately low (cold cache), hence the msgs
        # guard. Orange rather than red: red on this bar already means DUMP.
        lu = transcript.get("last_usage") or {}
        read = _int(lu.get("cache_read_input_tokens"))
        fresh = _int(lu.get("input_tokens")) + _int(lu.get("cache_creation_input_tokens"))
        if read + fresh > 0 and transcript["msgs"] >= 5:
            hit = read * 100 // (read + fresh)
            if hit < 80:
                parts.append(paint(ORANGE, "cache {0}%".format(hit)))

    usd = cost.get("total_cost_usd")
    if isinstance(usd, (int, float)):
        parts.append("${0:.2f}".format(usd))
    if transcript:
        parts.append("{0} msgs".format(transcript["msgs"]))

    if not parts:
        return line1
    return line1 + "\n" + paint(DIM, " · ".join(parts))


def main():
    payload = {}
    try:
        raw = sys.stdin.read()
        parsed = json.loads(raw or "{}")
        if isinstance(parsed, dict):
            payload = parsed
    except BaseException:
        payload = {}

    try:
        out = build(payload)
    except BaseException:
        # Last resort: something broke, but the statusline still prints something useful.
        try:
            model = _obj(payload, "model")
            workspace = _obj(payload, "workspace")
            name = os.path.basename(str(workspace.get("current_dir") or "").rstrip("/\\")) or "~"
            out = "{0} · {1}".format(name, model.get("display_name") or model.get("id") or "?")
        except BaseException:
            out = "claude"

    sys.stdout.write(out + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
