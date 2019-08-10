# coding=utf-8

import json
import os

absolutePath = os.path.abspath(__file__)

benchmarkDir = os.path.dirname(absolutePath) + "/../result/telemetry/top_10/"
baselineDir = benchmarkDir + "init/"
switcherDir = benchmarkDir + "tick/"
resultFileName = "results.json"
print(benchmarkDir)

# metrics
MetricsFMP = "timeToFirstMeaningfulPaint"
MetricsFCP = "timeToFirstContentfulPaint"
MetricsFP = "timeToFirstPaint"

MetricsAlias = {
    MetricsFMP: "FMP",
    MetricsFCP: "FCP",
    MetricsFP: "FP"
}

domains = [
    "google.com",
    "youtube.com",
    "facebook.com",
    "en.wikipedia.org",
    "amazon.com",
    "yahoo.com",
    "bing.com",
    "ask.com"
]

def checkDataType(data, intendedType):
    if type(data) != intendedType:
        raise Exception("bad type")

def checkTwoDataTypes(data, intendedType1, intendedType2):
    if type(data) != intendedType1 and type(data) != intendedType2:
        raise Exception("bad type")

def getEntry(info, metricsType):
    if metricsType == MetricsFMP:
        url = info["infos"]["values"][0]['url']
        start = info["infos"]["values"][0]["start"]
        end = info["infos"]["values"][0]["fmp"]
        return url, start, end
    
    elif metricsType == MetricsFCP:
        url = info["url"]["values"][0]
        start = info["Start"]["events"][0]["start"]
        end = info["End"]["events"][0]["start"]
        return url, start, end
    
    elif metricsType == MetricsFP:
        url = info["url"]["values"][0]
        start = info["Start"]["events"][0]["start"]
        end = info["End"]["events"][0]["start"]
        return url, start, end

def parseResult(data, metricsType):
    checkTwoDataTypes(data, list, dict)

    data_list = []
    if type(data) == list:
        data_list = data
    elif type(data) == dict:
        data_list = data.values()

    results = {}
    for url_list in data_list:
        checkDataType(url_list, list)
        if len(url_list) == 1 and url_list[0] == 0:
            continue
        if len(url_list) != 2:
            raise Exception("bad length")
        url_num = url_list[0]

        checkDataType(url_list[1], list)

        # collect the results
        for info in url_list[1]:
            url, start, end = getEntry(info, metricsType)
            # print("\t%s: %s->%s %f ms" % (url, start, end, float(end) - float(start)))
            if url in results.keys():
                # if we have this url, append this value
                results[url].append(float(end) - float(start))
            else:
                results[url] = [float(end) - float(start)]

    # duplicate and calculate the mean value
    duplicated_results = {}
    for key, value in results.items():
        duplicated_results[key] = float(sum(value)/len(value))

    return duplicated_results

def readAndParse(fileName):
    results = {}
    with open(fileName, 'r') as f:
        data = json.load(f)
        if type(data) == dict or type(data) == list:
            for d in data:
                if d["name"] == MetricsFMP:
                    results[MetricsFMP] = parseResult(d["allBins"], MetricsFMP)
                elif d["name"] == MetricsFCP:
                    results[MetricsFCP] = parseResult(d["allBins"], MetricsFCP)
                elif d["name"] == MetricsFP:
                    results[MetricsFP] = parseResult(d["allBins"], MetricsFP)
    return results

def parse(fileDir):
    results = {}

    dirs = os.listdir(fileDir)
    # get the max round
    round = 0
    for i in range(0, len(dirs)):
        if int(dirs[i]) > round:
            round = int(dirs[i])
    print("##### we have %d round(s) #####" % round)
    for i in range(1, round + 1):
        
        # print("\n\t** round %d **" % i)
        
        dirname = os.path.join(fileDir, str(i))
        if os.path.isdir(dirname):
            filename = os.path.join(dirname, resultFileName)
            if os.path.isfile(filename):
                # print("filename\t%s" % filename)

                # parse results
                fileResults = readAndParse(filename)
                results[i] = fileResults
    return results, round

def printResultForPlot():
    # print url
    print("\t-\t", end='')
    for domain in domains:
        print("%s\t" % domain, end='')
    print()

    # case INIT
    initResults, round = parse(baselineDir)
    #round = 1

    for metrics in [MetricsFP, MetricsFCP, MetricsFMP]:
        print("Baseline-%s" % MetricsAlias[metrics], end='')
        for i in range(1, round + 1):
            print("\t%d" % (i), end='')
            for domain in domains:
                found_domain = False
                for k in initResults[i][metrics].keys():
                    if k.find(domain) > 0:
                        print("\t%s" % initResults[i][metrics][k], end='')
                        found_domain = True
                        break
                if not found_domain:
                    print("\tUnknown", end='')
            print()

    # case TICK
    switcherResults, round = parse(switcherDir)
    
    for metrics in [MetricsFP, MetricsFCP, MetricsFMP]:
        print("TIM-%s" % MetricsAlias[metrics], end='')
        for i in range(1, round + 1):
            print("\t%d" % (i), end='')
            for domain in domains:
                found_domain = False
                for k in switcherResults[i][metrics].keys():
                    if k.find(domain) > 0:
                        print("\t%s" % switcherResults[i][metrics][k], end='')
                        found_domain = True
                        break
                if not found_domain:
                    print("\tUnknown", end='')
            print()
    pass

def run():
    printResultForPlot()

if __name__ == '__main__':
    # printResultByCase()
    printResultForPlot()
    pass
