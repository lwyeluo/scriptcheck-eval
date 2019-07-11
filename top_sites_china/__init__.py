# coding=utf-8

import os

_dir = os.path.abspath(os.path.dirname(__file__))
_domain_filename = os.path.join(_dir, "topsites")
_webpages_dir = os.path.join(_dir, "result")
_split_dir = os.path.join(_dir, "domain-split")
_max_webpage_in_one_domain = 20