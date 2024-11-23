import os
import numpy as np
from NHLData import NHLData
from data_cleaning import clean_data, convert_dictionaries_to_dataframes

filename = './data/dataframe_2020_to_2021.csv'
start_year = 2020
end_year = 2021


def get_data_from(first_year: int, last_year: int) -> NHLData:
    """
    Fetch NHL data for the specified range of years (both regular season and playoffs).
    :param first_year: First year (inclusive).
    :param last_year: Last year (inclusive).
    :return: NHLData object containing the fetched data.
    """
    nhl_data = NHLData()
    for year in range(first_year, last_year + 1):
        nhl_data.fetch_regular_season(year)
        nhl_data.fetch_playoffs(year)
        print(f"Successfully imported NHL data for the {year} season.")
    return nhl_data


if not os.path.isfile(filename):
    # Get the data from the NHL API (2016 - 2019)
    nhl_data_provider = get_data_from(start_year, end_year)

    # Clean the data
    clean_regular_season, clean_playoff = clean_data(nhl_data_provider)

    # Transform data into a dataframe
    df_2016_to_2019 = convert_dictionaries_to_dataframes(
        clean_regular_season,
        clean_playoff,
        np.arange(start_year, end_year + 1).tolist()
    )
    df_2016_to_2019.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
