# coding=utf-8

import os
import pickle
import math
import json

from utils.globalDefinition import _malicious_set_dir
from utils.globalDefinition import _chrome_binary_name, _chrome_binary_normal, _chrome_binary
from utils.executor import executeByList
from utils.regMatch import strip_into_csv

__COOKIE_GET__ = "get_cookie"
__COOKIE_SET__ = "set_cookie"
__DOM__ = "dom"
__XHR__ = "xhr"

__KEYS__ = [__COOKIE_GET__, __COOKIE_SET__, __DOM__, __XHR__]

class CountLog(object):
    def __init__(self, log_path):
        self._log_path = log_path

        self._feature_dom_block = '''"The task does not have the permission to access the DOM [url, info, is_task_sensitive] = '''
        self._feature_cookie_get_block = '''"The task does not have the permission to access the cookie. [host url] = '''
        self._feature_cookie_set_block = '''"The task does not have the permission to set the cookie. [host url, val] = '''
        self._feature_xhr_block = '''The task does not have the permission to to issue XHR [host_url, request_url] = '''
        self._feature_dict = {
            __COOKIE_GET__: self._feature_cookie_get_block,
            __COOKIE_SET__: self._feature_cookie_set_block,
            __XHR__: self._feature_xhr_block,
            __DOM__: self._feature_dom_block
        }
        self._feature_console = '''", source: '''
        self._host_origin = "http://host.com:3001"

        self.results = {}
        for k in __KEYS__:
            self.results[k] = 0

    def count(self):
        self.results = {}
        for k in __KEYS__:
            self.results[k] = 0
        f = open(self._log_path, "r", encoding="ISO-8859-1")
        content = f.readlines()
        idx, length = -1, len(content)
        while idx < length - 1:
            idx += 1
            line = content[idx].strip("\n")

            for fea_type, fea_info in self._feature_dict.items():
                if fea_info in line:
                    while self._feature_console not in line:
                        idx += 1
                        line += content[idx].strip("\n")
                    line.replace("\n", "")

                    print(line)

                    _, _, d = line.rpartition(fea_info)
                    first, _, last = d.rpartition('''", source: ''')
                    host_url, _, _ = first.partition(''',''')
                    _, _, last = last.rpartition(''',''')
                    third_url, _, _ = last.partition(''' (''')

                    if self._host_origin not in host_url or third_url.endswith(".html"):
                        continue

                    self.results[fea_type] += 1

        f.close()

    def get_detected_count(self):
        count = 0
        for d in __KEYS__:
            count += self.results[d]
        return count

    def get_results(self):
        return self.results

class Parse(object):
    def __init__(self, malicious_dir):
        self._results_dir = malicious_dir

        self._total_failed_js = set()
        self._total_parsed_js = set()
        self._total_benign_js = set()

        self._total_count = {}

    def check_run_error(self, path):
        f = open(path, "r", encoding="ISO-8859-1")
        for line in f.readlines():
            if line.find(", source:") > 0:
                for d in ["Uncaught ReferenceError:", "Uncaught TypeError:", "Uncaught SyntaxError"]:
                    if d in line:
                        f.close()
                        return False
        f.close()
        return True

    def strip_js_filepath(self, path):
        if not isinstance(path, str):
            return path
        idx = path.find(self._results_dir)
        if idx == 0:
            return path[idx + len(self._results_dir):]
        return path

    def run(self):
        self._total_failed_js = set()
        self._total_parsed_js = set()
        self._total_benign_js = set()
        self._total_count = {}

        years = os.listdir(self._results_dir)
        for year in years:
            p = os.path.join(self._results_dir, year)
            if not os.path.isdir(p):
                continue

            cmd = ["find", p, "-name", "*.js"]
            print(cmd)
            files = executeByList(cmd)
            for i, script in enumerate(files.split("\n")):
                if not os.path.isfile(script):
                    continue

                if not self.check_run_error(script):
                    self._total_failed_js.add(script)
                    self._total_count[self.strip_js_filepath(script)] = {}
                    for k in __KEYS__:
                        self._total_count[self.strip_js_filepath(script)][k] = -1
                    continue

                self._total_parsed_js.add(script)

                print("\n\n\t\t[PATH] = [%s]\n" % script)

                # parse that log
                p = CountLog(script)
                p.count()
                if p.get_detected_count() == 0:
                    self._total_benign_js.add(script)
                    self._total_count[self.strip_js_filepath(script)] = {}
                    for k in __KEYS__:
                        self._total_count[self.strip_js_filepath(script)][k] = -1
                else:
                    results = p.get_results()
                    self._total_count[self.strip_js_filepath(script)] = results

        return self._total_count

class Compare(object):
    def __init__(self, results_dir):
        self._results_dir = results_dir

        self._results_raw_file = os.path.join(self._results_dir, "compare_results_raw.csv")

    def write_results(self, _total_count_normal, _total_count_our):
        scripts = set()
        for script in _total_count_our.keys():
            scripts.add(script)
        for script in _total_count_normal.keys():
            scripts.add(script)

        for script in scripts:
            if script not in _total_count_normal.keys() or script not in _total_count_our.keys():
                raise Exception("Does not fit, we cannot find %s" % script)

        with open(self._results_raw_file, 'w') as f:
            f.write("SCRIPT,BASELINE-COOKIE-GET,BASELINE_COOKIE_SET,BASELINE-DOM,BASELINE-XHR,BASELINE-CNT,"
                    "OUR-COOKIE-GET,OUR_COOKIE_SET,OUR-DOM,OUR-XHR,OUR_CNR,COMPARE")

            for script in scripts:
                data = strip_into_csv("%s" % script) + ","

                cnt_normal = _total_count_normal[script]
                num = 0
                for k in __KEYS__:
                    num += cnt_normal[k]
                    data += "%d," % cnt_normal[k]
                data += "%d," % num

                cnt_our = _total_count_our[script]
                num = 0
                for k in __KEYS__:
                    num += cnt_our[k]
                    data += "%d," % cnt_our[k]
                data += "%d," % num

                is_equal = True
                for d in __KEYS__:
                    if cnt_normal[d] != cnt_our[d]:
                        is_equal = False
                data += "Y" if is_equal else "N"
                data += "\n"

                f.write(data)

    def run(self):
        dirname_normal = os.path.join(self._results_dir, "results-" + _chrome_binary_name[_chrome_binary_normal])
        dirname_our = os.path.join(self._results_dir, "results-" + _chrome_binary_name[_chrome_binary])
        if not os.path.exists(dirname_normal) or not os.path.exists(dirname_our):
            raise Exception("cannot found path %s or %s" % (dirname_normal, dirname_our))

        _total_count_normal = Parse(dirname_normal).run()
        _total_count_our = Parse(dirname_our).run()

        self.write_results(_total_count_normal, _total_count_our)

    def test(self):
        dirname_normal = os.path.join(self._results_dir, "results-" + _chrome_binary_name[_chrome_binary_normal])
        dirname_our = os.path.join(self._results_dir, "results-" + _chrome_binary_name[_chrome_binary])
        if not os.path.exists(dirname_normal) or not os.path.exists(dirname_our):
            raise Exception("cannot found path %s or %s" % (dirname_normal, dirname_our))

        path = "angler/201506/ek_angler_2015_06_21.js"
        p = CountLog(os.path.join(dirname_normal, path))
        p.count()
        print(p.get_results())


def run():
    print("hello...")
    Compare(_malicious_set_dir).run()

def test():
    Compare(_malicious_set_dir).test()
