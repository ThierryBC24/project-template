from ift6758.features.play_by_play import NHLData


def data_extract(first_year: int, last_year: int) -> NHLData:
    raw_data = NHLData()  # Initialize the data object

    # Loop over all years
    for year in range(first_year, last_year + 1):
        # Generate the data from API or local if available
        raw_data.get_regular_saison(year)
        raw_data.get_playoff(year)
        print(f"Successfully imported NHL data for the {year} season.")

    return raw_data
