# coding=utf-8

import numpy as np
import os
from utils.globalDefinition import _NORMAL_, _TIM_, _COST_
from benchmark.thirdScripts.sandbox_context.globalDefinition import _CASES, _CASE_BASELINE, _CASE_OURS_MAIN
from benchmark.thirdScripts.sandbox_context.globalDefinition import _CASE_OURS_SANDBOX, _CASE_OURS_CROSS


class Features(object):
    _NORMAL_ = '_normal_'
    _RISKY_ = '_risky_'

    _feature_empty = '''function(d){}'''
    _feature_empty_normal, _feature_empty_risky = _feature_empty+_NORMAL_, _feature_empty+_RISKY_

    _feature_add1 = '''function(d){return d+1;}'''
    _feature_add1_normal, _feature_add1_risky = _feature_add1 + _NORMAL_, _feature_add1 + _RISKY_

    _feature_math = '''Math.tan(5)'''
    _feature_math_normal, _feature_math_risky = _feature_math + _NORMAL_, _feature_math + _RISKY_

    _feature_eval = '''eval("if(true)true;false")'''
    _feature_eval_normal, _feature_eval_risky = _feature_eval + _NORMAL_, _feature_eval + _RISKY_

    _feature_windowMainToS = '''windowM'''
    _feature_windwoSandboxToM = '''windowS'''

    _feature_initialize = '''initialization'''

    _feature_keys_normal = [_feature_empty_normal, _feature_add1_normal,
                            _feature_math_normal, _feature_eval_normal]
    _feature_keys_all = [_feature_empty_normal, _feature_empty_risky,
                         _feature_add1_normal, _feature_add1_risky,
                         _feature_math_normal, _feature_math_risky,
                         _feature_eval_normal, _feature_eval_risky,
                         _feature_windowMainToS, _feature_windwoSandboxToM,
                         _feature_initialize]


class ParseLog(object):
    def __init__(self, filepath):
        self.filepath = filepath

        self._remain_sep = '''ms", source'''
        self._time_sep = ''': '''

        self._initialize_tag = '''LocalWindowProxy::Initialize. Initialize a new context. [is_risky, cpu_cycle, time] =1, '''
        self._initialize_sep = ', '

        self.results = {}
        for f in Features._feature_keys_all:
            self.results[f] = []

    def run(self):
        print(">>> Handle ", self.filepath)
        with open(self.filepath, "r", encoding="ISO-8859-1") as f:
            content = f.readlines()

            for line in content:
                line = line.strip("\n")

                if self._initialize_tag in line:
                    _, _, r = line.partition(self._initialize_tag)
                    t = r.split(self._initialize_sep)[1][:-1]
                    self.results[Features._feature_initialize] = float(t) * 1000
                    # the data is in second, convert it to ms
                    print(line, t)
                else:
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
                raise Exception("Cannot obtain data from LOG: %s" % filepath)
        return self._results_array

