# coding=utf-8
import logging

class FinalResult(object):

    def __init__(self, domain='', reachable=False, rank=-1, url='',
                 max_frame_chain=None, max_cross_origin_frame_chain=None, larger_cross_origin_frame_chain=None,
                 cross_origin_frame_chains=None):
        self.domain = domain
        self.reachable = reachable
        self.rank = rank
        self.url = url
        self.max_frame_chain = [] if not max_frame_chain else max_frame_chain
        self.max_cross_origin_frame_chain = [] if not max_cross_origin_frame_chain else max_cross_origin_frame_chain
        self.larger_cross_origin_frame_chain = [] if not larger_cross_origin_frame_chain else larger_cross_origin_frame_chain
        if cross_origin_frame_chains:
            self.cross_origin_frame_chains = cross_origin_frame_chains
        else:
            self.cross_origin_frame_chains = []

        self.has_vuln_frame_chains = []
        self.has_cross_origin_frame_chains = []
        self.file_names = []

    def setReachable(self, reachable):
        self.reachable = reachable

    def setRank(self, rank):
        self.rank = rank

    def setUrl(self, url):
        self.url = url
    
    def setDomain(self, domain):
        self.domain = domain
    
    def appendMaxLenFrameChain(self, max_frame_chain):
        self.max_frame_chain.append(max_frame_chain)

    def appendMaxLenCrossOriginFrameChain(self, max_cross_origin_frame_chain):
        self.max_cross_origin_frame_chain.append(max_cross_origin_frame_chain)

    def appendLargerLCrossOriginFrameChain(self, larger_cross_origin_frame_chain):
        self.larger_cross_origin_frame_chain.append(larger_cross_origin_frame_chain)
    
    def appendCrossOriginFrameChains(self, cross_origin_frame_chains):
        self.cross_origin_frame_chains.append(cross_origin_frame_chains)

    def appendResultFileName(self, filename):
        self.file_names.append(filename)

    def updateHasVulnFrameChains(self):
        if not self.max_frame_chain:
            return
        self.has_vuln_frame_chains = []
        for length in self.max_frame_chain:
            is_vuln = True if length > 1 else False
            self.has_vuln_frame_chains.append(is_vuln)

    def updateHasCrossOriginFrameChains(self):
        if not self.cross_origin_frame_chains:
            return
        self.has_cross_origin_frame_chains = []
        for frame_chain in self.cross_origin_frame_chains:
            is_vuln = True if frame_chain else False
            self.has_cross_origin_frame_chains.append(is_vuln)

    def collectLargestFrameChain(self):
        self.largest_len_frame_chain = 0
        self.largest_len_cross_origin_frame_chain = 0
        self.largest_cross_origin_frame_chain = ''
        self.file_name = ""
        self.is_vuln, self.is_cross_origin_vuln = False, False
        for i in range(0, len(self.max_frame_chain)):
            if self.max_frame_chain[i] > self.largest_len_frame_chain or \
                    (self.max_frame_chain[i] == self.largest_len_frame_chain and self.has_cross_origin_frame_chains[i]):
                self.largest_len_frame_chain = self.max_frame_chain[i]
                self.largest_len_cross_origin_frame_chain = self.max_cross_origin_frame_chain[i]
                self.largest_cross_origin_frame_chain = self.larger_cross_origin_frame_chain[i]
                self.file_name = self.file_names[i]
                self.is_vuln = self.has_vuln_frame_chains[i]
                self.is_cross_origin_vuln = self.has_cross_origin_frame_chains[i]

    def getMetadataOfLargestLenFrameChain(self):
        return self.largest_len_frame_chain

    def getMetadataOfLargestLenCrossOriginFrameChain(self):
        return self.largest_len_cross_origin_frame_chain

    def getMetadataOfLargestCrossOriginFrameChain(self):
        return self.largest_cross_origin_frame_chain

    def getMetadataOfVuln(self):
        return self.is_vuln

    def getMetadataOfCrossOriginVuln(self):
        return self.is_cross_origin_vuln

    def getMetadataOfFileName(self):
        return self.file_name

    def collectMetadata(self):
        self.updateHasVulnFrameChains()
        self.updateHasCrossOriginFrameChains()
        self.collectLargestFrameChain()

    def convertToDict(self):
        return {
            self.domain: {
                'reachable': self.reachable,
                'rank': self.rank,
                'url': self.url,
                'max_frame_chain': self.max_frame_chain,
                'cross_origin_frame_chains': self.cross_origin_frame_chains
            }
        }

    def convertToStr(self):
        return str(self.convertToDict())

    def print(self):
        data = str(self.rank) + '\t' + self.domain + '\t' + self.url + '\t' + str(self.reachable)
        if self.max_frame_chain:
            data += '\t' + '\t'.join([str(size) for size in self.max_frame_chain])
            data += '\t' + '\t'.join([str(d) for d in self.has_vuln_frame_chains])
            data += '\t' + '\t'.join([str(d) for d in self.has_cross_origin_frame_chains])
            data += '\t' + '\t'.join(['"' + str(d) + '"' for d in self.file_names])
        else:
            data += '\t' * 3 * 4

        # for max case
        data += '\t' + str(self.largest_len_frame_chain) + '\t' + str(self.is_vuln) + \
            '\t' + str(self.is_cross_origin_vuln) + '\t' + self.file_name
        
        logging.info(data)

    def printReachable(self):
        if self.reachable:
            self.print()

    @classmethod
    def printTag(cls):
        basic_tag = "rank\tdomain\turl\treachable\tmax_frame_chain\t\t\thas_vuln_frame_chain\t\t\thas_cross_origin_frame_chain\t\t\tfile_names\t\t\t"
        max_tag = "largest\tis_vuln\tis_cross_origin_vuln\tfile_name\t"
        logging.info("\n" + basic_tag + max_tag + "\n")

