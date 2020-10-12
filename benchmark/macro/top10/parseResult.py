# coding-utf-8

import os
import numpy as np
from benchmark.macro.top10.globalDefinition import _CASES, _CASE_BASELINE, _CASE_OURS, _COST, printf
from benchmark.macro.top10.globalDefinition import MetricsFMP, MetricsFCP, MetricsAlias, TELEMETRY_CASES_DOMAINS
from benchmark.macro.top10.getJsonFromTelemetry import GetJSONFromTelemetry
from benchmark.macro.top10.parseDataFromJSON import ParseDataFromJSON

class Parse(object):

    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")

        self._log_file_path = os.path.join(self._results_tree_dir, "results.log")

        # save the results
        self.raw_results = {}
        self.final_results = {}
        self.round = 0
        self._results_data_filepath = os.path.join(_dir, "experiement_data")
        self.str_cost_ = ""

    def collectJSONFile(self, filename, dirname):
        _download_filename = filename.replace(".html", ".json")
        if os.path.exists(os.path.join(dirname, _download_filename)):
           # we have obtained the JSON file
           return

        # downlaod JSON from the HTML files
        _file_path = os.path.join(dirname, filename)
        _save_path = os.path.join(dirname, filename.replace(".html", ".json"))
        printf(">>> downlaod JSON from the HTML files: %s -> %s" % (_file_path, _save_path))
        _p = GetJSONFromTelemetry(in_html_path=_file_path, in_log_path=self._log_file_path,
                                  in_save_path=_save_path, in_download_filename=_download_filename)
        if not _p.run_all():
            raise Exception("Cannot extract results.json from %s" % _file_path)

    def parseJSONFile(self, filename, dirname):
        _file_path = os.path.join(dirname, filename)
        return ParseDataFromJSON(in_file_to_parse=_file_path).run()

    def parseFilesInDir(self, dirpath):
        printf(">>> prepare to handle %s" % dirpath)

        _tmp_results = {}
        for metrics in MetricsAlias.keys():
            _tmp_results[metrics] = {}

        _files = os.listdir(dirpath)
        for _file in _files:
            _file_path = os.path.join(dirpath, _file)
            if not os.path.isfile(_file_path):
                continue

            if not _file.endswith(".html"):
                continue

            # retrieve JSON file if necessary
            self.collectJSONFile(filename=_file, dirname=dirpath)

            # get results from JSON file
            _r = self.parseJSONFile(filename=_file.replace(".html", ".json"), dirname=dirpath)
            # print(_r)
            for metrics in MetricsAlias.keys():
                if metrics not in _r.keys():
                    raise Exception("Cannot found key[%s] after parsing file[%s]" % (metrics, _file_path))
                for k, v in _r[metrics].items():
                    if k not in _tmp_results[metrics].keys():
                        _tmp_results[metrics][k] = v
                    else:
                        _tmp_results[metrics][k] = np.mean([_tmp_results[metrics][k], v])

        printf("<<< results for dir[%s]: " % dirpath)
        print(_tmp_results[MetricsFCP])
        # check the data is not empty
        if len(_tmp_results[MetricsFCP].keys()) == 0:
            return False
        return _tmp_results

    def parse(self):
        self.raw_results = {}

        _round = {}
        for case in _CASES:
            self.raw_results[case] = {}
            _round[case] = 0

            _results_dir = os.path.join(self._results_tree_dir, "results-%s" % case)
            if not os.path.exists(_results_dir):
                raise Exception("Cannot find dir: %s" % _results_dir)

            _dirs = sorted(os.listdir(_results_dir))
            for _dir in _dirs:
                _dir_path = os.path.join(_results_dir, _dir)
                if not os.path.isdir(_dir_path):
                    continue

                # extract the results and save into self.raw_results
                _tmp_results = self.parseFilesInDir(_dir_path)
                if _tmp_results != False:
                    self.raw_results[case][_round[case]] = _tmp_results
                    _round[case] += 1

            print(_round)

        # check the round for these cases
        _tmp_round = 0
        for case in _CASES:
            if _round[case] == 0:
                raise Exception("no data for case[%s]" % case)
            if _tmp_round == 0:
                _tmp_round = _round[case]
            elif _tmp_round != _round[case]:
                raise Exception("the round for cases are not equal")
        self.round = _tmp_round

    def writeRawDataIntoFile(self):
        with open(self._results_data_filepath, "w") as f:  # to save the benchmark results
            # print the raw data
            metrics = sorted(MetricsAlias.keys())

            for t in metrics:
                for case in _CASES:
                    f.write("%s-%s" % (case, MetricsAlias[t]))
                    for domain in TELEMETRY_CASES_DOMAINS:
                        f.write("\t%s" % domain)
                    f.write("\n")

                    for i in range(0, self.round):
                        f.write("%d" % i)
                        for domain in TELEMETRY_CASES_DOMAINS:
                            # check whether the domain exists in the results
                            _found = False
                            for k in self.raw_results[case][i][t].keys():
                                if domain in k:
                                    f.write("\t%s" % str(self.raw_results[case][i][t][k]))
                                    _found = True
                                    break
                            if not _found:
                                f.write("\tUnknown")
                        f.write("\n")
            f.write("\n\n\n")

    def printAndRecord(self, data, end="\n"):
        self.str_cost_ += data + end
        print(data, end=end)

    def writeDataIntoFile(self):
        with open(self._results_data_filepath, 'a') as f:
            f.write("\n\n")
            f.write(self.str_cost_)

    def calcAverage(self):
        metrics = sorted(MetricsAlias.keys())

        self.final_results = {}
        for domain in TELEMETRY_CASES_DOMAINS:
            self.final_results[domain] = {}
            for case in _CASES:
                self.final_results[domain][case] = {}
                for t in metrics:
                    data = []
                    for i in range(0, self.round):
                        # get the true value
                        for k in self.raw_results[case][i][t].keys():
                            if domain in k:
                                _value = self.raw_results[case][i][t][k]
                                if isinstance(_value, float):
                                    data.append(_value)
                    # calc the average value
                    self.final_results[domain][case][t] = np.mean(data)

    def printf(self):
        # calc the average value
        self.calcAverage()

        # begin to log
        for i in range(0, 3):
            print("********************************************************")
        cnt = 0
        average_cost = {}
        metrics = sorted(MetricsAlias.keys())
        for m in metrics:
            average_cost[m] = []
        _step = 6
        while True:
            idx = cnt + _step if cnt + _step <= len(TELEMETRY_CASES_DOMAINS) else len(TELEMETRY_CASES_DOMAINS)
            sites = [TELEMETRY_CASES_DOMAINS[i] for i in range(cnt, idx)]
            for domain in sites:
                for m in metrics:
                    self.printAndRecord("\t&\t\\textbf{%s-%s}" % (domain, MetricsAlias[m]), end="")
            self.printAndRecord(" \\\\ \\hline")
            self.printAndRecord(_CASE_BASELINE, end="")
            for domain in sites:
                for m in metrics:
                    self.printAndRecord("\t&\t%s" % self.final_results[domain][_CASE_BASELINE][m], end="")
            self.printAndRecord(" \\\\ \\hline")
            self.printAndRecord(_CASE_OURS, end="")
            for m in metrics:
                for domain in sites:
                    o = self.final_results[domain][_CASE_BASELINE][m]
                    n = self.final_results[domain][_CASE_OURS][m]
                    cost = (float(n) / float(o) - 1) * 100
                    average_cost[m].append(float("%.3f" % cost))
                    self.printAndRecord("\t&\t%f" % n, end="")
                    self.printAndRecord(" (%.3f\\%%)" % cost, end="")
            self.printAndRecord(" \\\\ \\hline")
            cnt += _step
            if cnt >= len(TELEMETRY_CASES_DOMAINS):
                break
        for m in metrics:
            self.printAndRecord("COST in metric[%s]: %s; Avearge: %f" % (MetricsAlias[m],
                                                                         '\t'.join([str(t) for t in average_cost[m]]),
                                                                         np.mean(average_cost[m])))

        self.writeDataIntoFile()

    def run(self):
        self.parse()
        self.writeRawDataIntoFile()
        self.printf()

def run():
    printf(">>> parse the results of telemetry benchmark")
    p = Parse()
    p.run()
