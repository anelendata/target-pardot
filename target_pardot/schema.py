import collections, datetime
import simplejson as json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import singer

# StitchData compatible timestamp meta data
#  https://www.stitchdata.com/docs/data-structure/system-tables-and-columns
BATCH_TIMESTAMP = "_sdc_batched_at"

logger = singer.get_logger()


def _flatten(d, parent_key='', sep='__'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v) if type(v) is list else v))
    return dict(items)


def clean_and_validate(message, schemas, invalids, on_invalid_record,
                       flatten_record=False, json_dumps=False):
    batch_tstamp = datetime.datetime.utcnow()
    batch_tstamp = batch_tstamp.replace(
        tzinfo=datetime.timezone.utc)

    if message.stream not in schemas:
        raise Exception(("A record for stream {} was encountered" +
                         "before a corresponding schema").format(
                             message.stream))

    schema = schemas[message.stream]

    try:
        validate(message.record, schema)
    except ValidationError as e:
        cur_validation = False
        error_message = str(e)

        # It's a big hacy and fragile here...
        instance = re.sub(r".*instance\[\'(.*)\'\].*", r"\1",
                          error_message.split("\n")[5])
        type_ = re.sub(r".*\{\'type\'\: \[\'.*\', \'(.*)\'\]\}.*",
                       r"\1", error_message.split("\n")[3])

        # Save number-convertible strings...
        if type_ in ["integer", "number"]:
            n = None
            try:
                n = float(message.record[instance])
            except Exception:
                # In case we want to persist the rows with partially
                # invalid value
                message.record[instance] = None
                pass
            if n is not None:
                cur_validation = True

        # TODO:
        # Convert to BigQuery timestamp type (iso 8601)
        # if type_ == "string" and format_ == "date-time":
        #     n = None
        #     try:
        #         n = float(message.record[instance])
        #         d = datetime.datetime.fromtimestamp(n)
        #         d = d.replace(tzinfo=datetime.timezone.utc)
        #         message.record[instance] = d.isoformat()
        #     except Exception:
        #         # In case we want to persist the rows with partially
        #         # invalid value
        #         message.record[instance] = None
        #         pass
        #     if d is not None:
        #         cur_validation = True

        if cur_validation is False:
            invalids = invalids + 1
            if invalids < MAX_WARNING:
                logger.warn(("Validation error in record %d [%s]" +
                             " :: %s :: %s :: %s") %
                            (count, instance, type_, str(message.record),
                             str(e)))
            elif invalids == MAX_WARNING:
                logger.warn("Max validation warning reached.")

            if on_invalid_record == "abort":
                raise ValidationError("Validation required and failed.")

    if (BATCH_TIMESTAMP in schema.keys() or
            schema.get("properties") is dict and
            BATCH_TIMESTAMP in schema["properties"].keys()):
        message.record[BATCH_TIMESTAMP] = batch_tstamp.isoformat()

    record = message.record

    if flatten_record:
        record = _flatten(record)

    if json_dumps:
        try:
            record = bytes(json.dumps(record) + "\n", "UTF-8")
        except TypeError as e:
            logger.warning(record)
            raise

    return record, invalids
