Architecture
============



Storage: server-side
--------------------

This is currently not a function of Niimpy, but on the server-side
data may be stored in some raw format, where each record contains
multiple observations as it has been uploaded.

Layer: conversion
-----------------

In this layer, raw data is converted to a one-row-per-observation
format, data is limited and processed for privacy, and other
preprocessing.  This is not a function of Niimpy.

Storage: downloaded
-------------------

Here, data is stored converted for analysis, for example in sqlite3
databases or csv files.

Layer: reading
--------------

Data is read from the on-disk formats.

Typical input consists of filenames on disk, and typical output is a
pandas.DataFrame with a direct mapping of on-disk formats.  For
converience, it may do various other small limiting and preprocessing,
but should not look inside the data too much.

Layer: preprocessing
--------------------

After reading the data for analysis, preprocessing can handle
filtering, etc. using the standard schema columns.  It does not look at or
understand actual sensor values, and the unknown sensor-specific
columns are passed straight through to a future layer.

Typical input arguments include the DataFrame, and output is the
DataFrame slightly adjusted, without affecting sensor-specific
columns.

These are mostly in ``niimpy.preprocessing``.

Layer: basic analysis
---------------------

These functions can do aggregation and other basic analysis which is
not specific to any sensor.

Layer: analysis
---------------

These functions understand the sensor values and perform analysis
based on them.

These are often in modules specific to the type of analysis.
