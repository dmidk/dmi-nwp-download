# dmi-nwp-download

A command line tool for downloading DMI NWP data from the DMI Open Data API. The tool will download GRIB files and concatenate them into a single file which contains all the messages for the requested cycle filtered in accordance with `config.yaml` under `dmi_nwp_download/config.yaml`. To keep more parameters, you can add them to the `config.yaml` file.

## Installation
Assuming pdm is installed on your system, you can install the package by running `pdm install` to install the package and its dependencies.


## examples

```shell
.venv/bin/nwp-download download --cycle 2024-08-26-00:00 --limit-files 4
```

This will attempt to use your DMI Open Data API key from the environment variable `DMI_API_FORECAST_KEY`. This key can be obtained from the DMI Open Data API website [here](dmiapi.govcloud.dk).
