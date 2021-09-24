"""Command-line interface."""

import os
import json
import csv
from io import StringIO

import click

from usgsm2m.api import API
from usgsm2m.usgsm2m import USGSM2M
from usgsm2m.errors import USGSM2MError

DATASETS = [
    "landsat_tm_c1",
    "landsat_etm_c1",
    "landsat_8_c1",
    "landsat_tm_c2_l1",
    "landsat_tm_c2_l2",
    "landsat_etm_c2_l1",
    "landsat_etm_c2_l2",
    "landsat_ot_c2_l1",
    "landsat_ot_c2_l2",
    "sentinel_2a",
]


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "-u",
    "--username",
    type=click.STRING,
    help="USGS M2M username.",
    envvar="USGSM2M_USERNAME",
)
@click.option(
    "-p",
    "--password",
    type=click.STRING,
    help="USGS M2M password.",
    envvar="USGSM2M_PASSWORD",
)
@click.option(
    "-d",
    "--dataset",
    type=click.Choice(DATASETS, case_sensitive=False),
    help="Dataset.",
    default="LANDSAT_8_C1",
)
@click.option(
    "-l",
    "--location",
    type=click.FLOAT,
    nargs=2,
    help="Point of interest (latitude, longitude).",
)
@click.option(
    "-b",
    "--bbox",
    type=click.FLOAT,
    nargs=4,
    help="Bounding box (xmin, ymin, xmax, ymax).",
)
@click.option("-c", "--clouds", type=click.INT, help="Max. cloud cover (1-100).")
@click.option("-s", "--start", type=click.STRING, help="Start date (YYYY-MM-DD).")
@click.option("-e", "--end", type=click.STRING, help="End date (YYYY-MM-DD).")
@click.option(
    "-o",
    "--output",
    type=click.Choice(["entity_id", "display_id", "json", "csv"]),
    default="display_id",
    help="Output format.",
)
@click.option("-m", "--limit", type=click.INT, help="Max. results returned.")
def search(
    username, password, dataset, location, bbox, clouds, start, end, output, limit
):
    """Search for scenes."""
    api = API(username, password)

    where = {"dataset": dataset}
    if location:
        latitude, longitude = location
        where.update(latitude=latitude, longitude=longitude)
    if bbox:
        where.update(bbox=bbox)
    if clouds:
        where.update(max_cloud_cover=clouds)
    if start:
        where.update(start_date=start)
    if end:
        where.update(end_date=end)
    if limit:
        where.update(max_results=limit)

    results = api.search(**where)
    api.logout()

    if not results:
        return

    if output == "entity_id":
        for scene in results:
            click.echo(scene["entity_id"])

    if output == "display_id":
        for scene in results:
            click.echo(scene["display_id"])

    if output == "json":
        dump = json.dumps(results, indent=True)
        click.echo(dump)

    if output == "csv":
        with StringIO("tmp.csv") as f:
            w = csv.DictWriter(f, results[0].keys())
            w.writeheader()
            w.writerows(results)
            click.echo(f.getvalue())


@click.command()
@click.option(
    "-u",
    "--username",
    type=click.STRING,
    help="USGS M2M username.",
    envvar="USGSM2M_USERNAME",
)
@click.option(
    "-p",
    "--password",
    type=click.STRING,
    help="USGS M2M password.",
    envvar="USGSM2M_PASSWORD",
)
@click.option("--dataset", "-d", type=click.STRING, required=False, help="Dataset")
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=True, dir_okay=True),
    default=".",
    help="Output directory.",
)
@click.option(
    "--filetype",
    "-f",
    required=False,
    type=click.STRING,
    default="bundle",
    help="Download File Type {'bundle','band'}",
)
@click.option(
    "--idfield",
    "-i",
    required=False,
    type=click.STRING,
    default="displayId",
    help="Entity Id Type {'displayId','entityId'}",
)
@click.option(
    "--timeout", "-t", type=click.INT, default=300, help="Download timeout in seconds."
)
@click.option("--skip", is_flag=True, default=False)
@click.argument("scenes", type=click.STRING, nargs=-1) ############################
def download(username, password, dataset, output, filetype, idfield,timeout, skip, scenes):
    """Download one or several scenes."""
    usgsm2m = USGSM2M(username, password)
    output_dir = os.path.abspath(output)
    if dataset and dataset.lower() not in DATASETS:
        raise USGSM2MError(f"`{dataset}` is not a supported dataset.")
#for scene in scenes:
    if not usgsm2m.logged_in():
        usgsm2m = USGSM2M(username, password)
    #print('cli.py:download ',list(scenes))
    fname = usgsm2m.download(
        scenes, output_dir,filetype=filetype, idField=idfield,dataset=dataset,timeout=timeout, skip=skip
    )

    if skip:
        click.echo(fname)
    usgsm2m.logout()
#######################################################################################

@click.command()
@click.option(
    "--username",
    "-u",
    type=click.STRING,
    help="USGS M2M username.",
    envvar="USGSM2M_USERNAME",
)
@click.option(
    "--password",
    "-p",
    type=click.STRING,
    help="USGS M2M password.",
    envvar="USGSM2M_PASSWORD",
)
@click.option("--dataset", "-d", type=click.STRING, required=False, help="Dataset")
@click.option(
    "--entityfile",
    "-e",
    required=True,
    type=click.Path(exists=True, file_okay=True),
    help="Entity File Name",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=True, dir_okay=True),
    default="./",
    help="Output directory.",
)
@click.option(
    "--filetype",
    "-f",
    required=False,
    type=click.STRING,
    default="bundle",
    help="Download File Type {'bundle','band'}",
)
@click.option(
    "--idfield",
    "-i",
    required=False,
    type=click.STRING,
    default="displayId",
    help="Entity Id Type {'displayId','entityId'}",
)
@click.option(
    "--timeout", "-t", type=click.INT, default=300, help="Download timeout in seconds."
)
@click.option("--skip", is_flag=True, default=False)
def downloadbulk(username, password, entityfile,dataset, output, filetype,idfield,timeout, skip ): #idField
    """Download one or several scenes."""
    usgsm2m = USGSM2M(username, password)
    output_dir = os.path.abspath(output)
    entityfile_path=os.path.abspath(entityfile)
    if dataset and dataset.lower() not in DATASETS:
        raise USGSM2MError(f"`{dataset}` is not a supported dataset.")
    if not usgsm2m.logged_in():
        usgsm2m = USGSM2M(username, password)
    fname = usgsm2m.downloadbulk(
        entityfile=entityfile_path, output_dir=output_dir, filetype=filetype,dataset=dataset, idField=idfield,timeout=timeout, skip=skip
    )
    if skip:
        click.echo(fname)
    usgsm2m.logout()


cli.add_command(search)
cli.add_command(download)
cli.add_command(downloadbulk)


if __name__ == "__main__":
    cli()
