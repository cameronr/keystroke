.pragma library

// The Web search extension's decisions: which engines exist, how a search URL
// is built and what the one row looks like. Pure functions, so
// tests/tst_websearch.qml covers them without a shell.

var NAME = "Web search"
var ICON = "󰊭"
var COLOR = "#4285f4"
var DEFAULT_KEY = "websearch"

// The single source of truth: the settings enum and the URL builder both read
// this table, so the choices a user can pick and the URLs we can build cannot
// drift apart. id: [display name, search URL prefix]. Display names become
// "Search <name>" row titles, so they stay short and never repeat the word.
var ENGINES = {
  google: ["Google", "https://www.google.com/search?q="],
  duckduckgo: ["DuckDuckGo", "https://duckduckgo.com/?q="],
  brave: ["Brave", "https://search.brave.com/search?q="],
  bing: ["Bing", "https://www.bing.com/search?q="],
  startpage: ["Startpage", "https://www.startpage.com/sp/search?query="]
}

var ENGINE_IDS = Object.keys(ENGINES)

var SETTINGS = [
  { key: "engine", type: "enum", label: "Search engine", "default": "google", options: ENGINE_IDS,
    description: "Where the search opens" }
]

// The search page for `text`. An unknown or missing engine is Google: a stale
// or hand-edited setting should open a search, not fail.
//
// Spaces become + the way the engines' own forms send them; everything else
// stays percent-encoded, so the text cannot add parameters to the URL.
function searchUrl(engine, text) {
  var e = ENGINES[engine] || ENGINES.google
  return e[1] + encodeURIComponent(text).replace(/%20/g, "+")
}

// Rows for the palette: exactly one for any non-empty text, none for empty.
function rows(text, engine, key) {
  var q = String(text || "").trim()
  if (!q) return []
  var e = ENGINES[engine] || ENGINES.google
  var url = searchUrl(engine, q)
  // A fixed score keeps the row out of the default matcher: the query is
  // search terms, not words of the title, and a zero score would drop the row.
  // The answer tier keeps it through Smart Match's intent filters, which drop
  // item rows for blocked or family requests ("how to center a div", "install
  // rust"); inside this extension's screen the search is the explicit request.
  return [{ id: key, title: "Search " + e[0], subtitle: q, icon: ICON, verb: "Search",
            tier: "answer", score: 100,
            action: { type: "url", url: url }, altAction: { type: "copy", text: url }, altVerb: "Copy URL" }]
}
