# coding=utf-8

import numpy as np
import os
from benchmark.thirdScripts.security_monitor.globalDefinition import _CASE_BASELINE, _CASE_OURS_NORMAL, _CASE_OURS_RESTRICTED, _CASES

_feature_normal = '''testDOMInNormalTask'''
_feature_restricted = '''testDOMIn3rdTask'''

class ParseLog(object):
    def __init__(self, filepath):
        self.filepath = filepath

        self._remain_sep = '''ms", source'''
        self._time_sep = ''': '''

        self.results = {
            _feature_normal: [],
            _feature_restricted: []
        }

    def run(self):
        print(">>> Handle ", self.filepath)
        with open(self.filepath, "r", encoding="ISO-8859-1") as f:
            content = f.readlines()

            for line in content:
                line = line.strip("\n")

                for feature in self.results.keys():
                    if feature in line:
                        _, _, r = line.partition(feature)
                        d, _, _ = r.partition(self._remain_sep)
                        _, _, t = d.partition(self._time_sep)
                        self.results[feature] = float(t)

        print(">>>>>>>>>> Raw Data in ", self.filepath)
        for feature in self.results.keys():
            print(feature, self.results[feature])

        return self.results

class Parse(object):
    def __init__(self, in_dir_name=""):
        if in_dir_name == "":
            _dir = os.path.abspath(os.path.dirname(__file__))
            self._results_tree_dir = os.path.join(_dir, "results")
        else:
            self._results_tree_dir = in_dir_name

        self._results_array = {}

        self.round = 0

    def run(self):
        if not os.path.exists(self._results_tree_dir):
            raise Exception("%s does not exist" % self._results_tree_dir)
        files = os.listdir(self._results_tree_dir)
        for file in files:
            if file.startswith("test"):
                continue
            self.round += 1
            filepath = os.path.join(self._results_tree_dir, file)
            p = ParseLog(filepath)
            results = p.run()
            found_data = False
            for r in results.keys():
                if isinstance(results[r], list):
                    continue
                found_data = True
                if r not in self._results_array.keys():
                    self._results_array[r] = [float(results[r])]
                else:
                    self._results_array[r].append(float(results[r]))
            if not found_data:
                raise Exception("Cannot obtain useful information in LOG[%s]" % filepath)
        return self._results_array


class ProcessLogs(object):

    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")

        self._results_data_filepath = os.path.join(_dir, "experiement_data")

        self.raw_results = {}  # save the raw data

        self.final_results = {}  # save the data on average

        self.str_cost_ = ""  # used to record the cost (in String)

    def parse(self):
        self.round = 0
        for case in _CASES:
            p = Parse(in_dir_name=os.path.join(self._results_tree_dir, case))
            self.raw_results[case] = p.run()
            if self.round == 0:
                self.round = p.round
            elif self.round != p.round:
                raise Exception("The round is not the same [cur_round(%d), case_round(%d:%s)]"
                                % (self.round, p.round, case))
        print(">>> the round is ", self.round)

    def writeRawDataIntoFile(self):
        with open(self._results_data_filepath, "w") as f:  # to save the benchmark results

            # print the raw data
            for t in [_feature_normal]:
                f.write("\t%s_NORMAL" % t)
            for t in [_feature_normal, _feature_restricted]:
                f.write("\t%s_TIM" % t)
            f.write("\n")
            for i in range(0, self.round):
                f.write("%d" % i)
                f.write("\t%f" % self.raw_results[_CASE_BASELINE][_feature_normal][i])
                f.write("\t%f" % self.raw_results[_CASE_OURS_NORMAL][_feature_normal][i])
                f.write("\t%f" % self.raw_results[_CASE_OURS_RESTRICTED][_feature_restricted][i])
                f.write("\n")
            f.write("\n\n\n")

    def printAndRecord(self, data, end="\n"):
        self.str_cost_ += data + end
        print(data, end=end)

    def writeDataIntoFile(self):
        with open(self._results_data_filepath, 'a') as f:
            f.write("\n\n")
            f.write(self.str_cost_)

    def printf(self):
        self.printAndRecord("\\textbf{Baseline}", end="")
        for benchmark in [_feature_normal, _feature_restricted]:
            self.printAndRecord("\t&\t\\textbf{%s}" % benchmark, end="")
        self.printAndRecord(" \\\\ \\hline")

        baseline_usage = np.mean(self.raw_results[_CASE_BASELINE][_feature_normal])
        tim_normal_usage = np.mean(self.raw_results[_CASE_OURS_NORMAL][_feature_normal])
        tim_restricted_usage = np.mean(self.raw_results[_CASE_OURS_RESTRICTED][_feature_restricted])

        self.printAndRecord("\t%f" % baseline_usage, end="")
        for d in [tim_normal_usage, tim_restricted_usage]:
            self.printAndRecord("\t&\t%f (%.3f\\%%)" % (d, (d/baseline_usage-1)*100), end="")
        self.printAndRecord(" \\\\ \\hline")

        self.writeDataIntoFile()

        print("cost:", end="\t")
        for d in [tim_normal_usage, tim_restricted_usage]:
            print((d/baseline_usage-1)*100, end="\t")
        print()

    def run(self):
        self.parse()
        self.writeRawDataIntoFile()
        self.printf()


def run():
    ProcessLogs().run()

if __name__ == '__main__':
    run()