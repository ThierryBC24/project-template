import pandas as pd
import requests
import os

class PlayByPlayData:
    def __init__(self, base_path: str):
        """
        Initialize the instance with a base path to save the data.

        :param base_path: Path to the repository where the files will be saved
        """
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def get_data(self, season: int) -> pd.DataFrame:
        """
        Fetch data for a specific season, either from a local save or from the NHL's API.

        :param season: Season (ex: 2022 for the 2022-2023 season)
        :return: DataFrame
        """
        file_path = os.path.join(self.base_path, f"{season}_play_by_play.csv")

        # If a local file exists, load the data from the file
        if os.path.exists(file_path):
            print(f"Loading local data for the season {season}-{season+1}...")
            return pd.read_csv(file_path)

        # Else, download data from the API
        print(f"Downloading data for the season {season}-{season+1}...")
        data = self.fetch_season_data(season)

        # Save data into a CSV file
        data.to_csv(file_path, index=False)
        return data

    def fetch_season_data(self, season: int) -> pd.DataFrame:
        """
        Fetch the play-by-play data of a season from the NHL's API

        :param season: Season (ex: 2022 for the 2022-2023 season)
        :return: DataFrame
        """
        # Only fetch regular season and playoffs
        game_types = ['02', '03']
        data = []

        for game_type in game_types:
            game_number = 1 
            while True:
                # Format the game number as a 4-digit string
                game_number_str = f'{game_number:04d}'
                url = f'https://api-web.nhle.com/v1/gamecenter/{season}{game_type}{game_number_str}/play-by-play'
                response = requests.get(url)

                # Break the loop if the response is a 404 error (no more games)
                if response.status_code == 404:
                    break

                # Append the JSON response data if successful
                elif response.status_code == 200:
                    data.append(response.json())


                game_number += 1

        # Convert data to DataFrame and return
        return pd.DataFrame(data)

    def get_all_data(self) -> pd.DataFrame:
        """
        Fetch all collected data into the local save.

        :return: DataFrame with all data
        """
        all_data = []
        for file in os.listdir(self.base_path):
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(self.base_path, file))
                all_data.append(df)
        return pd.concat(all_data, ignore_index=True)

    def __add__(self, other):
        """
        Overload the add operator to combine data from two PlayByPlayData instances.

        :param other: Other PlayByPlayData instance
        :return: Combined DataFrame
        """
        if isinstance(other, PlayByPlayData):
            combined_data = pd.concat([self.get_all_data(), other.get_all_data()], ignore_index=True)
            return combined_data
        raise ValueError("Object's type need to be PlayByPlayData.")
