# coding = utf-8

import re


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

    def removeTail(self):
        return self.frames.pop()

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
