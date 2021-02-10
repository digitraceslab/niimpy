
Input data formats

Raw data level
 * read from files
   * csv files with given format
   * sqlite databases
 * required fields: unix time, ...
 * data grouped to studies, disorders, control, ...
 * data specific required fields: screen status, ...
 * functions to add extra columns: day of the week (from unix time), ...

Feature extraction
 * Calculate things from person data
 * group by

# User stories

## PhD student with messy data

Emilianna is a PhD student has a mess of data from an advisor. The data has been
collected over 1.5 years from two groups of people. Patient group has 20 people.
Healthy control group has 35 people.

The data is in the same format between the groups but the amount of missing data
between the groups is different. For each person there data collected with
various devices over a period of 2 weeks from smart phones, smart watches and
web questionnaires.

Emilianna's advisor wants her to build a classifier to see if the data can be used
to classify the people based on this data. She can use any combination of any
of the data.

Emilianna uses Niimpy to load in the data. First she installs niimpy using
`pip install niimpy`. She checks the data format from Niimpy's user guide and
formats the data so that niimpy can read it.

... Exact data format ...

Niimpy runs an automatic quality
check, with quality thresholds she has defined. Niimpy gives her hints about
what kinds quality checks she should use and what the thresholds should be.

... exact commands to get quality analysis ...
... exact commands to filter data by quality thresholds ...

She now has a set of users in each group that fulfill the quality conditions.

## Making a classier with cleaned data
