# coding=utf-8

import os
from url_crawler import _topsites_alexa_dir

urls = os.path.join(_topsites_alexa_dir, "urls")
for i, domain in enumerate(os.listdir(urls)):
	if domain == "chewen.com":
		print("%d %s" % (i, domain))
	if 1879 <= i <= 2000:
		print("%d %s" % (i, domain))