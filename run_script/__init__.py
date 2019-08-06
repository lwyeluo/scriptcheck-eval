# coding=utf-8

import os
import logging
from utils.executor import execute

_dir = os.path.abspath(os.path.dirname(__file__))
_result_handler_dir = os.path.join(os.path.dirname(_dir), "result_handler")
_result_log_dir = os.path.join(_result_handler_dir, "tim-results")
_result_log_dir_for_china = os.path.join(_result_handler_dir, "tim-results-china")
