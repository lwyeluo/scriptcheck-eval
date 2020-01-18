# coding=utf-8

import subprocess


PYTHON_PATH = "/home/wluo/workspace/tim-evaluate/evaluate.py"

def run():
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

if __name__ == '__main__':
    while True:
        if run():
            break
    print("end")
