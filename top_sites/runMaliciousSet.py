# coding=utf-8

import os
import shutil
from utils.executor import *
from run_script.run import RunUrl

from utils.globalDefinition import _malicious_set_dir, _log_filename
from run_script.globalDefinition import *
from utils.logger import _logger

from utils.globalDefinition import _cache_for_Chrome_filepath, _node_run_url_filename_kraken
from utils.globalDefinition import _node_run_url_filename, _node_run_url_filename_dromeao
from utils.globalDefinition import _timeout_for_node_kraken_benchmark, _timeout_for_node
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary
from utils.globalDefinition import _chrome_binary_name


class RunMaliciousSet(object):
    def __init__(self, chrome_type=_chrome_binary):
        self._chrome_type = chrome_type
        chrome_type_name = _chrome_binary_name[chrome_type]

        self._web_server_dir = "/home/luowu/workspace/web-scenario/"
        self._web_server_addr = "http://host.com:3001/"
        self._third_server_addr = "http://third-party.com:3001/"

        self._test_html_rel = "taskPermission/scriptChecker/malicious-set/"
        self._test_html = self._web_server_addr + self._test_html_rel + "test.html"
        self._run_html = self._web_server_addr + self._test_html_rel + "run.html"

        self._feature = "TOBEUPDATED"

        # self._set_rel_dir = "taskPermission/scriptChecker/malicious-set/infosec_bjtu_edu-cn-wangwei-page_id=85/"
        self._set_rel_dir = "taskPermission/scriptChecker/malicious-set/js-malicious-dataset/"
        self._set_abs_dir = self._web_server_dir + self._set_rel_dir

        # the urls for a domain
        self._results_dir = os.path.join(_malicious_set_dir, "results-%s" % chrome_type_name)

        self._results_crash_filename = os.path.join(_malicious_set_dir, "crashed-url-%s" % chrome_type_name)
        self._crashed_urls = []

        if not os.path.exists(self._set_abs_dir) or not os.path.isdir(self._set_abs_dir):
            raise Exception("Cannot find the malicious set: %s" % self._set_abs_dir)
        if not os.path.exists(self.convertWebToFS(self._test_html)):
            raise Exception("Cannot find test.html: %s" %
                            self.convertWebToFS(self._test_html))

        # create an EMPTY directory to save results
        execute("rm -rf " + self._results_dir + " || true")
        execute("mkdir -p " + self._results_dir + " || true")

    '''
        Some caches for Chrome must be cleared, otherwise the latency for Chrome is too high
    '''
    def clearChromeInternal(self):
        if os.path.exists(_cache_for_Chrome_filepath):
            shutil.rmtree(_cache_for_Chrome_filepath)

        # run Chrome for the welcome webpage
        print(">>> Welcome to Chrome")
        filepath = os.path.join(self._results_dir, "test")
        r = RunUrl("https://www.baidu.com", filepath, node_filename=_node_run_url_filename,
                   timeout=_timeout_for_node,
                   timeout_for_node=_timeout_for_node,
                   chrome_binary=self._chrome_type)
        time.sleep(5)
        return r.flag

    def convertWebToFS(self, url):
        return url.replace(self._web_server_addr, self._web_server_dir)

    def update3rdSrc(self, third_url):
        test_html = self.convertWebToFS(self._test_html)
        run_html = self.convertWebToFS(self._run_html)

        url = third_url.replace(self._web_server_addr, self._third_server_addr)
        print("stripped to url: ", url)
        print(run_html)

        outfile = open(run_html, "w")
        outfile.truncate()
        outfile.close()

        outfile = open(run_html, "w")
        with open(test_html, "r") as infile:
            lines = infile.readlines()
            for line in lines:
                if line.find(self._feature) <= 0:
                    outfile.write(line)
                    continue

                data = line.replace(self._feature, url)
                outfile.write(data)
        outfile.close()

        outfile = open(run_html, "r")
        lines = outfile.readlines()
        outfile.close()
        if "".join(lines).find(url) <= 0:
            raise Exception("failed to update3rdSrc: %s" % url)

    def run(self):
        years = os.listdir(self._set_abs_dir)
        page_idx = 0

        for i, year in enumerate(years):
            year.replace(" ", "\ ")
            p = os.path.join(self._set_abs_dir, year)
            if not os.path.isdir(p):
                continue
            print(p)
            cmd = ["find", p, "-name", "*.js"]
            print(cmd)
            files = executeByList(cmd)

            for i, script in enumerate(files.split("\n")):
                if not os.path.isfile(script):
                    continue
                script_url = script.replace(self._web_server_dir, self._web_server_addr)

                script_dir = os.path.dirname(script).replace(self._set_abs_dir, "")
                script_name = os.path.basename(script)

                # results dir
                results_dir = os.path.join(self._results_dir, script_dir)
                cmd = ["mkdir", "-p", results_dir, "||", "true"]
                executeByList(cmd)

                # update the test.html
                self.update3rdSrc(third_url=script_url)

                # whether needs to clear cache
                if page_idx % 100 == 0:
                    self.clearChromeInternal()
                page_idx += 1

                print(page_idx, script_url, script_dir, script_name, results_dir)

                # run Chrome with that url
                r = RunUrl(self._run_html, results_dir + "/" + script_name,
                           node_filename=_node_run_url_filename,
                           timeout_for_node=60,
                           chrome_binary=self._chrome_type)
                if r.flag == CHROME_RUN_FLAG_CRASH:
                    print("!!!! this URL[%s] is crash!!!" % script_url)
                    self._crashed_urls.append(script_url)

        # save crashed urls
        with open(self._results_crash_filename, 'w') as fp:
            for url in self._crashed_urls:
                fp.write("%s\n" % url)


def run():
    RunMaliciousSet(chrome_type=_chrome_binary_normal).run()
    RunMaliciousSet(chrome_type=_chrome_binary).run()
