# coding=utf-8

from utils.globalDefinition import _chrome_binary_normal, _chrome_binary

_CASE_BASELINE = "Baseline"
_CASE_OURS = "Ours"

_CASES = [
    _CASE_BASELINE,
    _CASE_OURS,
]

_CASE_KEY_URL = "url"
_CASE_KEY_CHROME = "chrome"

_CASES_CONFIG = {
    _CASE_BASELINE: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/scriptChecker/microbenchmark/core.html",
        _CASE_KEY_CHROME: _chrome_binary_normal
    },
    _CASE_OURS: {
        _CASE_KEY_URL: "http://localhost:3001/taskPermission/scriptChecker/microbenchmark/core.html",
        _CASE_KEY_CHROME: _chrome_binary
    },
}

########################################################################
#
#  To parse the results
#
########################################################################

_TASK_NORMAL = "task_normal"
_TASK_RISKY = "task_risky"
_TASK_TYPE = [
    _TASK_NORMAL,
    _TASK_RISKY,
]
_CPU_CYCLE = "cpu"
_TIME_IN_US = "time_in_micro"
_SECURITY_MONITOR_DOM = "getElementByIdMethodForMainWorld"
_SECURITY_MONITOR_DOM_TARGET_ID = '''metadata:DomId:"block-form-input"'''
_SECURITY_MONITOR_SETTIMEOUTWR = "setTimeoutWR"
_SECURITY_MONITOR_SETTIMEOUT = "setTimeout"
_SECURITY_MONITOR_NETWORK = "sendMethodCallback"

_SECURITY_MONITOR_JS = "securityCheck_"
_SECURITY_MONITOR_JS_MAIN2RISKY = "main_access_risky"
_SECURITY_MONITOR_JS_RISKY2MAIN = "risky_access_main"

_SECURITY_MONITOR_TYPE_IN_CHROMIUM = [
    _SECURITY_MONITOR_DOM,
    "cookieAttributeGetter",
    _SECURITY_MONITOR_SETTIMEOUTWR,
    "ScheduleAsnycTaskForSetTimeoutWR",
    _SECURITY_MONITOR_SETTIMEOUT,
    _SECURITY_MONITOR_NETWORK,
    _SECURITY_MONITOR_JS + _SECURITY_MONITOR_JS_MAIN2RISKY,
    _SECURITY_MONITOR_JS + _SECURITY_MONITOR_JS_RISKY2MAIN,
]
_OTHER_KEY_EVENTS_IN_CHROMIUM = [
    "Initialize"
]
_KEY_EVENTS_IN_CHROMIUM = _SECURITY_MONITOR_TYPE_IN_CHROMIUM + _OTHER_KEY_EVENTS_IN_CHROMIUM
_OUTPUT_FILE_NAME = "experiement_data"
