from pardot.client import APIClient

client = None


def get_client(config=None):
    global client
    if client is None:
        if not config:
            raise KeyError("Need to set config")

        client = APIClient(config["pardot_email"],
                           config["pardot_password"],
                           config["pardot_user_key"])
    return client


def write(config, record, mapper):
    client = get_client(config)
    kwargs = {}
    email = record[config["email_field"]]
    for key in mapper.keys():
        pardot_key = mapper[key]["target_key"]
        kwargs[pardot_key] = record[key]
    response = client.prospect.update(email, **kwargs)
