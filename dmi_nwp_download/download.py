#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Master module for dmi_nwp_download.download
Called from dmi_nwp_download.__main__
"""
import argparse
import concurrent.futures
import logging
import os
import sys

import requests
from tqdm import tqdm

log = logging.getLogger("dmi-nwp-download")


class Download:
    """Class for Download"""

    def __init__(self, args: argparse.Namespace, config:dict) -> None:
        """Constructor for Download class"""

        self.cycle = args.cycle
        self.model = args.model
        self.limit_files = int(args.limit_files)

        self.stac_url = f"{config["download"]["stac_url"]}/{args.model}/items"


    def run(self) -> list:
        """Run the download"""

        log.info("Running download")

        api_key = os.environ.get('DMI_API_FORECAST_KEY', None)
        if api_key is None:
            log.error("DMI_API_FORECAST_KEY not set in environment. export DMI_API_FORECAST_KEY=<your-key>")
            sys.exit(1)

        model_run = f"{self.cycle.isoformat()}Z"

        method = "get"
        url = f"{self.stac_url}?modelRun={model_run}&api-key={api_key}"

        headers = { 'Accept': 'application/json'}
        response = requests.request(method, url, headers=headers, auth=None)

        if response.status_code != 200:
            log.error(f"Failed to download data for cycle {self.cycle}")
            return

        rsp = response.json()

        if rsp["numberReturned"] == 0:
            log.error(f"No data found for cycle {self.cycle}")
            return

        files_to_download = []
        for count, ele in enumerate(rsp["features"]):
            files_to_download.append((count, ele['asset']['data']['href']))

        if self.limit_files:
            files_to_download = files_to_download[0:self.limit_files]

        local_files = self.download_files_concurrently(files_to_download)

        return local_files

    def get_filename_from_url(self, url):
        """Extract the filename from the URL."""
        return os.path.basename(url).split("?")[0]

    def download_file(self, url: str, filename: str):
        """Download a file from a given URL and save it to a local file."""

        # Check if file already exists
        if os.path.exists(filename):
            log.info(f"File {filename} already exists. Skipping download.")
            return filename

        response = requests.get(url, stream=True)

        if response.status_code == 200:
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024 # 1 Kilobyte
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=filename)

            with open(filename, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                log.error("ERROR, something went wrong in the download process")

            return filename
        else:
            log.error(f"Failed to download file: {url}")
            return None


    def download_files_concurrently(self, files_to_download):
        """Download multiple files concurrently."""
        # Limit the number of concurrent downloads to 4

        local_files = [self.get_filename_from_url(url) for i, url in files_to_download if url is not None]

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_url = {executor.submit(self.download_file, url, local_files[i]): url for i, url in files_to_download}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    log.info(f"Downloaded: {data}")
                except Exception as exc:
                    log.error(f"{url} generated an exception: {exc}")

        return local_files
