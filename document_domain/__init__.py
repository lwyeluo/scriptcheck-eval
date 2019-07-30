# coding=utf-8

import os

_dir = os.path.dirname(__file__)
_urls_dir = os.path.join(_dir, "urls")

_url_list_dir = os.path.join(os.path.dirname(_dir), "url_list")
_topsites_alexa_dir = os.path.join(_url_list_dir, "topsitesAlexa")
_target_subdomains_json_file = os.path.join(_topsites_alexa_dir, "suspectedSubDomains")