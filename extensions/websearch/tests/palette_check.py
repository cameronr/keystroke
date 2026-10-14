#!/usr/bin/env python3
"""Real palette offscreen and isolated HOME. Web search runs no processes and
reads no data, so there is nothing to fake: the check drives the real palette
through the switch, the command, the engine setting, a renamed prefix and the
extension's own screen."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory(prefix="keystroke-websearch-") as temp:
    work = Path(temp)
    project = work / "project"
    shutil.copytree(root, project, ignore=shutil.ignore_patterns(".git", ".claude", ".agents", ".codex", "tests", "__pycache__", "experiments"))
    (work / "qs").symlink_to("/usr/share/omarchy/shell")
    source = project / "Keystroke.qml"
    qml = source.read_text().replace("  PanelWindow {", "  Window {\n    transientParent: null\n    width: 1000; height: 800")
    qml = qml.replace("    anchors { top: true; bottom: true; left: true; right: true }\n", "")
    source.write_text("\n".join(line for line in qml.splitlines() if "exclusionMode:" not in line and "WlrLayershell." not in line))
    config = work / ".config"
    (config / "omarchy").mkdir(parents=True)
    (config / "omarchy/keystroke.json").write_text(json.dumps({"version": 1, "matching": {"mode": "off"}}))
    (work / "shell.qml").write_text('''import QtQuick
import Quickshell
import "project"
ShellRoot {
  id: test
  property int stage: 0
  property int failures: 0
  Keystroke { id: palette; omarchyPath: "/usr/share/omarchy" }
  function service() { var s = palette.registry.services["websearch"]; return s ? s.instance : null }
  function check(ok, msg) { if (!ok) { failures++; console.log("FAIL", msg) } }
  function items() { return palette.rows.filter(function(r) { return r.providerKey === "websearch" && !r.disabled }) }
  function configure(on, engine, prefix) {
    palette.applyConfigText(JSON.stringify({ version: 1, matching: { mode: "off" }, providers: {
      websearch: { enabled: on, engine: engine, prefix: prefix || "g" }
    } }))
  }
  Timer { interval: 120; running: true; repeat: true; onTriggered: {
    if (palette.pending) return
    switch (test.stage) {
    case 0:
      if (!palette.registry.manifests["websearch"]) return
      check(!service(), "disabled extension is not loaded")
      configure(true, "google")
      test.stage++; return
    case 1:
      if (!service()) return
      check(service().provider.settings[0].key === "engine", "the engine setting is exposed")
      palette.open(JSON.stringify({ query: "g rust lifetimes" }))
      test.stage++; return
    case 2:
      var row = items()[0]
      check(items().length === 1, "the command returns exactly one row: " + items().length)
      check(row && row.title === "Search Google", "the row names the engine: " + (row ? row.title : ""))
      check(row && row.subtitle === "rust lifetimes", "the subtitle is the search text: " + (row ? row.subtitle : ""))
      check(row && row.action.type === "url", "activation opens the search URL")
      check(row && row.action.url === "https://www.google.com/search?q=rust+lifetimes", "Google builds the URL: " + (row ? row.action.url : ""))
      check(row && row.altAction.type === "copy", "the alternate copies")
      check(row && row.altAction.text === row.action.url, "the alternate copies the same URL")
      palette.setQuery("rust lifetimes")
      test.stage++; return
    case 3:
      check(items().length === 0, "an ordinary query stays quiet: " + items().length)
      configure(true, "bing")
      palette.setQuery("g omarchy wallpaper")
      test.stage++; return
    case 4:
      var bing = items()[0]
      check(items().length === 1 && bing && bing.title === "Search Bing", "the engine setting renames the row: " + (bing ? bing.title : ""))
      check(bing && bing.action.url.indexOf("https://www.bing.com/search?q=omarchy") === 0, "Bing builds the URL: " + (bing ? bing.action.url : ""))
      configure(true, "google", "web")
      palette.setQuery("g omarchy")
      test.stage++; return
    case 5:
      check(items().length === 0, "the renamed prefix kills the old command: " + items().length)
      palette.setQuery("web omarchy")
      test.stage++; return
    case 6:
      check(items().length === 1, "the renamed prefix answers: " + items().length)
      palette.open(JSON.stringify({ query: "hello world", scope: "websearch" }))
      test.stage++; return
    case 7:
      var screen = items()[0]
      check(items().length === 1 && screen && screen.subtitle === "hello world", "the extension's own screen searches: " + items().length)
      configure(false, "google")
      test.stage++; return
    case 8:
      check(!service(), "disabling destroys service")
      console.log(test.failures ? "FAIL websearch palette" : "PASS websearch palette")
      Qt.quit(); stop(); return
    }
  } }
  Timer { interval: 15000; running: true; onTriggered: {
    console.log("FAIL timeout", test.stage, JSON.stringify(palette.registry.problems)); Qt.quit()
  } }
}
''')
    env = dict(os.environ, HOME=str(work), XDG_CONFIG_HOME=str(config), XDG_RUNTIME_DIR=str(work),
               QT_QPA_PLATFORM="offscreen", QT_QPA_PLATFORMTHEME="generic",
               QT_QUICK_BACKEND="software", QML_IMPORT_PATH=str(work))
    for key in ("DISPLAY", "WAYLAND_DISPLAY", "XDG_CACHE_HOME", "XDG_STATE_HOME"):
        env.pop(key, None)
    result = subprocess.run(["quickshell", "-p", str(work / "shell.qml")], env=env, capture_output=True, text=True, timeout=25)
    output = result.stdout + result.stderr
    assert "PASS websearch palette" in output and "FAIL" not in output, output
    assert "TypeError" not in output and "ReferenceError" not in output, output
    print("PASS websearch palette: load/unload with the switch, command routing, the engine setting, a renamed prefix and the extension's own screen")
