import json
import logging
import os
from dataclasses import asdict
from pathlib import Path

import click

from otdr.file_parser import ParserFactory


@click.command()
@click.argument("sor_file", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument(
    "output_format", default="JSON", type=click.Choice(("JSON", "XML", "CBOR"))
)
@click.option("--timezone", default="UTC")
@click.option("--include-data-points", default=False, is_flag=True)
def main(sor_file: str, output_format: str, timezone: str, include_data_points: bool):
    logging.basicConfig(format="%(message)s")
    logger = logging.getLogger("pyOTDR")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    logger.setLevel(LOG_LEVEL)
    parser = ParserFactory.create_parser(Path(sor_file))
    blocks = parser.parse()
    for b in blocks:
        if b:
            print(json.dumps(asdict(b), indent=2))


if __name__ == "__main__":
    main()
