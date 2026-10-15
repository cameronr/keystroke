import QtQuick
import QtTest
import "../core/Model.js" as Model

TestCase {
    name: "WebSearch"

    function test_each_engine_has_its_own_url() {
        compare(Model.searchUrl("google", "rust lifetimes"), "https://www.google.com/search?q=rust+lifetimes")
        compare(Model.searchUrl("duckduckgo", "rust lifetimes"), "https://duckduckgo.com/?q=rust+lifetimes")
        compare(Model.searchUrl("brave", "rust lifetimes"), "https://search.brave.com/search?q=rust+lifetimes")
        compare(Model.searchUrl("bing", "rust lifetimes"), "https://www.bing.com/search?q=rust+lifetimes")
        compare(Model.searchUrl("startpage", "rust lifetimes"), "https://www.startpage.com/sp/search?query=rust+lifetimes")
    }

    function test_an_unknown_engine_searches_google() {
        compare(Model.searchUrl("yahoo", "x"), "https://www.google.com/search?q=x")
        compare(Model.searchUrl(undefined, "x"), "https://www.google.com/search?q=x")
    }

    function test_the_text_cannot_add_parameters() {
        compare(Model.searchUrl("google", "a & b"), "https://www.google.com/search?q=a+%26+b")
        compare(Model.searchUrl("google", "a+b"), "https://www.google.com/search?q=a%2Bb")
        compare(Model.searchUrl("google", "a#b"), "https://www.google.com/search?q=a%23b")
        compare(Model.searchUrl("google", "a?b"), "https://www.google.com/search?q=a%3Fb")
        compare(Model.searchUrl("google", "a/b"), "https://www.google.com/search?q=a%2Fb")
        compare(Model.searchUrl("google", "héllo"), "https://www.google.com/search?q=h%C3%A9llo")
    }

    function test_rows_build_one_search_row() {
        var out = Model.rows("omarchy wallpaper", "google", "websearch")
        compare(out.length, 1)
        var row = out[0]
        compare(row.id, "websearch")
        compare(row.title, "Search Google")
        compare(row.subtitle, "omarchy wallpaper")
        compare(row.verb, "Search")
        compare(row.altVerb, "Copy URL")
        compare(row.tier, "answer")
        compare(row.score, 100)
        compare(row.action.type, "url")
        compare(row.action.url, "https://www.google.com/search?q=omarchy+wallpaper")
        compare(row.altAction.type, "copy")
        compare(row.altAction.text, row.action.url)
        compare(Model.rows("x", "bing", "websearch")[0].title, "Search Bing")
    }

    function test_empty_text_returns_nothing() {
        compare(Model.rows("", "google", "websearch"), [])
        compare(Model.rows("   \t  ", "google", "websearch"), [])
        compare(Model.rows(undefined, "google", "websearch"), [])
    }

    function test_settings_offer_every_engine() {
        var setting = Model.SETTINGS[0]
        compare(setting.options, Object.keys(Model.ENGINES))
        verify(setting.options.indexOf(setting["default"]) >= 0)
        compare(setting["default"], "google")
    }
}
