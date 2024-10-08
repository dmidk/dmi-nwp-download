#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Master module for dmi_nwp_download.filter
Called from dmi_nwp_download.__main__
"""
import argparse
import logging
import shutil
import sys
import tempfile
import subprocess
import os

log = logging.getLogger("dmi-nwp-download")


class Filter:
    """Class for Filter"""

    def __init__(self, args: argparse.Namespace, config:dict, files:list) -> None:
        """Constructor for Filter class"""

        # Check if "grib_copy" is in $PATH
        if shutil.which("grib_filter") is None:
            log.error("grib_filter not found in $PATH")
            sys.exit(1)

        self.files = files
        self.parameters = config["download"]["parameters"]
        self.cycle = args.cycle
        self.model = args.model
        self.convert_to_ccsds = config["download"]["convert_to_ccsds"]

        self.temp_dir = tempfile.TemporaryDirectory()

        self.no_clean = args.no_clean


    def run(self) -> str:
        """Run the filter"""

        log.info("Running filter")

        temporary_files = []

        for file in self.files:
            temp_file = self.temp_dir.name + "/" + file
            temporary_files.append(temp_file)

            shortnames = [self.parameters[key]['shortName'] for key in self.parameters.keys()]
            shortnames = [item for sublist in shortnames for item in sublist]
            # Join the list elements with a comma
            shortnames_str = "/".join(shortnames)

            levels = [self.parameters[key]['level'] for key in self.parameters.keys()]
            levels = [item for sublist in levels for item in sublist]
            levels_str = "/".join(levels)

            leveltypes = [self.parameters[key]['levelType'] for key in self.parameters.keys()]
            leveltypes = [item for sublist in leveltypes for item in sublist]
            leveltypes_str = "/".join(leveltypes)

            statprocesses = [self.parameters[key]['typeOfStatisticalProcessing'] for key in self.parameters.keys()]
            statprocesses = [item for sublist in statprocesses for item in sublist]
            statprocesses_str = "/".join(statprocesses)

            typeoflevels = [self.parameters[key]['typeOfLevel'] for key in self.parameters.keys()]
            typeoflevels = [item for sublist in typeoflevels for item in sublist]
            typeoflevels_str = "/".join(typeoflevels)

            # Ensure the length of the lists are the same else exit
            if not len(shortnames) == len(levels) == len(leveltypes) == len(statprocesses):
                log.error("Length of shortName, level, levelType and typeOfStatisticalProcessing lists must be the same")
                sys.exit(1)

            rules_file_text = f""
            for k in range(len(shortnames)):
                if statprocesses[k] == "0":
                    rules_file_text += f'if ( shortName is "{shortnames[k]}" && level == {levels[k]} && levelType is "{leveltypes[k]}" && typeOfLevel is "{typeoflevels[k]}" ) {{\n write; \n}}\n'
                else:
                    rules_file_text += f'if ( shortName is "{shortnames[k]}" && level == {levels[k]} && levelType is "{leveltypes[k]}" && typeOfLevel is "{typeoflevels[k]}" &&typeOfStatisticalProcessing == {statprocesses[k]} ) {{\n write; \n}}\n'

            # TODO: Testing the downloaded files can be done here

            # Write the rules to a temporary file
            rules_file = self.get_temp_file_path("rules_file")
            with open(rules_file, "w") as f:
                f.write(rules_file_text)

            # Construct the command as a list
            cmd = ['grib_filter', '-o', temp_file, rules_file, file]

            # Running the command using subprocess
            log.debug(f"Running: {' '.join(cmd)}")
            try:
                # Capture the output and error
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                # Optional: Log the output
                log.info(result.stdout)
            except subprocess.CalledProcessError as e:
                log.error(f"Command '{e.cmd}' failed with return code {e.returncode}")
                log.error(e.stderr)


        # Concatenate the temporary files into a single file using grib_copy
        # Alternatively, you can use the "cat" command
        final_file = f"{self.model}_{self.cycle.isoformat()}.grib"

        cmd = ['grib_copy'] + temporary_files + [final_file]

        log.debug(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            log.info(result.stdout)
        except subprocess.CalledProcessError as e:
            log.error(f"Command '{e.cmd}' failed with return code {e.returncode}")
            log.error(e.stderr)


        if self.convert_to_ccsds:
            # Convert the final file to CCSDS compression
            cmd = ['grib_set', '-s', 'packingType=grid_ccsds', final_file, f"{final_file}.tmp"]

            log.debug(f"Running: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                log.info(result.stdout)
            except subprocess.CalledProcessError as e:
                log.error(f"Command '{e.cmd}' failed with return code {e.returncode}")
                log.error(e.stderr)

            # Move the temporary file to the final file
            os.rename(f"{final_file}.tmp", final_file)

        # Remove self.files
        if not self.no_clean:
            for file in self.files:
                os.remove(file)

        return final_file

    def get_temp_file_path(self, filename):
        """Get the path of the file in the temporary directory."""
        return os.path.join(self.temp_dir.name, filename)

    # Don't forget to clean up the temporary directory when done
    def __del__(self):
        self.temp_dir.cleanup()
