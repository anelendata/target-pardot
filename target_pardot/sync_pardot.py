import logging, sys
import simplejson as json

from pardot.client import APIClient
from pardot.resource import PardotAPIException

import singer

from . import utils


CLIENT = None
LOGGER = utils.get_logger(__name__)


def get_client(config=None):
    global CLIENT
    if CLIENT is None:
        if not config:
            raise KeyError("Need to set config")

        CLIENT = APIClient(config["email"],
                           config["password"],
                           config["user_key"])
    return CLIENT


def write(config, record, mapper, dryrun=True):
    client = get_client(config)
    kwargs = {}
    prospect_email = record[config["email_field"]]
    for key in mapper.keys():
        pardot_key = mapper[key]["target_key"]
        kwargs[pardot_key] = record[key]
    if dryrun is False:
        response = client.prospect.update(prospect_email, **kwargs)
        prospect = response["prospect"]
        LOGGER.debug("Wrote {id} {email} https://pi.pardot.com/prospect/read?id={id}".format(**prospect))
