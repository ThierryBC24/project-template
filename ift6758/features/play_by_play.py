import json
from os import makedirs
from os.path import join, isfile, exists

import requests


class NHLData:
    def __init__(self):
        self.playoffs = {}
        self.regular_season = {} 

    def get_regular_saison(self, year: str):

        path_directory = f"data/regular_season/{year}"

        
        if not exists(path_directory):
            makedirs(path_directory)

        game = "0001"  
        games_list = []
        nb_data = 0  

        while True:

            local_file = join(path_directory, f"{year}_{game}.json")

            url = f"https://api-web.nhle.com/v1/gamecenter/{year}02{game}/play-by-play"

            if not isfile(local_file):

                response = requests.get(url)

                if response.status_code == 200:

                    data = response.json()

                    with open(local_file, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)  
                    print(f"Data was successfully imported: {local_file}")

                
                else:
                    break
            else:
                
                with open(local_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)

            nb_data += 1   
            games_list.append(data) 
            game = f"{int(game) + 1:04d}"  

        self.regular_season[year] = games_list

    def get_playoff(self, year: str):
        path_directory = f"data/playoffs/{year}"

        if not exists(path_directory):
            makedirs(path_directory)

        game = "0111" 
        games_list = []  
        nb_data = 0  

        while int(game[1]) < 5:

            local_file = join(path_directory, f"{year}_{game}.json")

            url = f"https://api-web.nhle.com/v1/gamecenter/{year}03{game}/play-by-play"

            if not isfile(local_file):

                response = requests.get(url)

                if response.status_code == 200:

                    data = response.json()

                    with open(local_file, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4) 
                        print(f"Data was successfully imported: {local_file}")

                else:
                    game = self.__generate_playoff_id(game) 
                    continue  

            with open(local_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                games_list.append(data) 
                nb_data += 1  

            game = f"{int(game) + 1:04d}"
        self.playoffs[year] = games_list

    def __generate_playoff_id(self, playoff_id: str) -> str:

        prefix = playoff_id[0]  
        round_digit = int(playoff_id[1])  
        matchup_digit = int(playoff_id[2])  

        game_digit = 1
        if (round_digit == 1 and matchup_digit < 8) or (round_digit == 2 and matchup_digit < 4) or (
                round_digit == 3 and matchup_digit < 2):
            matchup_digit += 1
        else:
            round_digit += 1
            matchup_digit = 1

        
        new_playoff_id = f"{prefix}{round_digit}{matchup_digit}{game_digit}"

        return new_playoff_id
