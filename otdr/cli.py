import json
import logging
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional
from enum import Enum
from otdr.block_data_structure import BaseEnum

import cbor2 as cbor
import click
from dicttoxml import dicttoxml

from otdr.file_parser import ParserFactory


@click.command()
@click.argument("sor_file", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument(
    "output_format", default="JSON", type=click.Choice(("JSON", "XML", "CBOR"))
)
@click.option("--timezone", default="UTC")
@click.option("-o", "--output", "output_file", default=None)
@click.option("--include-data-points", default=False, is_flag=True)
def main(
    sor_file: str,
    output_format: str,
    timezone: str,
    output_file: Optional[str],
    include_data_points: bool,
) -> None:
    logging.basicConfig(format="%(message)s", stream=sys.stderr)
    logger = logging.getLogger("pyOTDR")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(LOG_LEVEL)
    parser = ParserFactory.create_parser(Path(sor_file))
    blocks = parser.parse()
    final_version = dict()
    # convert all blocks to dict and enum to strings
    for block in blocks:
        if block:
            if not include_data_points and block.__class__.__name__ == "DataPoints":
                block.points = None
            final_version[block.__class__.__name__] = asdict(block)
    dump = ""
    if output_format == "JSON":
        dump = json.dumps(final_version, indent=2, default=str)
    if output_format == "XML":
        dump = dicttoxml(final_version)
    if output_format == "CBOR":
        dump = cbor.dumps(final_version)

    if output_file:
        with open(output_file, "w") as w:
            w.write(dump)
    else:
        click.echo(dump)
