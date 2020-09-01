import logging, sys
import simplejson as json

from pypardot.client import PardotAPI

import singer

from . import utils


CLIENT = None
LOGGER = utils.get_logger(__name__)


def get_client(config=None):
    global CLIENT
    if CLIENT is None:
        if not config:
            raise KeyError("Need to set config")

        CLIENT = PardotAPI(email=config["email"],
                           password=config["password"],
                           user_key=config["user_key"],
                           version=3)
        CLIENT.authenticate()
    return CLIENT


def write(config, record, mapper, dryrun=True):
    client = get_client(config)
    kwargs = {}
    prospect_email = record[config["email_field"]]
    for key in mapper.keys():
        pardot_key = mapper[key]["target_key"]
        kwargs[pardot_key] = record[key]
    if dryrun is False:
        response = client.prospects.update_by_email(prospect_email, **kwargs)
        prospect = response["prospect"]
        LOGGER.info(prospect)
        LOGGER.debug("Wrote {id} {email} https://pi.pardot.com/prospect/read?id={id}".format(**prospect))


def write_batch(config, file_name, mapper=None):
    client = get_client(config)
    columns = None
    if mapper:
        columns = list()
        column = {"field": "email"}
        columns.append(column)
        for key in mapper.keys():
            pardot_key = mapper[key]["target_key"]
            column = {"field": pardot_key,
                      "overwrite": mapper[key].get("overwrite", True),
                      "nullOverwrite": mapper[key].get("nullOverwrite", True)
                      }
            columns.append(column)
    results = client.importapi.create(
        file_name=file_name,
        operation="Upsert",
        object="Prospect",
        columns=columns,
        restoreDeleted=config.get("restore_deleted", False))
    batch_id = results["id"]
    results = client.importapi.update(id=batch_id, state="Ready")
