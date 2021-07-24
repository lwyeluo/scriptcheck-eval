# coding=utf-8

from utils.globalDefinition import _chrome_binary_normal, _chrome_binary

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

_HOST_ = "localhost"
SITE_URL = {
    "chartjs": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/chartjs/index.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/chartjs/index.html" % _HOST_
    },
    "highcharts": {
       _CASE_BASELINE: "http://%s:3001/taskPermission/top10/highcharts/index.html" % _HOST_,
       _CASE_OURS: "http://%s:3001/taskPermission/top10/highcharts/index.html" % _HOST_
    },
    "particlesjs": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/particlesjs/index.1.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/particlesjs/index.1.html" % _HOST_
    },
    "raphael": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/raphael/index.1.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/raphael/index.1.html" % _HOST_
    },
    "d3": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/d3/index.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/d3/index.html" % _HOST_
    },
    "threejs": {
       _CASE_BASELINE: "http://%s:3001/taskPermission/top10/threejs/index.2.html" % _HOST_,
       _CASE_OURS: "http://%s:3001/taskPermission/top10/threejs/index.2.html" % _HOST_
    },
    "mathjax": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/mathjax/index.1.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/mathjax/index.1.html" % _HOST_
    },
    "amcharts": {
       _CASE_BASELINE: "http://%s:3001/taskPermission/top10/amcharts/amcharts.1.html" % _HOST_,
       _CASE_OURS: "http://%s:3001/taskPermission/top10/amcharts/amcharts.1.html" % _HOST_
    },
    "supersized": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/supersized/index.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/supersized/index.html" % _HOST_
    },
    "googlecharts": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/googlecharts/index.1.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/googlecharts/index.1.html" % _HOST_
    },

    # DOMTRIS
    "domtris": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/DOM-Tetris/index.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/DOM-Tetris/index.html" % _HOST_
    },

    "googleadsense": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/experiment/AdvertisingNetworks/GoogleAdsense.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/experiment/AdvertisingNetworks/GoogleAdsense.html" % _HOST_,
    },

    "lodash": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/Lodash.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/Lodash.html" % _HOST_,
    },
    "jquery": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/jquery.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/jquery.html" % _HOST_,
    },
    "modernizr": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/Modernizr.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/Modernizr.html" % _HOST_,
    },
    "moment": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/moment.js.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/moment.js.html" % _HOST_,
    },
    "underscore": {
        _CASE_BASELINE: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/underscore.html" % _HOST_,
        _CASE_OURS: "http://%s:3001/taskPermission/top10/experiment/JavascriptLibraries/underscore.html" % _HOST_,
    },

}

IN_SITE_GRAPHICS = [
    # "chartjs",
    # "highcharts",
    # "particlesjs",
    # "raphael",
    # "d3",
    # "threejs",
    # "mathjax",
    # "amcharts",
    # "supersized",
    # "googlecharts",

    "domtris",
    # "jquery",
    # "lodash",
    # "modernizr",
    # "moment",
    # "underscore"
]

IN_SITES = IN_SITE_GRAPHICS
