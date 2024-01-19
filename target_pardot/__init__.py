#!/usr/bin/env python3

import argparse
import csv
import io
import logging
import os
import sys
import simplejson as json
import urllib
import collections

from datetime import datetime
from tempfile import NamedTemporaryFile

import pkg_resources
from jsonschema.validators import Draft4Validator
import singer

from . import utils
from . import sync_pardot as destination
from .schema import clean_and_validate


REQUIRED_CONFIG_KEYS = ["consumer_key", "consumer_secret", "refresh_token",
                        "business_unit_id"]

logger = utils.get_logger(__name__, "debug")


def sync(config, lines):
    state = None
    schemas = {}
    key_properties = {}
    validators = {}
    on_invalid_record = config.get("on_invalid_record", "abort")

    streaming = config.get("streaming", False)
    delete_tempfile = config.get("delete_tempfile", True)
    dry_run = config.get("dry_run", False)
    logger.info("streaming %s. delete_tempfile %s. Dry-run mode %s" %
                (streaming, delete_tempfile, dry_run))

    with open(config["mapper_file"], "r") as f:
        mappers = json.load(f)

    record_count = collections.defaultdict(int)
    write_count = collections.defaultdict(int)
    invalids = collections.defaultdict(int)
    errors = collections.defaultdict(int)
    tempfiles = {}
    csv_writers = {}

    # Loop over lines from stdin
    for line in lines:
        try:
            message = singer.parse_message(line)
        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(line))
            raise

        if isinstance(message, singer.RecordMessage):
            stream = message.stream
            if stream not in mappers.keys():
                logger.info("Skipping the stream not present in the mapper: " +
                            stream)
                continue

            mapper = mappers[stream]
            record, invalids[stream] = clean_and_validate(
                message, schemas, invalids[stream], on_invalid_record,
                flatten_record=True, json_dumps=False)

            # if len(invalids[stream]) > 0:
            #     pass

            record_count[stream] = record_count[stream] + 1
            if streaming:
                try:
                    destination.write(config, record, mapper,
                                      dryrun=dry_run)
                except Exception as e:
                    prospect_email = record[config["email_field"]]
                    logger.debug("Error in updating " + prospect_email + " : " +
                                 str(e))
                    errors[e.args[1]] += 1
                    logger.debug(errors)
                else:
                    write_count[stream] = write_count[stream] + 1

            else:
                pardot_record = {"email": record[config["email_field"]]}
                for key in mapper.keys():
                    pardot_key = mapper[key]["target_key"]
                    value = record[key]
                    # Docs says:
                    # nullOverwrite: (Optional, default true) When set to true
                    # and updating an existing record, if the value in the input
                    # is an empty string or a string containing any number of
                    # whitespaces then the value in the database is set to empty
                    # string or null. When set to false the empty input value is
                    # ignored and the existing value in the database isn't
                    # updated. If the input row is a "Create" then this option
                    # is ignored and the empty string or null is present in
                    # the database.
                    # https://developer.salesforce.com/docs/marketing/pardot/guide/import-v4.html#create
                    # But an empty string does not update the value. It has
                    # to be whitespaces if I want to nullify the field.
                    if value is None or value == "None" or value == "":
                        value = " "
                    pardot_record[pardot_key] = value
                csv_writers[stream].writerow(pardot_record)
                write_count[stream] = write_count[stream] + 1

            if record_count[stream] % 100 == 0:
                logger.debug("Read %d records" % record_count[stream])
                logger.debug("Wrote %d records" % write_count[stream])

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
            if stream not in mappers.keys():
                continue

            mapper = mappers[stream]
            schemas[stream] = message.schema
            validators[stream] = Draft4Validator(message.schema)
            key_properties[stream] = message.key_properties

            if not streaming:
                tempfiles[stream] = NamedTemporaryFile(mode='w', delete=False)
                logger.info("temp file for %s: %s" %
                            (stream, tempfiles[stream].name))
                field_names = [v["target_key"] for v in mapper.values()]
                field_names = ["email"] + field_names
                csv_writers[stream] = csv.DictWriter(
                    tempfiles[stream], fieldnames=field_names)
                csv_writers[stream].writeheader()

        elif isinstance(message, singer.ActivateVersionMessage):
            # This is experimental and won't be used yet
            pass

        else:
            raise Exception("Unknown message type {} in message {}"
                            .format(message.type, message))

    # This is for streaming=False only
    for stream in tempfiles:
        tempfiles[stream].close()

        if not dry_run:
            destination.write_batch(config, file_name=tempfiles[stream].name,
                                    mapper=mappers[stream])
            logger.info("Uploaded the prospects from the tempfile for stream %s: %s" %
                         (stream, tempfiles[stream].name))

        if delete_tempfile:
            os.unlink(tempfiles[stream].name)
            logger.info("Deleted the tempfile for stream %s: %s" %
                         (stream, tempfiles[stream].name))

    for stream in schemas.keys():
        logger.info("Read %d records" % record_count[stream])
        logger.info("Wrote %d records" % write_count[stream])

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
    state = sync(config, input_)
    _emit_state(state)


if __name__ == "__main__":
    main()
