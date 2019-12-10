import os
from utils.regMatch import matchRawDomainFromURL, getSiteFromURL
from result_handler.finalResultForFrames import FinalResultListForFrames
from utils.tld import levelOfDomain

'''
    Show the events to set document.domain for tested web pages, including:
        1. subdomains setting domain to its super-domain (e.g.  v.qq.com -> qq.com)
        2. subsubdomains setting domain to its super-domain (e.g.  main.v.qq.com -> v.qq.com)

    parameters:
        @frames: an instance of `result_handler.finalResultForFrames.FinalResultForFrames`
        @logger:
'''

def printSetDomains(frames, _logger):
    results = FinalResultListForFrames(frames)

    # {old_domain: {new_domain: number}}
    set_domains = results._raw_set_domains[results._restricted_key]
    _logger.info("The number of subdomains setting document.domain: %d" % len(set_domains))

    levels = {}  # {old_level : {new_level: [domains], new_level: [domains]}, ...}
    for domain in set_domains.keys():
        level = levelOfDomain(domain)
        for new_domain in set_domains[domain].keys():
            new_level = levelOfDomain(new_domain)
        if level not in levels.keys():
            levels[level] = {
                new_level: ["%s -> %s" % (domain, new_domain)]
            }
        elif new_level not in levels[level].keys():
            levels[level][new_level] = ["%s -> %s" % (domain, new_domain)]
        else:
            levels[level][new_level].append("%s -> %s" % (domain, new_domain))

    # levels of domains
    for level in levels.keys():
        _logger.info("%d" % level)
        for new_level in levels[level].keys():
            _logger.info("\t-> %d (%d)" % (new_level, len(levels[level][new_level])))
            _logger.info("\t\t %s" % ', '.join(levels[level][new_level]))