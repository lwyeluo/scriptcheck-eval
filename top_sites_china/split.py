# coding=utf-8

import os
import math
from top_sites_china import _split_dir, _domain_filename, _webpages_dir, _max_webpage_in_one_domain
from utils.executor import execute


def split(number_of_machines):
    # 1. load the number of webpages for each domain
    url_nums = []
    sites = []  # the sites has webpages
    with open(_domain_filename, 'r') as f:
        domains = f.readlines()
        for line in domains:
            domain = line.strip("\n").strip(' ')

            webpage_filename = os.path.join(_webpages_dir, domain)

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
    for i in range(0, len(sites)):
        print("%s: %d" % (sites[i], url_nums[i]), end="\t")
    print("")

    # for each domain, we only handle at most |_max_webpage_in_one_domain| webpages
    webpage_nums = []
    for num in url_nums:
        num = num if num < _max_webpage_in_one_domain else _max_webpage_in_one_domain
        webpage_nums.append(num)

    # 2. calculate the number of webpages each machine should handle
    webpage_num = sum(webpage_nums)
    mean_num = math.ceil(webpage_num / number_of_machines)
    print(webpage_num, mean_num)

    # 3. calculate the domains for each machine
    start = 0
    domain_per_machine = []
    for machine in range(0, number_of_machines):
        total = 0
        for i in range(start, len(webpage_nums)):
            total += webpage_nums[i]
            if total >= mean_num:
                domain_per_machine.append(i - start + 1)
                start = i + 1
                total = 0
                break
    if len(domain_per_machine) == number_of_machines - 1:
        domain_per_machine.append(len(webpage_nums) - sum(domain_per_machine))
    print(domain_per_machine)

    # 3. create the dir
    execute("rm -rf %s || true" % _split_dir)
    execute("mkdir %s || true" % _split_dir)

    # 4. fulfill the data
    start = 0
    for i in range(0, number_of_machines):
        filename = os.path.join(_split_dir, "sites-%d" % i)
        execute("touch %s" % filename)

        end = start + domain_per_machine[i]
        domain_at_machine = sites[start:end]
        start = end

        with open(filename, 'w') as f:
            f.write(''.join(domain_at_machine))
            f.close()