class FinalResultList(object):

    def __init__(self, results):
        self._results = results
        self._log = logging
        # the distribution of frame chains
        self._dist_frame_chain = {}  # {sizeOfFrameChain: Domains}
        self._dist_cross_origin_frame_chain = {}  # {sizeOfFrameChain: CrossOriginDomains}
        self._dist_cross_origin = {}  # {sizeOfCrossOriginFrameChain: CrossOriginDomains}
        # domains which has cross-origin frame chains
        self._domains_with_cross_origin_fc = {}  # {domain: {'filename': filename, 'sizeOfCrossOriginFC': sizeOfCrossOriginFC}
        # number of tested_websites
        self._tested_websites = 0

        self.compute()

    def compute(self):
        for i, ret in enumerate(self._results):
            if not ret.reachable:
                continue

            # computeFrameChainDistribution
            length = ret.getMetadataOfLargestLenFrameChain()
            if length in self._dist_frame_chain:
                self._dist_frame_chain[length].append(ret.domain)
            else:
                self._dist_frame_chain[length] = [ret.domain]

            # computeDomainsWithCrossOriginFrameChain
            is_cross_origin_vuln = ret.getMetadataOfCrossOriginVuln()
            if is_cross_origin_vuln:
                if length in self._dist_cross_origin_frame_chain:
                    self._dist_cross_origin_frame_chain[length].append(ret.domain)
                else:
                    self._dist_cross_origin_frame_chain[length] = [ret.domain]

                filename = ret.getMetadataOfFileName()
                length_of_cross_origin = ret.getMetadataOfLargestLenCrossOriginFrameChain()
                largest_cross_origin_frame_chain = ret.getMetadataOfLargestCrossOriginFrameChain()
                self._domains_with_cross_origin_fc[ret.domain] = {
                    'filename': filename,
                    'sizeOfCrossOriginFC': length_of_cross_origin,
                    'largestCrossOriginFC': largest_cross_origin_frame_chain
                }

                if length_of_cross_origin in self._dist_cross_origin:
                    self._dist_cross_origin[length_of_cross_origin].append(ret.domain)
                else:
                    self._dist_cross_origin[length_of_cross_origin] = [ret.domain]

            # number of tested websites
            self._tested_websites += 1
    
    def printRawDataTable(self):
        # the table for all reachable frames
        self._log.info("\n\n")
        self._log.info("#######################################")
        self._log.info("####      TABLE for RAW DATA       ####")
        self._log.info("#######################################")

        FinalResult.printTag()
        for ret in self._results:
            ret.printReachable()

    def printDistributionTable(self):
        self._log.info("\n\n")
        self._log.info("#######################################")
        self._log.info("# TABLE for frame chain distribution  #")
        self._log.info("#######################################")

        self._log.info("length\t#domains\t#cross_origin\tcross_origin_domains\tdomains")
        keys = sorted(self._dist_frame_chain.keys())
        for k in keys:
            v = self._dist_frame_chain[k]
            d = str(k) + '\t' + str(len(v)) # length\t#domains
            if k in self._dist_cross_origin_frame_chain.keys():
                cross_v = self._dist_cross_origin_frame_chain[k]
                d += '\t' + str(len(cross_v)) # \t#cross_origin_domains
                d += '\t' + ','.join(cross_v) # \tcross_origin_domains
            else:
                d += '\t0\t-'
            d += '\t' + ','.join(v) # \tdomains
            self._log.info(d)

    def printCrossOriginDomains(self):
        self._log.info("\n\n")
        self._log.info("#######################################")
        self._log.info("# TABLE for cross-origin frame chains #")
        self._log.info("#######################################")

        vuln_size = len(self._domains_with_cross_origin_fc)
        self._log.info('The probability is %d/%d=%f%%' % (vuln_size, self._tested_websites,
                                                          vuln_size / self._tested_websites * 100))
        self._log.info('\ndomain\tlengthOfCrossOriginFC\tlargestCrossOriginFC\tfilename')
        for k, v in self._domains_with_cross_origin_fc.items():
            self._log.info("%s\t%s\t%s\t%s" % (k, str(v['sizeOfCrossOriginFC']), v['largestCrossOriginFC'], v['filename']))

    def printDistributionOfCrossOriginDomains(self):
        self._log.info("\n\n")
        self._log.info("#######################################")
        self._log.info("# Distribution for cross-origin frame chains #")
        self._log.info("#######################################")

        self._log.info('\nlengthOfCrossOriginFC\t#domains\tdomains')
        keys = sorted(self._dist_cross_origin.keys())
        for k in keys:
            v = self._dist_cross_origin[k]
            d = str(k) + '\t' + str(len(v))  # length\t#domains
            d += '\t' + ','.join(v)  # \t domains
            self._log.info(d)



