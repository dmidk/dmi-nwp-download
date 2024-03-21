import logging
import sys

from . import config
from .args import Arguments
from .download import Download


def main():
    """
    Main entrypoint for dmi_nwp_download.
    """

    modargs = Arguments()
    args = modargs.get_args(sys.argv)

    log = logging.getLogger("dmi-nwp-download")

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log.info("Starting dmi_nwp_download job")

    if args.log_level == "DEBUG":
        logging.debug("---- Input Arguments ----")
        for name, value in vars(args).items():
            log.debug(f"{name}: {value}")
        logging.debug("---- --------------- ----")

    # Load the configuration file
    configuration = config.load_config(args.config)
    config.check_config(configuration, args)

    if args.cmd == "download":
        log.info("Running download")

        download_run = Download(args, configuration)
        files = download_run.run()

        if configuration["download"]["filter_parameters"]:
            log.info("Filtering parameters")


if __name__ == "__main__":
    main()
