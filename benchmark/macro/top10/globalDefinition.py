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

# we use the normal chrome to download the JSON file from telemetry's results.html,
#   here is the default path where this chrome downloads files.
#     [NOTE: the user should manually grants the download permission]
_CHROME_NORMAL_DOWNLOAD_DIR = os.path.join(os.environ['HOME'], "Downloads")
print(_CHROME_NORMAL_DOWNLOAD_DIR)

# metrics for data in the JSON file
MetricsFMP = "timeToFirstMeaningfulPaint"
MetricsFCP = "timeToFirstContentfulPaint"

MetricsAlias = {
    MetricsFCP: "FCP",
    MetricsFMP: "FMP",
}

TELEMETRY_CASES_DOMAINS = [
    "google.com",
    "yelp.com",
    "eurosport.com",
    "reddit.com",
    "legacy.com",
    "twitch.tv",
    "amazon.com",
    "seatguru.com",
    "economist.com",
    "espn.com",
    "wowprogress.com",

]

# to normalize the printed information
LOG_NAME = "TELEMETRY"
def printf(msg):
    print("[%s] %s" % (LOG_NAME, msg))
