import json
import logging
import os
from dataclasses import asdict
from pathlib import Path

import click
from dicttoxml import dicttoxml

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
    final_version = dict()
    for b in blocks:
        if b:
            if not include_data_points and b.__class__.__name__ == "DataPoints":
                b.points = None
            final_version[b.__class__.__name__] = asdict(b)

    if output_format == "JSON":
        print(json.dumps(final_version, indent=2, default=str))
    if output_format == "XML":
        print(dicttoxml(final_version))


if __name__ == "__main__":
    main()
