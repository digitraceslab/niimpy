"""Read data from a CSV file

"""

import pandas as pd
import warnings

from niimpy.preprocessing import util


def read_csv(filename, read_csv_options={}, add_group=None,
             tz=None):
    """Read DataFrame from csv file

    This will read data from a csv file and then process the result with
    `niimpy.util.df_normalize`.


    Parameters
    ----------

    filename : str
        filename of csv file

    read_csv_options: dict
        Dictionary of options to pandas.read_csv, if this is necessary for custom
        csv files.

    add_group : object
        If given, add a 'group' column with all values set to this.

    """
    if tz is None:
        warnings.warn(DeprecationWarning("From now on, you should explicitely specify timezone with e.g. tz='Europe/Helsinki'"), stacklevel=2)

    df = pd.read_csv(filename, **read_csv_options)

    # df_normalize converts sets the index to time values and does other time
    # conversions.  Inplace.
    util.df_normalize(df, tz=tz)
    df = util.read_preprocess(df, add_group=add_group)
    return df


def read_csv_string(string, tz=None):
    """Parse a string containing CSV and return dataframe

    This should not be used for serious reading of CSV from disk, but
    can be useful for tests and examples.  Various CSV reading options
    are turned on in order to be better for examples:

    - Allow comments in the CSV file

    - Remove the `datetime` column (redundant with `index` but some
      older functions break without it, so default readers need to leave
      it).

    Parameters
    ----------
    string : string containing CSV file


    Returns
    -------
    df: pandas.DataFrame
    """
    if tz is None:
        warnings.warn(DeprecationWarning("From now on, you should explicitely specify timezone with e.g. tz='Europe/Helsinki'"), stacklevel=2)
    import io
    df = read_csv(io.StringIO(string),
                  tz=tz,
                  read_csv_options={
                      'comment': '#',
                      },
                 )
    if 'datetime' in df.columns:
        del df['datetime']
    return df
