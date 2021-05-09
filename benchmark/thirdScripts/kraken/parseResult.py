# coding=utf-8

import json
import os
import codecs
import numpy as np
from benchmark.thirdScripts.kraken.globalDefinition import _CASES, _CASE_BASELINE, _CASE_OURS, _COST


benchmarkExampleResults = '''
===============================================
RESULTS (means and 95% confidence intervals)
-----------------------------------------------
Total:                        3877.8ms +/- 0.6%
-----------------------------------------------

  ai:                          280.8ms +/- 2.4%
    astar:                     280.8ms +/- 2.4%

  audio:                       495.6ms +/- 2.0%
    beat-detection:            173.3ms +/- 4.0%
    dft:                       112.2ms +/- 2.3%
    fft:                       104.7ms +/- 4.8%
    oscillator:                105.4ms +/- 1.2%

  imaging:                     516.6ms +/- 0.4%
    gaussian-blur:             199.1ms +/- 0.5%
    darkroom:                  232.6ms +/- 0.5%
    desaturate:                 84.9ms +/- 1.9%

  json:                        871.2ms +/- 0.2%
    parse-financial:           642.9ms +/- 0.3%
    stringify-tinderbox:       228.3ms +/- 0.6%

  stanford:                   1713.6ms +/- 0.5%
    crypto-aes:                267.0ms +/- 1.5%
    crypto-ccm:                528.5ms +/- 1.3%
    crypto-pbkdf2:             736.8ms +/- 0.9%
    crypto-sha256-iterative:   181.3ms +/- 2.7%
'''

_NORMAL_ = _CASE_BASELINE
_TIM_ = _CASE_OURS

class Parser(object):
    def __init__(self):
        self.benchmarkNames = []
        self.subBenchmarkNames = {}

        _dir = os.path.dirname(os.path.abspath(__file__))
        self._results_normal_filepath = os.path.join(_dir, "kraken_node_results_" + _NORMAL_)
        self._results_tim_filepath = os.path.join(_dir, "kraken_node_results_" + _TIM_)

        self._results_data_filepath = os.path.join(_dir, "experiement_data")
        self.str_kraken_cost_ = "" # used to record the cost (in String)
        self.results_cost_ = {} # used to record the cost (in Dict)

        self.getBenchmarkNamesFromExample()
        pass

    def getBenchmarkNamesFromExample(self):
        currentBenchmark = ""

        for line in benchmarkExampleResults.split("\n"):
            if len(line) < 5:
                continue

            if line[0] == '#':
                continue

            if ":" not in line:
                continue

            if line.startswith("Total:"):
                # all overhead
                self.benchmarkNames.append("Total")

            elif line[2] != ' ':
                # here is the benchmark name
                name, _, remain = line.partition(":")
                self.benchmarkNames.append(name.strip())
                currentBenchmark = name.strip()
                self.subBenchmarkNames[currentBenchmark] = []

            elif line[4] != ' ':
                # here is the subBenchmark name
                name, _, remain = line.partition(":")
                self.subBenchmarkNames[currentBenchmark].append(name.strip())
        print(self.benchmarkNames)
        print(self.subBenchmarkNames)

    def parse(self, filepath):
        round = 0
        results = []
        with open(filepath, "r") as f:
            line = f.readline()
            print(line.strip("\n"))
            while line:
                print(line)
                # find for a new round
                while line.find(">>>") != 0:
                    line = f.readline()
                if str(round) not in line:
                    line = f.readline()
                    continue

                print("!!! A new round -> ", line.strip("\n"))
                line = f.readline()
                if line.find(">>>") == 0:
                    continue
                round += 1
                results.append({})
                # collect the data for this round
                while line and line.find(">>>") != 0:
                    if ":" not in line:
                        # this is not the data we expect, skip it
                        line = f.readline()
                        continue
                    n, _, r = line.partition(":")
                    t, _, p = r.partition("+/-")
                    # remove unuseful symbol in name
                    d_, i_ = n, len(n)
                    for i in range(0, i_):
                        if not d_[i].isalpha():
                            continue
                        else:
                            d_ = d_[i:]
                            break
                    print(n, d_)
                    name, time = d_.strip(), t.strip()
                    results[round - 1][name] = time
                    print(line.strip("\n"), '\t->\t', name, time)
                    # read the next line
                    line = f.readline()
            print("end. round=%d" % round)
        return results

    def printAndRecord(self, data, end="\n"):
        self.str_kraken_cost_ += data + end
        print(data, end=end)

    def writeDataIntoFile(self):
        with open(self._results_data_filepath, 'a') as f:
            f.write("\n\n")
            f.write(self.str_kraken_cost_)

    def run(self):
        # parse the results
        results_normal = self.parse(self._results_normal_filepath)
        results_tim = self.parse(self._results_tim_filepath)

        if len(results_normal) != len(results_tim):
            raise Exception("The round of NORMAL (%d) and TIM (%d) is not equal" % (
                len(results_normal), len(results_tim)
            ))

        # to calculate the average value
        results_average = {}
        for benchmark in self.benchmarkNames:
            results_average[benchmark] = {_NORMAL_: 0, _TIM_: 0}

        with open(self._results_data_filepath, "w") as f: # to save the benchmark results
            # record the raw data into file
            for benchmark in self.benchmarkNames:
                f.write("\t%s-%s" % (benchmark, _NORMAL_))
            for benchmark in self.benchmarkNames:
                f.write("\t%s-%s" % (benchmark, _TIM_))
            f.write("\n")

            for i in range(0, len(results_normal)):
                f.write("%s" % str(i))
                for benchmark in self.benchmarkNames:
                    usage = float(results_normal[i][benchmark].replace("ms", ""))
                    results_average[benchmark][_NORMAL_] += usage
                    f.write("\t" + str(usage))
                for benchmark in self.benchmarkNames:
                    usage = float(results_tim[i][benchmark].replace("ms", ""))
                    results_average[benchmark][_TIM_] += usage
                    f.write("\t" + str(usage))
                f.write("\n")

        # calculate the average value
        for benchmark in self.benchmarkNames:
            d1, d2 = results_average[benchmark][_NORMAL_], results_average[benchmark][_TIM_]
            v1, v2 = d1 / len(results_normal), d2 / len(results_tim)
            self.results_cost_[benchmark] = {_NORMAL_: v1, _TIM_: v2, _COST: v2/v1}

        # print the cost
        self.printf()

    def printf(self):
        # print the final
        for benchmark in self.benchmarkNames:
            self.printAndRecord("\t&\t\\textbf{%s}" % benchmark, end="")
        self.printAndRecord(" \\\\ \\hline")

        self.printAndRecord(_CASE_BASELINE, end="")
        for benchmark in self.benchmarkNames:
            self.printAndRecord("\t&\t%f" % self.results_cost_[benchmark][_NORMAL_], end="")
        self.printAndRecord(" \\\\ \\hline")

        self.printAndRecord(_CASE_OURS, end="")
        for benchmark in self.benchmarkNames:
            self.printAndRecord("\t&\t%f" % self.results_cost_[benchmark][_TIM_], end="")
            self.printAndRecord(" (%.3f\\%%)" % ((self.results_cost_[benchmark][_COST]-1)*100), end="")
        self.printAndRecord(" \\\\ \\hline")

        self.writeDataIntoFile()


def run():
    Parser().run()