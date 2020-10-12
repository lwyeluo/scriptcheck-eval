# coding=utf-8

from utils.globalDefinition import _chrome_binary_normal, _chrome_binary

_CASE_BASELINE = "Baseline"
_CASE_OURS_MAIN = "Ours-Main"
_CASE_OURS_SANDBOX = "Ours-Sandbox"
_CASE_OURS_CROSS = "Ours-Cross"

_CASES = [
    _CASE_BASELINE,
    _CASE_OURS_MAIN,
    _CASE_OURS_SANDBOX,
    _CASE_OURS_CROSS
]

_CASE_KEY_URL = "url"
_CASE_KEY_CHROME = "chrome"

_CASES_CONFIG = {
    _CASE_BASELINE: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/sandboxContext/index.main.html",
        _CASE_KEY_CHROME: _chrome_binary_normal
    },
    _CASE_OURS_MAIN: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/sandboxContext/index.main.html",
        _CASE_KEY_CHROME: _chrome_binary
    },
    _CASE_OURS_SANDBOX: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/sandboxContext/index.sandbox.html",
        _CASE_KEY_CHROME: _chrome_binary
    },
    _CASE_OURS_CROSS: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/sandboxContext/index.cross.html",
        _CASE_KEY_CHROME: _chrome_binary
    },
}