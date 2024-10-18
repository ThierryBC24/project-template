import os
import json
import pandas as pd

def load_json_file(file_path):
    """
    Charge un fichier JSON et retourne son contenu sous forme de dictionnaire ou liste.
    :param file_path: Chemin vers le fichier JSON.
    :return: Contenu du fichier JSON.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def display_json_columns_and_types(file_path):
    """
    Affiche les colonnes et leurs types d'un fichier JSON.
    :param file_path: Chemin vers le fichier JSON.
    """
    data = load_json_file(file_path)

    # Convertir en DataFrame si c'est une liste de dictionnaires
    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, dict):
        # Si le JSON est un dictionnaire, essayons de le transformer en DataFrame
        df = pd.json_normalize(data)
    else:
        print("Le contenu JSON n'est ni une liste ni un dictionnaire.")
        return

    # Afficher les colonnes et leurs types
    print("Colonnes et leurs types :")
    print(df.dtypes)

if __name__ == "__main__":
    # Chemin vers un fichier JSON spécifique
    json_file_path = "/home/mohamed/project-template/play_by_play_data/2016_play_by_play.json"

    # Vérifier si le fichier existe
    if os.path.exists(json_file_path):
        display_json_columns_and_types(json_file_path)
    else:
        print(f"Le fichier {json_file_path} n'existe pas.")
