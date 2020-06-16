# coding=utf-8

import subprocess
import time


PYTHON_PATH = "/home/wluo/workspace/tim-evaluate/evaluate.py"

def run3rd():
    print("run")
    p = subprocess.Popen(["python3", PYTHON_PATH, "--third-benchmark", "run", "--script", "amcharts"])
    p.communicate()

    p2 = subprocess.Popen(["python3", PYTHON_PATH, "--third-benchmark", "parse"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p2.communicate()
    for d in stdout.decode("gb2312").split("\n"):
        print(d)
        if "overhead-site" in d and "amcharts" in d:
            cost = float(d.split(" ")[-1])
            if cost < 1:
                print("cost is too low", cost)
            elif cost > 1.05:
                print("cost is too high", cost)
            else:
                print("cost is OK", cost)
                return True
    return False

def runAsync():
    print("runAsync")
    p = subprocess.Popen(["python3", PYTHON_PATH, "--async-benchmark", "run"])
    p.communicate()

    data_size = "512k"
    _label_sync = "Sync (%s)" % data_size
    _label_all_async = "all-Async (%s)" % data_size
    _label_create0_async = "create0-Async (%s)" % data_size
    _label_create1_async = "create1-Async (%s)" % data_size
    _label_wait0_async = "wait0-Async (%s)" % data_size
    _label_wait1_async = "wait1-Async (%s)" % data_size
    _label_func_async = "func-Async (%s)" % data_size
    _label_ret_async = "ret-Async (%s)" % data_size
    _label_strip_async = "strip-Async (%s)" % data_size
    features = {
        # _label_sync: 100,
        # _label_all_async: 100,
        _label_create0_async: 0.25,
        _label_create1_async: 0.25,
        _label_wait0_async: 5.8,
        _label_wait1_async: 1.5,
        _label_func_async: 100,
        # _label_ret_async: 100
    }
    results = {}

    p2 = subprocess.Popen(["python3", PYTHON_PATH, "--async-benchmark", "parse"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = p2.communicate()
    for d in stdout.decode("gb2312").split("\n"):
        # print(data_size, d)
        if data_size not in d:
            continue
        for k in features.keys():
            if k not in d:
                continue
            data = d[len(k):].strip(" ").strip("\t")
            if data == "nan" and k == _label_create0_async:
                return False
            results[k] = float(data)
            break
    # check
    print(results)
    # if results[_label_all_async] < results[_label_sync] + results[_label_create_async]:
    #     print("\tthe time for async is too lower")
    #     return False
    # if results[_label_all_async] - results[_label_sync] > 5:
    #     print("\toverhead is too high")
    #     return False
    if results[_label_create0_async] + results[_label_create1_async] > 0.35:
        print("\tthe task creation wait too long")
        return False
    if results[_label_create0_async] - results[_label_create1_async] > 0.02:
        print("\tcreating the first task costs too long")
        return False
    if results[_label_wait0_async] + results[_label_wait1_async] > 7:
        print("\tthe async execution wait too long")
        return False
    for k in results.keys():
        if results[k] > features[k]:
            print("\t<<< In %s, data [%f] is larger than %f" % (k, results[k], features[k]))
            return False
    return True

def test3rd():
    while True:
        if run3rd():
            break
        time.sleep(10)
    print("end")

def testAsync():
    while True:
        if runAsync():
            break
    print("end")

if __name__ == '__main__':
    testAsync()
