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
        # initialize a list which holds the different csv files
        all_matches = []

        # initialize structure to be able to track if the data set columns match through the different csv files
        all_columns = None
        column_mismatches = {}

        # iterate over all leagues
        for league in os.listdir(self.path):
            league_path = os.path.join(self.path, league)

            if os.path.isdir(league_path):
                # iterate over all years
                for year in os.listdir(league_path):
                    year_path = os.path.join(league_path, year)

                    # read in the csv
                    df = pd.read_csv(year_path)

                    # check mechanism for column mismatches
                    if all_columns is None:
                        all_columns = list(df.columns)
                    else:
                        if set(all_columns) != set(df.columns):
                            column_mismatches[f"{league}/{year}"] = list(df.columns)

                    # add custom columns to differentiate between the leagues and seasons easily
                    df["league"] = league
                    df["year"] = year

                    #   append the data frame to the already combined data sets
                    all_matches.append(df)
        # print out if any column mismatches appear
        if column_mismatches:
            print("⚠️ Warning: There are column mismatches between the csv files!")
            for file, cols in column_mismatches.items():
                print(f"{file}: {cols}")

        if all_matches:
            # add data into the class object
            self.data = pd.concat(all_matches, ignore_index=True)
        else:
            # raise corresponding error when the loading fails
            raise FileNotFoundError("No corresponding .csv file found in directory")

        # give out the created data frame to be able to continue working with it in the notebook
        return self.data