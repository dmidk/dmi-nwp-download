import sys
import logging

from .args import Arguments
from .download import Download

def main():
    """
    Main entrypoint for upscale.
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

    log.info("Starting upscale job")

    if args.log_level == "DEBUG":
        logging.debug("---- Input Arguments ----")
        for name, value in vars(args).items():
            log.debug(f"{name}: {value}")
        logging.debug("---- --------------- ----")

    if args.cmd == "download":
        log.info("Running download")

        download_run = Download(args)

        #download_run.run()

if __name__ == "__main__":
    main()