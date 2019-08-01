import json

from pardot.client import APIClient
import singer

client = None
LOGGER = singer.get_logger()

def get_client(config=None):
    global client
    if client is None:
        if not config:
            raise KeyError("Need to set config")

        client = APIClient(config["email"],
                           config["password"],
                           config["user_key"])
    return client


def write(config, record, mapper, dryrun=True):
    client = get_client(config)
    kwargs = {}
    prospect_email = record[config["email_field"]]
    for key in mapper.keys():
        pardot_key = mapper[key]["target_key"]
        kwargs[pardot_key] = record[key]
    if dryrun is False:
        response = client.prospect.update(prospect_email, **kwargs)
        LOGGER.info(response)
