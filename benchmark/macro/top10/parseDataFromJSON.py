# coding=utf-8

import json
import numpy as np
from benchmark.macro.top10.globalDefinition import MetricsFCP, MetricsFMP, printf


# parse the metrics from a JSON file:
#   ParseDataFromJSON(in_file_to_parse=xxx).run()
class ParseDataFromJSON(object):

    def __init__(self, in_file_to_parse):
        self.file_to_parse = in_file_to_parse

    def checkDataType(self, data, intendedType):
        if type(data) != intendedType:
            raise Exception("bad type")

    def checkTwoDataTypes(self, data, intendedType1, intendedType2):
        if type(data) != intendedType1 and type(data) != intendedType2:
            raise Exception("bad type")

    def getEntry(self, info, metricsType):
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

    def parseResult(self, data, metricsType):
        self.checkTwoDataTypes(data, list, dict)

        data_list = []
        if type(data) == list:
            data_list = data
        elif type(data) == dict:
            data_list = data.values()

        results = {}
        for url_list in data_list:
            self.checkDataType(url_list, list)
            if len(url_list) == 1 and url_list[0] == 0:
                continue
            if len(url_list) != 2:
                raise Exception("bad length")
            url_num = url_list[0]

            self.checkDataType(url_list[1], list)

            # collect the results
            for info in url_list[1]:
                url, start, end = self.getEntry(info, metricsType)
                # printf("\t%s: %s->%s %f ms" % (url, start, end, float(end) - float(start)))
                if url in results.keys():
                    # if we have this url, append this value
                    results[url].append(float(end) - float(start))
                else:
                    results[url] = [float(end) - float(start)]

        # duplicate and calculate the mean value
        duplicated_results = {}
        for key, value in results.items():
            duplicated_results[key] = np.mean(value)
            if duplicated_results[key] < 100:
                duplicated_results[key] = "Unknown"
                # raise Exception("Some error happens, for that the value is less than 100. <%s: %s>"
                #                 % (key, duplicated_results[key]))

        return duplicated_results

    def run(self):
        printf(">>> PARSE %s" % self.file_to_parse)
        results = {}
        with open(self.file_to_parse, 'r') as f:
            data = json.load(f)
            if type(data) == dict or type(data) == list:
                for d in data:
                    if d["name"] == MetricsFMP:
                        results[MetricsFMP] = self.parseResult(d["allBins"], MetricsFMP)
                    elif d["name"] == MetricsFCP:
                        results[MetricsFCP] = self.parseResult(d["allBins"], MetricsFCP)
        return results