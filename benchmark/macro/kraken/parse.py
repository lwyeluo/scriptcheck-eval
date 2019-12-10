# coding=utf-8

'''
    Test the performance for TIM. The commit is 9cf5b2ef9bd6cdab4b82992ddc874dc07f731fb0
'''


import json
import os
import codecs
import numpy as np

absolutePath = os.path.abspath(__file__)

benchmarkDir = os.path.dirname(absolutePath) + "/../result/kraken/"
baselineDir = benchmarkDir + "init-results/"
switcherDir = benchmarkDir + "tim-results/"
switcherFallbackDir = benchmarkDir + "tim-fallback-results/"
print(benchmarkDir)

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
        print(self.benchmarkNames)
        print(self.subBenchmarkNames)

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

        # switcher fallback to context-based access control
        switcherFallbackResults = {}
        for f in range(1, round + 1):
            filename = os.path.join(switcherFallbackDir, str(f))
            fileResults = self.parseFile(filename)

            if not switcherFallbackResults:
                switcherFallbackResults = fileResults
            else:
                for key in switcherFallbackResults.keys():
                    switcherFallbackResults[key].append(fileResults[key][0])

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

        print("TIM fallback", end='')
        for i in range(1, round + 1):
            print("\t%d" % (i), end='')
            for key in self.benchmarkNames:
                if key in switcherFallbackResults.keys():
                    time = switcherFallbackResults[key][i - 1]
                    if time.endswith("ms"):
                        print("\t%f" % float(time[:-2]), end="")
                    else:
                        print("\tUnknown", end="")
                else:
                    print("\tUnknown", end="")
            print()

def run():
    parser = parseSunspider()
    parser.printResultForPlot()

if __name__ == '__main__':
    parser = parseSunspider()
    parser.printResultForPlot()
    pass