# coding=utf-8

import os
import math
from utils.globalDefinition import _topsites_split_dir, _topsites_reachable_file, _topsites_urls_dir
from utils.executor import execute
from utils.regMatch import matchDomainFromURL


def split(number_of_machines):
    # 1. load the number of webpages for each domain
    url_nums = []
    sites = []  # the sites has webpages
    with open(_topsites_reachable_file, 'r') as f:
        domains = f.readlines()
        for line in domains:
            url = line.strip('\n') + '/'
            domain = matchDomainFromURL(url)
            if not domain:
                raise Exception("Bad Domain. url is %s" % url)

            webpage_filename = os.path.join(_topsites_urls_dir, domain)

            if not os.path.exists(webpage_filename):
                continue

            sites.append(domain)

            # get the row number of that file
            with open(webpage_filename, 'r') as f_url:
                count = 0
                for idx, line in enumerate(f_url):
                    count += 1
                url_nums.append(count)

                f_url.close()

    f.close()

    print(len(sites), len(url_nums))

    # 2. calculate the number of webpages each machine should handle
    webpage_num = sum(url_nums)
    mean_num = math.ceil(webpage_num / number_of_machines)
    print(webpage_num, mean_num)

    # 3. calculate the domains for each machine
    start = 0
    domain_per_machine = []
    for machine in range(0, number_of_machines):
        total = 0
        for i in range(start, len(url_nums)):
            total += url_nums[i]
            if total >= mean_num:
                domain_per_machine.append(i - start + 1)
                start = i + 1
                total = 0
                break
    if len(domain_per_machine) == number_of_machines - 1:
        domain_per_machine.append(len(url_nums) - sum(domain_per_machine))
    print(domain_per_machine)

    # 3. create the dir
    execute("rm -rf %s || true" % _topsites_split_dir)
    execute("mkdir %s || true" % _topsites_split_dir)

    # 4. fulfill the data
    start = 0
    for i in range(0, number_of_machines):
        print("\n\n>>>>> MACHINE %d \n\n" % i)
        site_dir = os.path.join(_topsites_split_dir, "sites-%d" % i)
        execute("mkdir %s || true" % site_dir)

        end = start + domain_per_machine[i]
        domain_at_machine = sites[start:end]
        start = end

        for domain in domain_at_machine:
            d_path = os.path.join(site_dir, domain)
            s_path = os.path.join(_topsites_urls_dir, domain)
            print("<<< copy %s" % domain)
            execute("cp %s %s" % (s_path, d_path))
