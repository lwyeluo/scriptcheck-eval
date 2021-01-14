# coding=utf-8

import os
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary

# CASES for running telemetry
_CASE_BASELINE = "Baseline"
_CASE_OURS = "Ours"

_CASES = [
    _CASE_BASELINE,
    _CASE_OURS,
]

_CASE_KEY_CHROME = "chrome"

_CASES_CONFIG = {
    _CASE_BASELINE: {
        _CASE_KEY_CHROME: _chrome_binary_normal
    },
    _CASE_OURS: {
        _CASE_KEY_CHROME: _chrome_binary
    }
}

_COST = "cost"