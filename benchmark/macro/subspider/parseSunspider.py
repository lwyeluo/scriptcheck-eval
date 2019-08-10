# coding=utf-8

import json
import os
import codecs
import numpy as np

absolutePath = os.path.abspath(__file__)

benchmarkDir = os.path.dirname(absolutePath) + "/../result/sunspider/"
baselineDir = benchmarkDir + "init-results/"
switcherDir = benchmarkDir + "tick-results/"
print(benchmarkDir)

benchmarkExampleResults = '''
============================================
RESULTS (means and 95% confidence intervals)
--------------------------------------------
Total:                 1249.9ms +/- 0.8%
--------------------------------------------

  3d:                   148.6ms +/- 3.7%
    cube:                63.6ms +/- 4.5%
    morph:               17.7ms +/- 11.4%
    raytrace:            67.3ms +/- 6.6%

  access:                80.8ms +/- 3.7%
    binary-trees:         7.6ms +/- 6.6%
    fannkuch:            35.2ms +/- 2.7%
    nbody:               12.7ms +/- 6.5%
    nsieve:              25.3ms +/- 9.9%

  bitops:                86.0ms +/- 1.7%
    3bit-bits-in-byte:    5.3ms +/- 9.1%
    bits-in-byte:        11.8ms +/- 4.8%
    bitwise-and:         56.7ms +/- 1.3%
    nsieve-bits:         12.2ms +/- 3.7%

  controlflow:            7.2ms +/- 10.3%
    recursive:            7.2ms +/- 10.3%

  crypto:               101.3ms +/- 2.7%
    aes:                 45.5ms +/- 5.7%
    md5:                 26.0ms +/- 1.3%
    sha1:                29.8ms +/- 1.9%

  date:                 126.6ms +/- 3.0%
    format-tofte:        69.4ms +/- 4.8%
    format-xparb:        57.2ms +/- 2.8%

  math:                 316.6ms +/- 2.4%
    cordic:              23.0ms +/- 7.0%
    partial-sums:       284.0ms +/- 2.5%
    spectral-norm:        9.6ms +/- 9.4%

  regexp:                 6.9ms +/- 15.8%
    dna:                  6.9ms +/- 15.8%

  string:               375.9ms +/- 2.1%
    base64:              52.9ms +/- 17.1%
    fasta:               44.0ms +/- 4.3%
    tagcloud:           126.7ms +/- 3.2%
    unpack-code:         83.3ms +/- 2.8%
    validate-input:      69.0ms +/- 3.4%
'''

class parseSunspider:

    def __init__(self):
        self.benchmarkNames = []
        self.subBenchmarkNames = {}

        self.getBenchmarkNamesFromExample()
        pass

    def getBenchmarkNamesFromExample(self):
        currentBenchmark = ""

        for line in benchmarkExampleResults.split("\n"):
            if len(line) < 5:
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
        # print(self.benchmarkNames)
        # print(self.subBenchmarkNames)

    def parseFile(self, fileName):
        results = {}
        with codecs.open(fileName, 'r', encoding='utf-8',
                 errors='ignore') as f:
            content = f.readlines()
            for line in content:
                if ":" not in line:
                    continue
                
                n, _, r = line.partition(":")
                t, _, p = r.partition("+/-")
                name = n.strip()
                time = t.strip()
                results[name] = [time]
        return results

    def printResultForPlot(self):
        round = len(os.listdir(baselineDir))
        
        # init
        initResults = {}
        for f in range(1, round + 1):
            filename = os.path.join(baselineDir, str(f))
            fileResults = self.parseFile(filename)

            if not initResults:
                initResults = fileResults
            else:
                for key in initResults.keys():
                    initResults[key].append(fileResults[key][0])

        # switcher
        switcherResults = {}
        for f in range(1, round + 1):
            filename = os.path.join(switcherDir, str(f))
            fileResults = self.parseFile(filename)

            if not switcherResults:
                switcherResults = fileResults
            else:
                for key in switcherResults.keys():
                    switcherResults[key].append(fileResults[key][0])

        # print
        print("-\t-", end="")
        for key in self.benchmarkNames:
            print("\t%s" % key, end="")
        print()

        print("Baseline", end='')
        for i in range(1, round + 1):
            print("\t%d" % (i), end='')
            for key in self.benchmarkNames:
                if key in initResults.keys():
                    time = initResults[key][i - 1]
                    if time.endswith("ms"):
                        print("\t%f" % float(time[:-2]), end="")
                    else:
                        print("\tUnknown", end="")
                else:
                    print("\tUnknown", end="")
            print()

        print("TIM", end='')
        for i in range(1, round + 1):
            print("\t%d" % (i), end='')
            for key in self.benchmarkNames:
                if key in switcherResults.keys():
                    time = switcherResults[key][i - 1]
                    if time.endswith("ms"):
                        print("\t%f" % float(time[:-2]), end="")
                    else:
                        print("\tUnknown", end="")
                else:
                    print("\tUnknown", end="")
            print()

if __name__ == '__main__':
    parser = parseSunspider()
    parser.printResultForPlot()
    pass