# coding=utf-8

import logging
import os
import random
from utils.executor import *
from run_script.run import RunUrl

from document_domain import _dir, _urls_dir
from utils.logger import _logger, _log_filename
from utils.globalDefinition import _random_sample


class RunSubDomains(object):
    def __init__(self, domain):
        # the urls for a domain
        self._urls_dir = _urls_dir
        # to save the Chrome's logs
        self._results_dir = os.path.join(_dir, "results")
        self._results_log_filename = os.path.join(_dir, "run-subdomain.log")

        # create an EMPTY directory to save results
        execute("rm -rf " + self._results_dir + " || true")
        execute("mkdir -p " + self._results_dir + " || true")

    def run(self):
        if not os.path.exists(self._urls_dir):
            raise Exception("%s does not exist" % self._urls_dir)

        sites = os.listdir(self._urls_dir)
        for site in sites:
            filepath = os.path.join(self._urls_dir, site)

            # results dir
            results_dir = os.path.join(self._results_dir, site)
            execute("mkdir -p " + results_dir + " || true")

            with open(filepath, 'r') as f:
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
                    r = RunUrl(url, results_dir + "/" + filename)

                    # collect the frame info for that url. See |RunUrl.frame_info|
                    _logger.info("######## frame info is: " + str(r.frame_info))
                    if r.frame_info and len(r.frame_info.keys()) > 1:
                        _logger.info("\t\t---> Multiple FRAMES")

                f.close()

        # save logs
        execute("cp %s %s" % (_log_filename, self._results_log_filename))


def run(domain):
    RunSubDomains(domain).run()
