Data schema
===========

This page documents the expected data schema of Niimpy.  This does
*not* extend to the contents of data from sensors (yet), but relates
to the metadata applicable to all sensors.

By using a standardized schema (mainly column names), we can promote
interoperability of various tools.



Format
------

Data is in a tabular (relational) format.  A row is an observation,
and columns are properties of observations.  (At this level of
abstraction, an "observation" may be one sensor observation, or some
data which contains a package of multiple observations).

In Niimpy, this is internally stored and handled as a
pandas.DataFrame.  The schema naturally maps to the columns/rows of
the DataFrames.

The on-disk format is currently irrelevant, as long as the producers
can create a DataFrame of the necessary format.  Currently, we provide
readers for sqlite3 and csv.  Other standards may be implemented later.



Standard columns in DataFrames
------------------------------

By having standard columns, we can create portable functions that
easily operate on diverse data types.

* The **DataFrame index** should be a ``pandas.DatetimeIndex``.

* ``user``: opaque identifier for the user.  Often a string or
  integer.

* ``device``: unique identifier for a user's device (not the
  device type).  For example, a user could have multiple phones, and
  each would have a separate ``device`` identifier.

* ``time``: timestamp of the observation, in unixtime (seconds
  since 00:00 on 1970-01-01), stored as an integer.  Unixtime is a
  globally unique measure
  of an instance of time on Earth, and to get localtime it is combined
  with a timezone.

  In on-disk formats, ``time`` is considered the master timestamp,
  many other time-based properties are computed from it (though you
  could produce your own DataFrames other ways).  In some of the
  standard formats (CSV/sqlite3), when a file is read, this integer
  column is automatically converted to the ``datetime`` column below
  and the DataFrame index.

* ``datetime``: a ``DateTime``-compatible object, such as in pandas a
  numpy.datetime64 object, used only in in-memory representations (not
  usually written to portable save files).  This should be an
  timezone-aware object, and the data loader handles the timezone
  conversion.  automatically added to DataFrames when loaded.

  It is the responsibility of each loader (or preprocessor) to add
  this column to the in-memory representation by converting the
  ``time`` column to this format.  This happens automatically with
  readers included in ``niimpy``.

* ``timezone``: Timezone in some format.  Not yet used, to be
  decided.

* For questionaire data

  * ``id``: a question identifier.  String, should be of form
    ``QUESTIONAIRE_QUESTION``, for example ``PHQ9_01``.  The common
    prefix is used to group questions of the same series.
  * ``answer``: the answer to the question.  Opaque identifier.

Sensor-specific schemas are defined elsewhere.  Columns which are not
defined here are allowed and considered to be part of the sensors,
most APIs should pass through unknown columns for handling in a future
layer (sensor analysis).



Other standard columns in Niimpy
--------------------------------

These are not part of the primary schema, but are standard in Niimpy.

* ``day``: e.g. ``2021-04-09`` (str)
* ``hour``: hour of day, e.g. ``15`` (int)



Standard columns in on-disk formats
-----------------------------------

For the most part, this maps directly to the columns you see above.
An on-disk format should have a ``time`` column (unixtime, integer)
plus whatever else is needed for that particular sensor, based on the
above.



