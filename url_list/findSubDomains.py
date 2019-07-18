# coding=utf-8

import os
from multiprocessing import Process, Manager
from subdomain_tracker import sublist3r
from url_list import _subdomains_dir
from utils.executor import execute


class FindSubDomain(object):

    def __init__(self, domain):
        self.domain = domain

        # get the filename
        filepath = os.path.join(_subdomains_dir, domain)
        if not os.path.exists(filepath):
            execute("mkdir -p %s" % filepath)

        self.output_filename = os.path.join(filepath, "raw_subdomains")

        self.threads = 40
        self.ports = None
        self.verbose = True
        self.enable_bruteforce = True

        # the final results
        self.subdomains = []

    def run(self):
        print(">>> parse the sub-domains for %s" % self.domain)
        self.subdomains = sublist3r.main(self.domain, self.threads,
                                         self.output_filename, self.ports, silent=False,
                                         verbose=self.verbose,
                                         enable_bruteforce=self.enable_bruteforce, engines=None)
        print(">>> done!")

    def runWithMulitpleProcess(self, zone, domain, return_dict):
        print("\n\n>>> parse the sub-domains for %s" % domain)
        subdomains = sublist3r.main(domain, self.threads, None, self.ports, silent=False,
                                    verbose=self.verbose,
                                    enable_bruteforce=self.enable_bruteforce, engines=None)
        print("\n\n%s DONE!" % domain)
        return_dict[zone] = subdomains

    def runWithDomainList(self):
        if self.domain != 'compute.amazonaws.com':
            raise Exception("runWithDomainList() is only for compute.amazonaws.com")

        # fulfill the domain list
        zones = [
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "ca-central-1",
            "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1",
            "ap-east-1", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
            "ap-southeast-1", "ap-southeast-2", "ap-south-1",
            "sa-east-1",
        ]

        # collect the results for each process
        return_dict = Manager().dict()
        jobs = []

        # start process
        for zone in zones:
            domain = "%s.%s" % (zone, self.domain)
            p = Process(target=self.runWithMulitpleProcess, args=(zone, domain, return_dict))
            p.daemon = False
            jobs.append(p)
            p.start()

        # wait for the termination
        for job in jobs:
            job.join()

        # save results
        with open(self.output_filename, "w") as f:
            for zone in zones:
                subdomains = return_dict[zone]
                for subdomain in subdomains:
                    f.write("%s\n" % subdomain)
            f.close()

        print(">>> done!")


def run(domain):
    if domain == 'compute.amazonaws.com':
        FindSubDomain(domain).runWithDomainList()
    else:
        FindSubDomain(domain).run()


if __name__ == '__main__':
    domain = "blog.csdn.net"
    FindSubDomain(domain).run()
