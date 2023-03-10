# noinspection PyPep8
# noinspection PyArgumentList

"""
AUTO-GENERATED BY `scripts/generate_protocol.py` using `data/browser_protocol.json`
and `data/js_protocol.json` as inputs! Please do not modify this file.
"""

import logging
from typing import Any, Optional, Union

from chromewhip.helpers import PayloadMixin, BaseEvent, ChromeTypeBase

log = logging.getLogger(__name__)

# GPUDevice: Describes a single graphics processor (GPU).
class GPUDevice(ChromeTypeBase):
    def __init__(self,
                 vendorId: Union['float'],
                 deviceId: Union['float'],
                 vendorString: Union['str'],
                 deviceString: Union['str'],
                 driverVendor: Union['str'],
                 driverVersion: Union['str'],
                 ):

        self.vendorId = vendorId
        self.deviceId = deviceId
        self.vendorString = vendorString
        self.deviceString = deviceString
        self.driverVendor = driverVendor
        self.driverVersion = driverVersion


# GPUInfo: Provides information about the GPU(s) on the system.
class GPUInfo(ChromeTypeBase):
    def __init__(self,
                 devices: Union['[GPUDevice]'],
                 driverBugWorkarounds: Union['[]'],
                 auxAttributes: Optional['dict'] = None,
                 featureStatus: Optional['dict'] = None,
                 ):

        self.devices = devices
        self.auxAttributes = auxAttributes
        self.featureStatus = featureStatus
        self.driverBugWorkarounds = driverBugWorkarounds


# ProcessInfo: Represents process info.
class ProcessInfo(ChromeTypeBase):
    def __init__(self,
                 type: Union['str'],
                 id: Union['int'],
                 cpuTime: Union['float'],
                 ):

        self.type = type
        self.id = id
        self.cpuTime = cpuTime


class SystemInfo(PayloadMixin):
    """ The SystemInfo domain defines methods and events for querying low-level system information.
    """
    @classmethod
    def getInfo(cls):
        """Returns information about the system.
        """
        return (
            cls.build_send_payload("getInfo", {
            }),
            cls.convert_payload({
                "gpu": {
                    "class": GPUInfo,
                    "optional": False
                },
                "modelName": {
                    "class": str,
                    "optional": False
                },
                "modelVersion": {
                    "class": str,
                    "optional": False
                },
                "commandLine": {
                    "class": str,
                    "optional": False
                },
            })
        )

    @classmethod
    def getProcessInfo(cls):
        """Returns information about all running processes.
        """
        return (
            cls.build_send_payload("getProcessInfo", {
            }),
            cls.convert_payload({
                "processInfo": {
                    "class": [ProcessInfo],
                    "optional": False
                },
            })
        )

