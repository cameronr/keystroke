# Web search

Force a web search from the [Keystroke](../../README.md) command palette. Type
`g rust lifetimes` or `g omarchy wallpaper` and the palette returns exactly one
row: the search page for your text on the engine you picked. Enter opens it in
your default browser; Ctrl+Enter copies the URL instead. Nothing else is
offered, because the point is to leave the palette and go to the engine.

Turn it on under **Extensions > Web search > Enabled**, like every extension.

## When rows appear

Only for the typed command, or while you are inside the extension's own screen.
An ordinary query stays quiet: Web search never competes with applications,
files or the matcher for text it was not asked about. A typed command is
exclusive, so while `g ` is on the field nothing else answers.

## Settings

- **Search engine**: Google (default), DuckDuckGo, Brave Search, Bing or
  Startpage. The engine decides the row's title and the URL it opens.

The trigger word itself is the reserved **Prefix** setting, reachable from
Keystroke Settings > Web search > Prefix, so `g` can become `s`, `web`, or
whatever you would rather type. The engine list and the URL builder read one
table in `core/Model.js`, so a choice in Settings always has a URL behind it.

## URL building

Your text is percent-encoded and appended to the engine's search prefix, with
spaces sent as `+` the way the engines' own forms send them. Everything else
that a search URL cares about stays encoded, so `a & b` becomes `a+%26+b`: your
text cannot close the parameter and add one of its own.

## Dependencies and data access

None. No processes, no network calls, no files, no caches, no setup step. The
only side effects are host effects run when you activate the row: Enter runs
`xdg-open <url>` and Ctrl+Enter runs `wl-copy`. Nothing of this extension runs
while it is off; while it is on, a query builds one row and nothing else, and
only when the command or the extension's screen is active.

## Limits

It opens the engine's results page in your browser. It does not fetch results
into the palette: the searching happens there, not here.

## Verification

```sh
bin/keystroke check-extensions extensions/websearch
python3 extensions/websearch/tests/palette_check.py
```

Tests cover URL building per engine, encoding that cannot inject parameters,
the row shape and empty-text silence. The offscreen palette check covers
load/unload with the switch, command routing, the engine setting, a renamed
prefix and the extension's own screen, including that screen's scoped queries
under Smart Match: a blocked request ("how to center a div") and an arithmetic
one ("27 plus 90") keep their single row with the typed text.
