"""
Handle configuration file for dmi_nwp_download.
"""
from pathlib import Path
import sys
import logging
import yaml


def load_config(config_file: Path) -> dict:
    """
    Load the configuration file.

    input:
        config_file: Path to the configuration file
    output:
        config: Configuration file as a dictionary
    """

    with open(config_file, encoding='utf-8') as configfile:
        config = yaml.safe_load(configfile)

    return config

def check_config(config, args: dict) -> None:
    """Check if the configuration file is valid.

    Parameters
    ----------
    data_source : str
        Name of the data source

    Returns
    -------
    bool
        True if the data source exists, False otherwise
    """

    if args.cmd == "download":

        download_patterns = config["download"].keys()

        stac_url = "stac_url"
        filter_parameters = "filter_parameters"


        if not stac_url in download_patterns:
            logging.error(
                f"Download pattern {download_patterns} does not exist in configuration - aborting"
            )
            sys.exit(1)
        else:
            if not isinstance(config["download"][stac_url], str):
                logging.error(
                    f"{stac_url} in configuration must be a string - aborting"
                )
                sys.exit(1)


        if not filter_parameters in download_patterns:
            logging.error(
                f"Download pattern {download_patterns} does not exist in configuration - aborting"
            )
            sys.exit(1)
        else:
            if not isinstance(config["download"][filter_parameters], bool):
                logging.error(
                    f"{filter_parameters} in configuration must be a boolean - aborting"
                )
                sys.exit(1)


        if config["download"][filter_parameters]:
            logging.debug("Filter parameters enabled - checking for filter parameters")

            # check that the section looks like this:
            # parameters:
            #     t2m:
            #         shortName: ["t2"]
            #         level: ["2"]
            #         levelType: ["heightAboveGround"]
            #         typeOfStatisticalProcessing: ["0"]
            #     u10m:
            #         shortName: ["u10"]
            #         level: ["10"]
            #         levelType: ["heightAboveGround"]
            #         typeOfStatisticalProcessing: ["0"]

            if not "parameters" in config["download"]:
                logging.error(
                    f"Filter parameters enabled but no parameters section in configuration - aborting"
                )
                sys.exit(1)
            else:
                for parameter in config["download"]["parameters"]:
                    if not "shortName" in config["download"]["parameters"][parameter]:
                        logging.error(
                            f"Filter parameters enabled but no shortName for {parameter} in configuration - aborting"
                        )
                        sys.exit(1)
                    if not "level" in config["download"]["parameters"][parameter]:
                        logging.error(
                            f"Filter parameters enabled but no level for {parameter} in configuration - aborting"
                        )
                        sys.exit(1)
                    if not "levelType" in config["download"]["parameters"][parameter]:
                        logging.error(
                            f"Filter parameters enabled but no levelType for {parameter} in configuration - aborting"
                        )
                        sys.exit(1)
                    if not "typeOfStatisticalProcessing" in config["download"]["parameters"][parameter]:
                        logging.error(
                            f"Filter parameters enabled but no typeOfStatisticalProcessing for {parameter} in configuration - aborting"
                        )
                        sys.exit(1)

        logging.debug("Config check passed")
