pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import "core/Model.js" as Model

// Web search: `g <query>` returns exactly one row that opens the chosen
// engine's search page in the default browser; a typed command is exclusive,
// so nothing else answers while it is on the field. Rows appear only for the
// explicit command or on this extension's screen, keeping ordinary queries
// quiet. Ctrl+Enter copies the search URL instead of opening it. The trigger
// is renameable in Keystroke Settings, like every extension's first command.
//
// Keystroke creates this object when the user turns the extension on, injects
// `shell`, `extension` and `omarchyPath`, reads `provider`, and destroys it
// when the extension is turned off. The extension itself has no side effects:
// opening and copying are host effects run from the row.
QtObject {
  id: root
  property var shell: null
  property var extension: null
  property string omarchyPath: Quickshell.env("OMARCHY_PATH")
  readonly property string key: extension && extension.id ? String(extension.id) : Model.DEFAULT_KEY

  readonly property var provider: ({
    apiVersion: 1,
    name: Model.NAME,
    icon: Model.ICON,
    color: Model.COLOR,
    description: "Force a web search: g <query> opens the engine directly",
    settings: Model.SETTINGS,
    query: function(ctx) { return root.query(ctx) }
  })

  // Answer only the declared command or this extension's own screen.
  function query(ctx) {
    if (!ctx.command && ctx.scope !== root.key) return []
    return Model.rows(ctx.command ? ctx.command.rest : ctx.rawQuery, (ctx.settings || {}).engine, root.key)
  }
}
