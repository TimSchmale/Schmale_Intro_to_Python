import os

import pandas as pd

class DataHandler:
    """
    Class which contains functions to load, combine and prepare the 40 football match data sets for a data analysis
    """

    def __init__(self):
        self.path = "data/top5"
        self.data = None

    def load_data(self):
        """
        Function which loads all 40 .csv (5 different leagues with 8 years) files into one data frame
        """
        all_matches = []

        # iterate over all leagues
        for league in os.listdir(self.path):
            league_path = os.path.join(self.path, league)

            if os.path.isdir(league_path):
                # iterate over all years
                for year in os.listdir(league_path):
                    year_path = os.path.join(league_path, year)

                    df = pd.read_csv(year_path)
                    df["league"] = league
                    df["year"] = year

                    all_matches.append(df)

        if all_matches:
            self.data = pd.concat(all_matches, ignore_index=True)
        else:
            raise FileNotFoundError("No corresponding .csv file found in directory")

        return self.data