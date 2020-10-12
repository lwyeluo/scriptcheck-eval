# coding=utf-8

import os, shutil
from utils.globalDefinition import _chrome_binary_normal, _node_run_url_filename_telemetry, _timeout_for_node, _timeout_benchmark
from benchmark.macro.top10.globalDefinition import _CHROME_NORMAL_DOWNLOAD_DIR, printf
from run_script.run import RunUrl
from run_script.globalDefinition import *

class GetJSONFromTelemetry(object):
    def __init__(self, in_html_path, in_log_path, in_save_path, in_download_filename):
        self.html_path = in_html_path
        if not os.path.isfile(self.html_path):
            raise Exception("Cannot find telemetry result file: %s" % self.html_path)
        self.log_path = in_log_path
        self.save_path = in_save_path
        if not os.path.exists(os.path.dirname(self.save_path)):
            raise Exception("Cannot store telemetry result file into: %s" % self.save_path)

        self.download_json_path = os.path.join(_CHROME_NORMAL_DOWNLOAD_DIR, in_download_filename)
        printf("\t\tdata will be downloaded into %s" % self.download_json_path)

    def clearDownloads(self):
        # the file downloaded will be automatically stored in here, we need to clear it
        if not os.path.isdir(_CHROME_NORMAL_DOWNLOAD_DIR):
            raise Exception("Cannot find Chrome's download dir: %s" % _CHROME_NORMAL_DOWNLOAD_DIR)
        files = os.listdir(_CHROME_NORMAL_DOWNLOAD_DIR)
        for file in files:
            file_path = os.path.join(_CHROME_NORMAL_DOWNLOAD_DIR, file)
            if not os.path.isfile(file_path):
                continue
            if file.find("results") == 0 and file_path.endswith(".json"):
                printf(">>> remove file: %s" % file_path)
                os.remove(file_path)

    def run(self):
        printf(">>> Welcome to Chrome for %s" % self.html_path)
        url_path = "file://" + self.html_path
        r = RunUrl(url_path, self.log_path, node_filename=_node_run_url_filename_telemetry,
                   timeout=_timeout_benchmark,
                   timeout_for_node=_timeout_benchmark,
                   chrome_binary=_chrome_binary_normal)
        return r.flag

    def run_all(self):
        self.clearDownloads()
        flag = self.run()
        if (flag == CHROME_RUN_FLAG_TELEMETRY_ERROR) or (not os.path.exists(self.download_json_path)):
            return False
        # save the results file
        printf(">>> mv download_json_path save_path")
        shutil.copy(self.download_json_path, self.save_path)
        os.remove(self.download_json_path)
        return True

    def test(self):
        return self.run_all()

