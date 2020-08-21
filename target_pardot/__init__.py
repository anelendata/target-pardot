#!/usr/bin/env python3

import argparse
import io
import logging
import os
import sys
import simplejson as json
import urllib
from datetime import datetime
import collections

import pkg_resources
from jsonschema.validators import Draft4Validator
import singer

from . import utils
from . import sync_pardot as destination
from .schema import clean_and_validate


REQUIRED_CONFIG_KEYS = ["email", "password", "user_key", "email_field"]

logger = utils.get_logger(__name__, "debug")


def write_records(config, lines):
    state = None
    schemas = {}
    key_properties = {}
    headers = {}
    validators = {}
    on_invalid_record = config.get("on_invalid_record", "abort")

    dry_run = config.get("dry_run", False)
    if dry_run:
        logger.info("Dry-run mode")

    with open(config["mapper_file"], "r") as f:
        mapper = json.load(f)

    # Loop over lines from stdin
    record_count = 0
    write_count = 0
    invalids = 0

    errors = collections.defaultdict(int)

    for line in lines:
        try:
            message = singer.parse_message(line)
        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(line))
            raise

        if isinstance(message, singer.RecordMessage):
            record, invalids = clean_and_validate(
                message, schemas, invalids, on_invalid_record,
                flatten_record=True, json_dumps=False)

            # if len(invalids) > 0:
            #     pass

            try:
                destination.write(config, record, mapper, dryrun=dry_run)
            except Exception as e:
                prospect_email = record[config["email_field"]]
                logger.debug("Error in updating " + prospect_email + " : " +
                             str(e))
                errors[e.args[1]] += 1
                logger.debug(errors)
            else:
                write_count = write_count + 1

            record_count = record_count + 1

            if record_count % 100 == 0:
                logger.debug("Read %d records" % record_count)
                logger.debug("Wrote %d records" % write_count)

            state = None

        elif isinstance(message, singer.StateMessage):
            state = message.value
            # State may contain sensitive info. Not logging in production
            logger.debug("State: %s" % state)
            currently_syncing = state.get("currently_syncing")
            bookmarks = state.get("bookmarks")
            if currently_syncing and bookmarks:
                logger.info("State: currently_syncing %s - last_update: %s" %
                            (currently_syncing,
                             bookmarks.get(currently_syncing, dict()).get(
                                 "last_update")))

        elif isinstance(message, singer.SchemaMessage):
            stream = message.stream
            schemas[stream] = message.schema
            validators[stream] = Draft4Validator(message.schema)
            key_properties[stream] = message.key_properties

        elif isinstance(message, singer.ActivateVersionMessage):
            # This is experimental and won't be used yet
            pass

        else:
            raise Exception("Unknown message type {} in message {}"
                            .format(message.type, message))

    logger.info("Read %d records" % record_count)
    logger.info("Wrote %d records" % write_count)
    for key in errors.keys():
        logger.info("Unsuccessful cause - %s - %d records" % (key, errors[key]))

    return state


def _emit_state(state):
    if state is None:
        return
    line = json.dumps(state)
    logger.debug("Emitting state {}".format(line))
    sys.stdout.write("{}\n".format(line))
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="A JSON-format config file")

    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "--help"]:
        parser.print_help(sys.stderr)
        exit(1)

    args = parser.parse_args()

    if args.config:
        with open(args.config) as input_:
            config = json.load(input_)
    else:
        config = {}

    singer.utils.check_config(config, REQUIRED_CONFIG_KEYS)

    input_ = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    state = write_records(config, input_)

    _emit_state(state)


if __name__ == "__main__":
    main()
