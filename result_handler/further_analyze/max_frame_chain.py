# coding=utf-8

import os
from result_handler.vulnWebPage import VulnWebPage
from utils.regMatch import matchRawDomainFromURL, getSiteFromURL

'''
    Show the information for the frame chain with maximum length for each web page, including:
        1. Two frames are cross-origin.
        2. All frames are same-origin, but two frames' parents are cross-origin
        3. All frames are same-origin and their parents are same-origin
        4. The reason for two cross-origin frames
    If a frame is the top frame, then we consider its parent as itself.
'''


class Character:
    SAME_ORIGIN_AND_PARENT_SAME_ORIGIN = 1,
    SAME_ORIGIN_BUT_PARENT_CROSS_ORIGIN = 2,
    CROSS_ORIGIN = 3,

class MaximumFrameChain(object):
    '''
    parameters:
        @web_pages: a list, whose element is an instance of `result_handler.vulnWebPage.VulnWebPage`
        @logger:
    '''
    def __init__(self, web_pages, _logger):
        self._vuln_web_pages = web_pages
        for page in self._vuln_web_pages:
            if not isinstance(page, VulnWebPage):
                raise Exception("Bad parameter for _vuln_web_pages")
        self._logger = _logger

        self.dict_max_frame_chains = {}

    def collectMaximumFrameChain(self):
        for page in self._vuln_web_pages:
            if len(page.vuln_frame_chain) < 1:
                continue
            self.dict_max_frame_chains[page.file_name] = {}  # {chain: frames}
            for frame_chain in page.vuln_frame_chain:
                # the frame chains whose length is bigger than 1
                #  the format is `result_handler.frameChain.FrameChain.frames`
                if len(frame_chain['frames']) == page.len_for_vuln_frame_chain:
                    self.dict_max_frame_chains[page.file_name][frame_chain['chain']] = frame_chain['frames']
        return

    def collectCharacter(self, frame0, frame1):
        # Feature 1: they have different effective domains
        domain0, domain1 = frame0['domain'], frame1['domain']
        # if frame0 has set its domain, update domain0
        if 'set_domain' in frame0.keys():
            domain0 = frame0['set_domain']
        if domain0 != domain1:
            # the reason why they are cross-origin
            reason = "Unknown"
            if 'triggered_by_event' in frame1.keys():
                reason = frame1['triggered_by_event']
            elif 'triggered_by_event' in frame0.keys():
                reason = frame0['triggered_by_event']
            return Character.CROSS_ORIGIN, reason

        # Feature 2: they have different parent frames but not the parent-child relationship
        # parent_id0, parent_id1 = frame0['parent_id'], frame1['parent_id']
        # id0, id1 = frame0['id'], frame1['id']
        # if id0 == parent_id1 or id1 == parent_id0:
        #     # here means that one is the other's parent frame
        #     return Character.SAME_ORIGIN_AND_PARENT_SAME_ORIGIN

        parent_origin0, parent_origin1 = frame0['parent_origin'], frame1['parent_origin']
        parent_domain0, parent_domain1 = frame0['parent_domain'], frame1['parent_domain']

        if parent_origin0 == '' or parent_origin1 == '':
            # here one of them is the top frame
            domain = parent_domain0 + parent_domain1
            expected_domain = domain0  # domain0 is the same as domain1
            if domain != expected_domain:
                return Character.SAME_ORIGIN_BUT_PARENT_CROSS_ORIGIN, None
        else:
            if parent_domain0 != parent_domain1:
                return Character.SAME_ORIGIN_BUT_PARENT_CROSS_ORIGIN, None
        return Character.SAME_ORIGIN_AND_PARENT_SAME_ORIGIN, None

    def getCharactersForEachPage(self):
        dict_character = {}
        need_manually_check_frame_chain = []
        for file, value in self.dict_max_frame_chains.items():
            dict_character[file] = {
                'character': Character.SAME_ORIGIN_AND_PARENT_SAME_ORIGIN,
                'reason': None
            }
            for chain, frames in value.items():
                for i in range(0, len(frames) - 1):
                    # get the two consecutive frames
                    frame0, frame1 = frames[i], frames[i + 1]
                    character, reason = self.collectCharacter(frame0, frame1)
                    # update the character for that url
                    if dict_character[file]['character'] < character:
                        dict_character[file]['character'] = character
                    # we have found cross-origin, just break
                    if character == Character.CROSS_ORIGIN:
                        if reason == "Unknown":
                            # we need to manually check the reason
                            need_manually_check_frame_chain.append({
                                'filepath': file,
                                'chain': chain,
                                'frames': frames,
                                'frame0': str(frame0),
                                'frame1': str(frame1),
                            })
                        dict_character[file]['reason'] = reason
                        break
                # we have found cross-origin, just break
                if dict_character[file] == Character.CROSS_ORIGIN:
                    break
        return dict_character, need_manually_check_frame_chain


    def run(self):
        self.collectMaximumFrameChain()

        self._logger.info(">>> tested webpages: %d" % len(self._vuln_web_pages))
        self._logger.info(">>> webpages having frame chain's length bigger than 1: %d" % len(self.dict_max_frame_chains.keys()))

        dict_character, need_manually_check_frame_chain = self.getCharactersForEachPage()
        distribution_character = {
            Character.SAME_ORIGIN_AND_PARENT_SAME_ORIGIN: 0,
            Character.SAME_ORIGIN_BUT_PARENT_CROSS_ORIGIN: 0,
            Character.CROSS_ORIGIN: 0
        }
        for url, info in dict_character.items():
            distribution_character[info['character']] += 1
        self._logger.info(distribution_character)

        distribution_reason_for_cross_origin = {}
        for url, info in dict_character.items():
            if info['character'] != Character.CROSS_ORIGIN:
                continue
            reason = info['reason']
            if reason not in distribution_reason_for_cross_origin.keys():
                distribution_reason_for_cross_origin[reason] = 1
            else:
                distribution_reason_for_cross_origin[reason] += 1
        self._logger.info(distribution_reason_for_cross_origin)

        # the one need to be manually checked
        for frame in need_manually_check_frame_chain:
            self._logger.info(frame)

