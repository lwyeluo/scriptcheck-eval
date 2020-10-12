# coding=utf-8

from utils.globalDefinition import _chrome_binary_normal, _chrome_binary

_CASE_BASELINE = "Baseline"
_CASE_OURS_NORMAL = "Ours-Normal"
_CASE_OURS_RESTRICTED = "Ours-Restricted"

_CASES = [
    _CASE_BASELINE,
    _CASE_OURS_NORMAL,
    _CASE_OURS_RESTRICTED
]

_CASE_KEY_URL = "url"
_CASE_KEY_CHROME = "chrome"

_CASES_CONFIG = {
    _CASE_BASELINE: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/yahoo/index.html",
        _CASE_KEY_CHROME: _chrome_binary_normal
    },
    _CASE_OURS_NORMAL: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/yahoo/index.html",
        _CASE_KEY_CHROME: _chrome_binary
    },
    _CASE_OURS_RESTRICTED: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/yahoo/index.restricted.html",
        _CASE_KEY_CHROME: _chrome_binary
    },
}