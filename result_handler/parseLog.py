# coding=utf-8

import re
import os


# represent for a series of frame chain
class FrameChain(object):
    def __init__(self):
        self.frames = []  # all frames in that frame chain
        self.frame_ids = []  # all frame ids in that frame chain
        self.chain = ""  # the final frame chain

    def isEmpty(self):
        return self.frames == []

    def append(self, frame_info):
        frame_id = frame_info['id']
        if frame_id in self.frame_ids:
            # here may be a problem if the current frame_info is not the same as the previous one
            #  do it later...
            pass
        else:
            self.frame_ids.append(frame_id)
        self.frames.append(frame_info)

    def recordJSStack(self, js_stack):
        self.frames[-1]['js_stack'] = js_stack

    def matchFrameChain(self, chain):
        ret = []
        reg = "-(\d{1,}):(\d{1,})_([^\s/]+://[^\s/]+/)(.*)"
        m = re.match(reg, chain)
        if m:
            process_id, frame_id, origin, remain = m.group(1), m.group(2), m.group(3), m.group(4)
            ret.append({
                'process_id': process_id,
                'id': frame_id,
                'origin': origin
            })
            if remain != "":
                ret += self.matchFrameChain(remain)
        return ret

    def recordChain(self, chain):
        # 1. record the chain
        self.chain = chain

        # 2. update the origins for each frame in that frame chain
        frames = self.matchFrameChain(self.chain)

        if not frames:
            # here means that we cannot extract information from chain
            self.frames = []
            return

        if len(frames) != len(self.frames):
            raise Exception("Failed to parse frame chain: %s, %s" % (str(self.frames), str(frames)))

        for i in range(0, len(frames)):
            if self.frames[i]['id'] != frames[i]['id']:
                raise Exception("Failed to parse frame chain: %s <--> %s" % (self.frames[i], frames[i]))
            self.frames[i]['origin'] = frames[i]['origin']

    def getChain(self):
        return self.chain

    def getFramesInfo(self):
        return self.frames

    def length(self):
        return len(self.frames)

    def print(self):
        for frame in self.frames:
            print(str(frame))


class ParseLog(object):
    def __init__(self, file_name, is_debug=False):
        self.file_name = file_name

        # some indicators
        self._feature_frame_chain = "updated frame chain: [num, frameChain, subject, last, " \
                                    "function_name, source_code] = "
        self._feature_metadata = "metadata is [subject_url, domain, routing_id, frame_chain_length, " \
                                 "parent_origin, parent_domain] = "
        self._feature_js_stack = ">>> BindingSecurity::PrintStack. stack is "

        # save the results
        self.vuln_frames = []  # the frame chain whose size >= 2
        self.vuln_cross_origin_frames = []  # the frame chain which has multiple origins
        self.max_len_of_frame_chain = 0  # the max length of frame chains
        self.max_len_of_cross_origin_frame_chain = 0
        self.larger_cross_origin_frame_chain = ''

        # the content in that log
        self.content = None
        # the current line index for parsing
        self.idx = -1

        self.is_debug = is_debug

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

    def completeCurrentFrameChain(self, chain, frame_chain):
        frame_chain.recordChain(chain)

    def handleFeatureMetadata(self, line, frame_chain):
        line = line[line.index(self._feature_metadata):]
        _, _, remain = line.partition("=")
        if remain == "":
            raise Exception("Bad format for metadata: " + line)

        # get the subject url and domain
        info = remain.split('", ')
        url = info[0][2:]
        domain = info[1][1:]

        remain = info[2]
        info = remain.split(',')
        if len(info) != 4:
            raise Exception("Bad format for metadata: " + line)

        frame_info = {
            'url': url,
            'domain': domain,
            'id': info[0].strip(' ').strip('"'),
            'parent_origin': info[2].strip(' ').strip('"'),
            'parent_domain': info[3].strip(' ').strip('"').strip('\n'),
        }

        frame_chain.append(frame_info)

    def handleFeatureJSStack(self, line, frame_chain):
        stack = []
        while True:
            self.idx += 1
            next_line = self.content[self.idx]
            if self._feature_frame_chain in next_line:
                self.idx -= 1
                break

            if next_line == '\n':
                break

            stack.append(next_line.strip('\n').strip('\t').strip(' '))

        frame_chain.recordJSStack(stack)

    def handleFeatureFrameChain(self, line, frame_chain):

        chain = ""

        if self.is_debug:
            print("begin....")

        # handle all frames in that series of frame chain
        while self.idx < self.length - 1:
            line = line[line.index(self._feature_frame_chain):]
            _, _, remain = line.partition("=")
            if remain == "":
                raise Exception("Bad format for frame chain: " + line)

            info = remain.split(',')
            chain_len = int(info[0].strip(' '))

            # here is the next series of frame chain, so we should complete the
            #  current one and decrease self.idx with 1
            if chain_len == 1 and not frame_chain.isEmpty():
                break

            chain = info[1].strip(' ')

            # here we begin to update the current series of frame chain

            # 1. collect the metadata and JS stack
            while self.idx < self.length - 1:
                self.idx += 1
                line = self.content[self.idx]

                # here we are in the next frame in current series frame chain
                if self._feature_frame_chain in line:
                    break

                # get the metadata and JS stack for that frame
                if self._feature_metadata in line:
                    self.handleFeatureMetadata(line, frame_chain)
                elif self._feature_js_stack in line:
                    self.handleFeatureJSStack(line, frame_chain)

        # here is |the end of the log| or |the end of the current series of frame chain|
        self.completeCurrentFrameChain(chain, frame_chain)
        if self.is_debug:
            print(chain, self.content[self.idx])
        self.idx -= 1

    def handle(self):
        print(">>> HANDLE %s" % self.file_name)
        f = open(self.file_name, "r", encoding="ISO-8859-1")

        self.content = f.readlines()
        self.idx, self.length = -1, len(self.content)
        while self.idx < self.length - 1:
            self.idx += 1
            line = self.content[self.idx].strip("\n")

            # here is a frame chain
            if self._feature_frame_chain in line:

                # extract the series of frame chain in that line
                chain = FrameChain()
                self.handleFeatureFrameChain(line, chain)

                if chain.isEmpty():
                    continue

                # update the max size of frame chain
                if chain.length() > self.max_len_of_frame_chain:
                    self.max_len_of_frame_chain = chain.length()
                # for frame chain whose size is 1, we ignore it
                if chain.length() < 2:
                    continue
                # record frame chain whose size >= 2
                frames = chain.getFramesInfo()
                self.vuln_frames.append(frames)

                if self.is_debug:
                    print(frames)

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
                            self.larger_cross_origin_frame_chain = chain.getChain()
                        break

        f.close()


def test(domain="yahoo.com"):
    from result_handler import _result_dir

    ret_dir = os.path.join(_result_dir, domain)
    if os.path.exists(ret_dir) and os.path.isdir(ret_dir):
        files = os.listdir(ret_dir)
        for ret_file in files:
            parser = ParseLog(os.path.join(ret_dir, ret_file), is_debug=True)
            print(parser.getMaxLengthOfFrameChain(), parser.getMaxLengthOfCrossOriginFrameChain())
            print(parser.getLargerCrossOriginFrameChain())
            print(parser.getVulnCorssOriginFrames())
            print(parser.getVulnFrames())
