import json
import os
from os.path import join, isfile
import requests


class NHLData:
    def __init__(self):
        """
        Initialize NHLData with dictionaries to store data.
        """
        self.playoffs = {}
        self.regular_season = {}

    def fetch_regular_season(self, year: int):
        """
        Fetch data for the regular season of a given year.
        :param year: Year of the season.
        """
        path_directory = f"data/regular_season/{year}"
        os.makedirs(path_directory, exist_ok=True)

        game_number = "0001"
        games_list = []
        while True:
            local_file = join(path_directory, f"{year}_{game_number}.json")
            url = f"https://api-web.nhle.com/v1/gamecenter/{year}02{game_number}/play-by-play"

            if not isfile(local_file):
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    with open(local_file, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                    print(f"Data saved: {local_file}")
                else:
                    break
            else:
                with open(local_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)

            games_list.append(data)
            game_number = f"{int(game_number) + 1:04d}"

        self.regular_season[year] = games_list

    def fetch_playoffs(self, year: int):
        """
        Fetch data for the playoffs of a given year.
        :param year: Year of the playoffs.
        """
        path_directory = f"data/playoffs/{year}"
        os.makedirs(path_directory, exist_ok=True)

        game_number = "0111"
        games_list = []
        while int(game_number[1]) < 5:
            local_file = join(path_directory, f"{year}_{game_number}.json")
            url = f"https://api-web.nhle.com/v1/gamecenter/{year}03{game_number}/play-by-play"

            if not isfile(local_file):
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    with open(local_file, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                    print(f"Data saved: {local_file}")
                else:
                    game_number = self.__generate_playoff_id(game_number)
                    continue
            else:
                with open(local_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)

            games_list.append(data)
            game_number = f"{int(game_number) + 1:04d}"

        self.playoffs[year] = games_list

    def __generate_playoff_id(self, playoff_id: str) -> str:
        """
        Generate the next playoff game ID.
        :param playoff_id: Current playoff ID.
        :return: Next playoff ID.
        """
        round_digit = int(playoff_id[1])
        matchup_digit = int(playoff_id[2])

        if (round_digit == 1 and matchup_digit < 8) or \
           (round_digit == 2 and matchup_digit < 4) or \
           (round_digit == 3 and matchup_digit < 2):
            matchup_digit += 1
        else:
            round_digit += 1
            matchup_digit = 1

        return f"0{round_digit}{matchup_digit}1"
