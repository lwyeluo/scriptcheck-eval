# coding=utf-8

import os
from utils.regMatch import matchRawDomainFromURL, getSiteFromURL

'''
    Show the frame structures for tested web pages, including:
        1. number of sites which embeds cross-site frames
        2. number of web pages which embeds cross-site/cross-origin frames
        3. distribution of sites which embeds cross-site frames
        4. distribution of sites which is embedded into cross-site frames
        
    parameters:
        @frames: an instance of `result_handler.finalResultForFrames.FinalResultForFrames`
        @logger:
'''
def printFrameStructures(frames, _logger):
    # log
    print("The size of frames is %d" % len(frames))
    cross_site_frames, cross_origin_frames = 0, 0
    embeded_sites = {}  # url: sites
    i = 0
    for frame in frames:
        structure = frame.getFrameStructure()
        if len(structure) <= 1:
            continue
        origin_set = set()
        for s in structure.values():
            domain = matchRawDomainFromURL(s)
            if domain:
                origin_set.add(s)
        if len(origin_set) == 1:
            continue
        cross_origin_frames += 1
        site_set = set()
        for origin in origin_set:
            site = getSiteFromURL(origin)
            if site:
                site_set.add(site)
        if len(site_set) == 1:
            continue
        cross_site_frames += 1

        # record the embeded sites
        _, _, main_site = os.path.dirname(frame.filepath).rpartition('/')
        if main_site not in site_set:
            continue

        site_set.remove(main_site)
        if main_site not in embeded_sites.keys():
            embeded_sites[main_site] = site_set
        else:
            [embeded_sites[main_site].add(s) for s in site_set]

    _logger.info("total = %d, cross-origin = %d (%f%%), cross-site = %d (%f%%), sites with cross-sites iframes=%d" %
          (len(frames), cross_origin_frames, cross_origin_frames/len(frames), cross_site_frames, cross_site_frames/len(frames),
           len(embeded_sites.keys())))

    _logger.info("################################################")
    _logger.info("\t\t\tRaw Data\t\t")
    _logger.info("################################################")
    for site, embdeds in embeded_sites.items():
        _logger.info("%s\t%d\t%s" % (site, len(embdeds), ','.join(embdeds)))

    _logger.info("################################################")
    _logger.info("\t\t\tDistribution for main frame\t\t")
    _logger.info("################################################")
    distri_main = {}
    for site, embdeds in embeded_sites.items():
        if len(embdeds) not in distri_main.keys():
            distri_main[len(embdeds)] = [site]
        else:
            distri_main[len(embdeds)].append(site)
    _logger.info("#numberOfEmbdeddedSites\t#numberOfMainSites\tMainSites")
    for l in sorted(distri_main.keys()):
        _logger.info("%d\t%d\t%s" % (l, len(distri_main[l]), ','.join(distri_main[l])))

    _logger.info("################################################")
    _logger.info("\t\t\tDistribution for embedded frame\t\t")
    _logger.info("################################################")
    collect_embed = {}
    for site, embdeds in embeded_sites.items():
        for e in embdeds:
            if e not in collect_embed.keys():
                collect_embed[e] = [site]
            else:
                collect_embed[e].append(site)
    distri_embed = {}
    for embed, sites in collect_embed.items():
        if len(sites) not in distri_embed.keys():
            distri_embed[len(sites)] = [embed]
        else:
            distri_embed[len(sites)].append(embed)
    _logger.info("#numberOfMainSites\t#numberOfEmbeddedSites\tEmbedSites")
    for l in sorted(distri_embed.keys()):
        _logger.info("%d\t%d\t%s" % (l, len(distri_embed[l]), ','.join(distri_embed[l])))