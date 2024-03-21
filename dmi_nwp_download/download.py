#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Master module for dmi_nwp_download.download
Called from dmi_nwp_download.__main__
"""

import datetime as dt
import argparse
import logging
import requests

log = logging.getLogger("dmi-nwp-download")

class Download:
    """Class for Download"""

    def __init__(self, args:argparse.Namespace) -> None:
        """Constructor for Download class"""

        self.cycle = args.cycle

        log.info(f"Cycle: {self.cycle}")