class ProcessLogs(object):

    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")

        self._results_data_filepath = os.path.join(_dir, "experiement_data")

        self.raw_results = {}  # save the raw data

        self.final_results = {}  # save the data on average

        self._tag_base, self._tag_main, self._tag_sandbox = "Baseline", "Main Context", "Sandbox Context"
        self._tag_cost_main, self._tag_cost_sandbox = "CostMain", "CostSandbox"

        self.str_cost_ = ""  # used to record the cost (in String)

    def parse(self):
        self.round = 0
        for case in _CASES:
            p = Parse(in_dir_name=os.path.join(self._results_tree_dir, "results-"+case))
            try:
                self.raw_results[case] = p.run()
            except Exception as e:
                if case != _CASE_OURS_CROSS:
                    raise e
                else:
                    continue
            if self.round == 0:
                self.round = p.round
            elif self.round != p.round:
                raise Exception("The round is not the same [cur_round(%d), case_round(%d:%s)]"
                                % (self.round, p.round, case))

    def writeRawDataIntoFile(self):
        with open(self._results_data_filepath, "w") as f:  # to save the benchmark results

            # print the raw data
            for t in Features._feature_keys_normal:
                f.write("\t%s" % t.replace("normal", 'baseline'))
            for t in Features._feature_keys_all:
                f.write("\t%s" % t)
            f.write("\n")
            for i in range(0, self.round):
                f.write("%d" % i)
                for t in Features._feature_keys_normal:
                    f.write("\t%f" % self.raw_results[_CASE_BASELINE][t][i])
                for t in Features._feature_keys_all:
                    for case in self.raw_results.keys():
                        if case == _CASE_BASELINE:
                            continue
                        if t in self.raw_results[case].keys():
                            f.write("\t%f" % self.raw_results[case][t][i])
                            break
                f.write("\n")
            f.write("\n\n\n")

    def printAndRecord(self, data, end="\n"):
        self.str_cost_ += data + end
        print(data, end=end)

    def writeDataIntoFile(self):
        with open(self._results_data_filepath, 'a') as f:
            f.write("\n\n")
            f.write(self.str_cost_)

    def calcAverage(self, _f, _f_normal, _f_risky):
        self.final_results[_f] = {
            self._tag_base: "%.6f" % np.mean(self.raw_results[_CASE_BASELINE][_f_normal]),
            self._tag_main: "%.6f" % np.mean(self.raw_results[_CASE_OURS_MAIN][_f_normal]),
            self._tag_sandbox: "%.6f" % np.mean(self.raw_results[_CASE_OURS_SANDBOX][_f_risky]),
        }
        self.final_results[_f][self._tag_cost_main] = \
            "%.2f" % ((float(self.final_results[_f][self._tag_main])/float(self.final_results[_f][self._tag_base])-1)*100)
        self.final_results[_f][self._tag_cost_sandbox] = \
            "%.2f" % ((float(self.final_results[_f][self._tag_sandbox])/float(self.final_results[_f][self._tag_base])-1)*100)


    def printf(self):

        self.printAndRecord("\t&\t\\textbf{%s}\t&\t\\textbf{%s}\t&\t\\textbf{%s}"
                            % (self._tag_base, self._tag_main, self._tag_sandbox), end="")
        self.printAndRecord(" \\\\ \\hline")

        self.calcAverage(Features._feature_math, Features._feature_math_normal, Features._feature_math_risky)
        self.calcAverage(Features._feature_eval, Features._feature_eval_normal, Features._feature_eval_risky)
        self.calcAverage(Features._feature_empty, Features._feature_empty_normal, Features._feature_empty_risky)
        self.calcAverage(Features._feature_add1, Features._feature_add1_normal, Features._feature_add1_risky)

        for f in [Features._feature_math, Features._feature_eval,
                  Features._feature_empty, Features._feature_add1]:
            self.printAndRecord("%s\t&\t%s" % (f, self.final_results[f][self._tag_base]), end="")
            self.printAndRecord("\t&\t%s(%s%%)" % (
                self.final_results[f][self._tag_main], self.final_results[f][self._tag_cost_main]), end="")
            self.printAndRecord("\t&\t%s(%s%%)" % (
                self.final_results[f][self._tag_sandbox], self.final_results[f][self._tag_cost_sandbox]), end="")
            self.printAndRecord(" \\\\ \\hline")

        # 5. initialize
        if _CASE_OURS_CROSS in self.raw_results.keys():
            for f in [Features._feature_windowMainToS, Features._feature_windwoSandboxToM,
                      Features._feature_initialize]:
                self.printAndRecord("%s\t&\t%f\t" % (f, np.mean(self.raw_results[_CASE_OURS_CROSS][f])), end="")
                self.printAndRecord(" \\\\ \\hline")

        self.writeDataIntoFile()

    def run(self):
        self.parse()
        self.writeRawDataIntoFile()
        self.printf()

def run():
    ProcessLogs().run()

if __name__ == '__main__':
    run()