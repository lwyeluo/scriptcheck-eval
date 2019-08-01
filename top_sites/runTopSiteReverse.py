# coding=utf-8

import os
import random
import requests
from utils.executor import *
from run_script.run import RunUrl

from utils.globalDefinition import _topsites_dir, _log_filename
from utils.globalDefinition import _random_sample, _http_headers
from utils.logger import _logger


'''
    run the Alexa top sites reversely, for the purpose that running top sites with 2 machines
'''
class RunTopSitesReverse(object):
    def __init__(self):

        # the homepages for a domain
        self._homepage_file = os.path.join(_topsites_dir, "reachable_domains")
        # the urls for a domain
        self._urls_dir = os.path.join(_topsites_dir, "urls")
        # to save the Chrome's logs
        self._results_dir = os.path.join(_topsites_dir, "results")
        self._results_log_filename = os.path.join(_topsites_dir, "results-domain.log")
        # save the Chrome's logs for the last time running scritp
        self._results_dir_last_time = os.path.join(_topsites_dir, "results.bak")

        # create an EMPTY directory to save results
        execute("rm -rf " + self._results_dir + " || true")
        execute("mkdir -p " + self._results_dir + " || true")

    def isReachable(self, site):
        maybe_reachable = [
            "https://www.%s/" % site, "http://www.%s/" % site,
             "https://%s/" % site, "http://%s/" % site
        ]
        filepath = os.path.join(self._urls_dir, site)
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                url = line.strip("\n").strip(' ')
                if url in maybe_reachable:
                    # check whether this url is reachable
                    try:
                        response = requests.request("GET", url, headers=_http_headers, timeout=10,
                                                    allow_redirects=False)
                        print(">>> try %s: the status code is %d" % (url, response.status_code))
                        if response.status_code == 200:
                            return url
                    except Exception as e:
                        print("Failed to load %s" % url, e)
                    return None
        return None

    def run(self):
        _logger.info(">>> initial file name is " + self._homepage_file)

        if not os.path.exists(self._urls_dir):
            raise Exception("Please run --crawl-url first")

        # the domains we have run last time
        have_run_domains = []
        if os.path.exists(self._results_dir_last_time):
            have_run_domains = os.listdir(self._results_dir_last_time)

        # transvers all domains
        sites = os.listdir(self._urls_dir)
        for site in sites[::-1]:
            # if we have run that site last time, we ignore it
            if site in have_run_domains:
                print(">>> %s has been checked, continue" % site)
                continue

            if self.isReachable(site) is None:
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



def run():
    RunTopSitesReverse().run()
