# coding=utf-8

import json
import os

absolutePath = os.path.abspath(__file__)
resultFileName = "results.json"

# metrics
MetricsFMP = "timeToFirstMeaningfulPaint"
MetricsFCP = "timeToFirstContentfulPaint"
MetricsFP = "timeToFirstPaint"

MetricsAlias = {
    MetricsFMP: "FMP",
    MetricsFCP: "FCP",
    MetricsFP: "FP"
}

'''
    We need to differentiate China's sites and others, due to THE WALL...
'''
domains = [
    "google.com",
    "youtube.com",
    "facebook.com",
    "en.wikipedia.org",
    "amazon.com",
    #"yahoo.com",
    "bing.com",
    "ask.com"
]
domains_cn = [
    "tmall.com",
    "baidu.com",
    "qq.com",
    "sohu.com",
    "taobao.com",
    #"en.wikipedia.org",
    #"amazon.com",
]

domains_final = [
    "google.com",
    "youtube.com",
    "tmall.com",
    "facebook.com",
    "baidu.com",
    "qq.com",
    "sohu.com",
    "taobao.com",
    "en.wikipedia.org",
    "amazon.com",
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
        if duplicated_results[key] < 100:
            duplicated_results[key] = "Unknown"
            # raise Exception("Some error happens, for that the value is less than 100. <%s: %s>"
            #                 % (key, duplicated_results[key]))

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

    if not os.path.exists(fileDir):
        return results, 0

    dirs = os.listdir(fileDir)
    # get the max round
    round = 0
    for i in range(0, len(dirs)):
        if int(dirs[i]) > round:
            round = int(dirs[i])
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

def printResult(results, round, category, domains):
    for metrics in [MetricsFCP, MetricsFMP]:
        print("%s-%s" % (category, MetricsAlias[metrics]), end='')
        for i in range(1, round + 1):
            print("\t%d" % (i), end='')
            for domain in domains:
                found_domain = False
                if i not in results.keys():
                    print("\tUnknown", end='')
                    continue
                for k in results[i][metrics].keys():
                    if k.find(domain) > 0:
                        print("\t%s" % results[i][metrics][k], end='')
                        found_domain = True
                        break
                if not found_domain:
                    print("\tUnknown", end='')
            print()

def printResultForTop10(cnResults, outResults, round, category, domains):
    for metrics in [MetricsFCP, MetricsFMP]:
        print("%s-%s" % (category, MetricsAlias[metrics]), end='')
        for i in range(1, round + 1):
            print("\t%d" % (i), end='')
            for domain in domains:
                found_domain = False
                results = cnResults if domain in domains_cn else outResults
                if i not in results.keys():
                    print("\tUnknown", end='')
                    continue
                for k in results[i][metrics].keys():
                    if k.find(domain) > 0:
                        print("\t%s" % results[i][metrics][k], end='')
                        found_domain = True
                        break
                if not found_domain:
                    print("\tUnknown", end='')
            print()

def runResultForPlot(domains):
    benchmarkDir = os.path.dirname(absolutePath) + "/../result/telemetry/top_10/"
    baselineDir = benchmarkDir + "init/"
    switcherDir = benchmarkDir + "tick/"
    switcherFallbackDir = benchmarkDir + "tick-fallback/"

    # print url
    print("\t-\t", end='')
    for domain in domains:
        print("%s\t" % domain, end='')
    print()

    # case INIT
    initResults, round = parse(baselineDir)
    print("##### we have %d round(s) #####" % round)
    printResult(initResults, round, "Baseline", domains)

    # case TICK-fallback
    switcherFallbackResults, round = parse(switcherFallbackDir)
    print("##### we have %d round(s) #####" % round)
    printResult(switcherFallbackResults, round, "TIM (Fallback)", domains)

    # case TICK
    switcherResults, round = parse(switcherDir)
    print("##### we have %d round(s) #####" % round)
    printResult(switcherResults, round, "TIM", domains)

def run():
    runResultForPlot()

'''
   parse top 10
'''
def runResult():
    benchmarkDir = os.path.dirname(absolutePath) + "/../result/telemetry/top_10/"
    # print url
    print("\t-\t", end='')
    for domain in domains_cn:
        print("%s\t" % domain, end='')
    print()

    initResults, round = parse(benchmarkDir)
    print("##### we have %d round(s) #####" % round)
    printResult(initResults, round, "-", domains_cn)


'''
    parse the results for all top 10 sites
'''
def runResultForTop10():
    # 1. get the file path
    benchmarkDir = os.path.dirname(absolutePath) + "/../result/telemetry/top_10_final/"
    cnDir = benchmarkDir + "cn/"
    outDir = benchmarkDir + "out/"

    # 2. subpath name
    initDirName, tickDirName, tickFallbackDirName = "init/", "tick/", "tick-fallback/"

    # print url
    print("\t-\t", end='')
    for domain in domains_final:
        print("%s\t" % domain, end='')
    print()

    # 3. parse cn's sites
    # case INIT
    cnInitResults, cnRound = parse(cnDir + initDirName)
    outInitResults, outRound = parse(outDir + initDirName)
    print("##### we have %d round(s) #####" % outRound)
    printResultForTop10(cnInitResults, outInitResults, outRound, "Baseline", domains_final)

    # case TICK-fallback
    cnTickFallbackResults, cnRound = parse(cnDir + tickFallbackDirName)
    outTickFallbackResults, outRound = parse(outDir + tickFallbackDirName)
    print("##### we have %d round(s) #####" % outRound)
    printResultForTop10(cnTickFallbackResults, outTickFallbackResults, outRound, "TIM (Fallback)", domains_final)

    # case TICK
    cnTickResults, cnRound = parse(cnDir + tickDirName)
    outTickResults, outRound = parse(outDir + tickDirName)
    print("##### we have %d round(s) #####" % outRound)
    printResultForTop10(cnTickResults, outTickResults, outRound, "TIM", domains_final)
    pass


if __name__ == '__main__':
    # runResultForPlot(domains_cn)
    # runResult()
    runResultForTop10()
    pass
