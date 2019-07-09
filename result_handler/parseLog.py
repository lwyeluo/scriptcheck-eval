# coding=utf-8

import re

class ParseLog(object):
    def __init__(self, file_name):
        self.file_name = file_name

        # some indicators
        self._feature = "updated frame chain"

        # save the results
        self.vuln_frames = [] # the frame chain whose size >= 2
        self.vuln_cross_origin_frames = [] # the frame chain which has multiple origins
        self.max_len_of_frame_chain = 0 # the max length of frame chains
        self.max_len_of_cross_origin_frame_chain = 0
        self.larger_cross_origin_frame_chain = ''

        self.handle()

    def getVulnFrames(self):
        return self.vuln_frames

    def getVulnCorssOriginFrames(self):
        return self.vuln_cross_origin_frames

    def getMaxLengthOfFrameChain(self):
        return self.max_len_of_frame_chain

    def getMaxLengthOfCrossOriginFrameChain(self):
        return self.max_len_of_cross_origin_frame_chain

    def getLargerCrossOriginFrameChain(self):
        return self.larger_cross_origin_frame_chain

    def matchFrameChain(self, frame_chain):
        ret = []
        reg = "-(\d{1,}:\d{1,})_([^\s/]+://[^\s/]+/)(.*)"
        m = re.match(reg, frame_chain)
        if m:
            frame_id, origin, remain = m.group(1), m.group(2), m.group(3)
            ret.append({
                'id': frame_id,
                'origin': origin
            })
            if remain != "":
                ret += self.matchFrameChain(remain)
        return ret

    def handle(self):
        print(">>> HANDLE %s" % self.file_name)
        f = open(self.file_name, "r", encoding="ISO-8859-1")

        for line in f.readlines():
            line = line.strip("\n")
            if self._feature in line:
                line = line[line.index(self._feature) : ]
                _, _, remain = line.partition("=")
                if remain == "":
                    continue
                frame_chain = remain.split(',')[1].strip(' ')
                if frame_chain == "":
                    continue
                frames = self.matchFrameChain(frame_chain)
                # update the max size of frame chain
                if len(frames) > self.max_len_of_frame_chain:
                    self.max_len_of_frame_chain = len(frames)
                # for frame chain whose size is 1, we ignore it
                if len(frames) < 2:
                    continue
                # record frame chain whose size >= 2
                self.vuln_frames.append(frames)
                # record frame chain which has multiple origins
                origins = []
                for frame in frames:
                    if frame['origin'] not in origins:
                        origins.append(frame['origin'])
                    if len(origins) > 1:
                        self.vuln_cross_origin_frames.append(frames)
                        # update the max size of cross-origin frame chain
                        if len(frames) > self.max_len_of_cross_origin_frame_chain:
                            self.max_len_of_cross_origin_frame_chain = len(frames)
                            self.larger_cross_origin_frame_chain = frame_chain
                        break

        f.close()
