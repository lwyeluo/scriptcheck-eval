# coding=utf-8

import logging
import os
import random
from utils.executor import *
from run_script.run import RunUrl

from run_script import _subdomains_dir, _random_sample


class RunSubDomains(object):
    def __init__(self, domain):

        # the homepages for a domain
        self._homepage_dir = os.path.join(_subdomains_dir, domain)
        self._homepage_file = os.path.join(self._homepage_dir, "reachable_subdomains")
        # to save the Chrome's logs
        self._results_dir = os.path.join(self._homepage_dir, "results")

        # create an EMPTY directory to save results
        execute("rm -rf " + self._results_dir + " || true")
        execute("mkdir -p " + self._results_dir + " || true")

    def run(self):
        logging.info(">>> initial file name is " + self._homepage_file)
        with open(self._homepage_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                url = line.strip("\n").strip(' ')

                # generate a unique name for the results
                filename = url.replace('/', ',')
                if len(filename) > 30:
                    filename = filename[:30]
                filename += ''.join(random.sample(_random_sample, 10))

                logging.info("[url, filename] = %s, %s" % (url, filename))

                # run Chrome with that url
                r = RunUrl(url, self._results_dir + "/" + filename)

                # collect the frame info for that url. See |RunUrl.frame_info|
                logging.info(r.frame_info)
                if r.frame_info and len(r.frame_info.keys()) > 1:
                    logging.info("\t\t---> Multiple FRAMES")

            f.close()


def run(domain):
    RunSubDomains(domain).run()
