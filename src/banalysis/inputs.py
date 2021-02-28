# -*- coding: utf-8 -*-
"""
    Module for reading the bank statement CSV files in the midata format.
"""

##### IMPORTS #####
# Standard imports
import logging
from pathlib import Path

# Third party imports
import pandas as pd

# Local imports
import banalysis.errors as ban_errors

##### CONSTANTS #####
LOG = logging.getLogger(__name__)

##### FUNCTIONS #####
def read_midata(path: Path) -> pd.DataFrame:
    """Read CSV in midata format.

    Checks all required columns are present in the CSV
    and will raise MidataCSVError if not.

    Parameters
    ----------
    path : Path
        Path to the CSV file, which should be in
        midata format containing the following
        columns: date, type, merchant/description,
        debit/credit and balance.

    Returns
    -------
    pd.DataFrame
        DataFrame with the following columns:
        date, type, description, amount and balance.

    Raises
    ------
    MidataCSVError
        If any required columns are missing.
    """
    df = pd.read_csv(path)
    df = _check_midata_columns(df)
    # Drop last row which contains overdraft data
    if df.iat[-1, 0].lower().startswith("arranged"):
        df.drop(df.index[-1], inplace=True)
    # Assume that all balance and amount values are in £ and convert to numbers
    for c in ("amount", "balance"):
        df[c] = pd.to_numeric(df[c].str.replace("£", ""), errors="raise")
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="raise").dt.date
    return df


def _check_midata_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Check and rename the columns in midata DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to check and rename, expected columns:
        "date", "type", "merchant/description", "debit/credit"
        and "balance".

    Returns
    -------
    pd.DataFrame
        DataFrame with columns renamed output columns are:
        "date", "type", "description", "amount" and "balance".

    Raises
    ------
    MidataCSVError
        If any expected columns aren't present.
    """
    df.columns = [c.strip().lower() for c in df.columns.tolist()]
    columns = ["date", "type", "merchant/description", "debit/credit", "balance"]
    missing = []
    for c in columns:
        if c not in df.columns.tolist():
            missing.append(c)
    if missing:
        # Create comma-separated list of columns and replace the last , with and
        msg = ", ".join(f"'{s}'" for s in missing)
        msg = " and".join(msg.rsplit(",", 1))
        print(msg)
        raise ban_errors.MidataCSVError(
            f"the following columns are missing from midata CSV: {msg}"
        )
    # Drop any columns that aren't needed
    df = df.loc[:, columns]
    rename = {"merchant/description": "description", "debit/credit": "amount"}
    return df.rename(columns=rename)
