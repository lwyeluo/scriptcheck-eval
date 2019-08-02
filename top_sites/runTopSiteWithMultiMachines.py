# coding=utf-8

import os
import random
from utils.executor import *
from run_script.run import RunUrl

from utils.globalDefinition import _topsites_dir, _log_filename, _topsites_split_dir, _topsites_reachable_file
from utils.globalDefinition import _random_sample
from utils.logger import _logger


class RunTopSitesWithMultiMachines(object):
    def __init__(self, machine_id):

        self.machine_id = machine_id
        self._urls_dir = os.path.join(_topsites_split_dir, "sites-%d" % machine_id)

        # the homepages for a domain
        self._homepage_file = _topsites_reachable_file
        # to save the Chrome's logs
        self._results_dir = os.path.join(_topsites_dir, "results")
        self._results_log_filename = os.path.join(_topsites_dir, "results-domain.log")
        # save the Chrome's logs for the last time running script
        self._results_dir_last_time = os.path.join(_topsites_dir, "results.bak")

        # create an EMPTY directory to save results
        execute("rm -rf " + self._results_dir + " || true")
        execute("mkdir -p " + self._results_dir + " || true")

    def run(self):
        _logger.info(">>> initial file name is " + self._homepage_file)
        _logger.info(">>> urls_dir is " + self._urls_dir)

        if not os.path.exists(self._urls_dir):
            raise Exception("Please run --split MACHINE_ID first")

        # the domains we have run last time
        have_run_domains = []
        if os.path.exists(self._results_dir_last_time):
            have_run_domains = os.listdir(self._results_dir_last_time)

        # traverse all domains
        sites = os.listdir(self._urls_dir)
        for site in sites:
            # if we have run that site last time, we ignore it
            if site in have_run_domains:
                print(">>> %s has been checked, continue" % site)
                continue

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

                    _logger.info("[url, filename] = %s, %s" % (url, filename))

                    # run Chrome with that url
                    r = RunUrl(url, results_dir + "/" + filename)

                    # collect the frame info for that url. See |RunUrl.frame_info|
                    _logger.info("######## frame info is: " + str(r.frame_info))
                    if r.frame_info and len(r.frame_info.keys()) > 1:
                        _logger.info("\t\t---> Multiple FRAMES")

                f.close()

        # save logs
        execute("cp %s %s" % (_log_filename, self._results_log_filename))



def run(machine_id):
    RunTopSitesWithMultiMachines(machine_id).run()
