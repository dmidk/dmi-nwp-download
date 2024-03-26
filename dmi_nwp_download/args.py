#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Master module for dmi_nwp_download.args
Called from dmi_nwp_download.__main__
"""
import argparse
import datetime as dt
import sys
from pathlib import Path


class MyParser(argparse.ArgumentParser):
    """Parser for dmi_nwp_download arguments

    Parameters
    ----------
    argparse : argparse.ArgumentParser
        Parser for dmi_nwp_download arguments
    """

    def error(self, message):
        sys.stderr.write(f"error: {message}\n")
        self.print_help()
        sys.exit(2)


class Arguments:
    """Holds all the arguments for dmi_nwp_download"""

    def __init__(self) -> None:
        """Constructor for arguments class"""

    @staticmethod
    def check_args(args) -> None:
        """Check the arguments

        Parameters
        ----------
        args : argparse.Namespace
            Namespace with all the arguments

        Returns
        -------
        None
        """

        if args.cmd == "download":

            if not args.model in ["harmonie_dini_sf"]:
                raise ValueError("Model must be harmonie_dini_sf")

    def get_args(self, sysargs):
        """Get arguments from command line

        Parameters
        ----------
        sysargs : sys.argv
            Arguments given to dmi_nwp_download on command line

        Returns
        -------
        argparse.Namespace
            Namespace with all the arguments
        """

        parent_parser = MyParser(
            description="Run dmi_nwp_download",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        subparser = parent_parser.add_subparsers(dest="cmd")

        # Parser for download
        parser_download = subparser.add_parser(
            "download", help="Run dmi_nwp_download download"
        )

        parser_download.add_argument(
            "--log-level",
            "-l",
            dest="log_level",
            default="DEBUG",
            help="Log level",
        )
        parser_download.add_argument(
            "--cycle",
            "-c",
            dest="cycle",
            required=True,
            type=dt.datetime.fromisoformat,
            help="Cycle to download",
        )
        parser_download.add_argument(
            "--config",
            dest="config",
            default=Path("dmi_nwp_download/config.yaml"),
            type=Path,
            help="Path to the configuration file",
        )
        parser_download.add_argument(
            "--model",
            dest="model",
            default="harmonie_dini_sf",
            type=str,
            help="Model to download [harmonie_dini_sf]",
        )
        parser_download.add_argument(
            "--limit-files",
            dest="limit_files",
            default=None,
            help="Limit the number of files to download to the first n files. Default is None, which means all files",
        )
        parser_download.add_argument(
            "--no-clean",
            dest="no_clean",
            default=False,
            action="store_true",
            help="Do not clean up temporary files",
        )

        if len(sysargs) == 1:
            parent_parser.print_help()
            sys.exit(2)

        args = parent_parser.parse_args()

        self.check_args(args)

        return args
