# target-pardot

This is a [Singer](https://singer.io) target that reads JSON-formatted data
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#singer-specification).

## Install

```
pip install pip --upgrade
pip install -U target-pardot
```

Note: Make sure to upgrade pip first as this `target-pardot` has a dependency
to an enhancement to PyPardot4 that is not released to PyPi yet.
(See https://stackoverflow.com/a/56635563)

## Configuration file

See [sample_config.json](https://github.com/anelendata/target-pardot/blob/master/sample_config.json)
for the sample configuration file.

## Updating checkbox field

There is a slight difference in the Pardot API implementations when we want to
make use of synchronous update (i.e. streaming=True) and batch update.

When we want to synchronously update a checkbox field called "Some Field",
the mapper's `target_key` must be set as "Some_Field_0" just like explained
in the
[API doc](https://developer.pardot.com/kb/api-version-3/prospects/#updating-fields-with-multiple-values)

But when we use batch update, the field name must be "Some_Field".

---

Copyright &copy; 2020- Anelen Co, LLC
