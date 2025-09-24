import os

import pandas as pd

class DataHandler:
    """
    Class which contains functions to load, combine, prepare and get the data set information of the 40 football match data sets for a data analysis
    """

    def __init__(self):
        """
        Function which initializes a data handler object including a data path and a space to save the data
        """
        self.path = "data/top5"
        self.data = None

    def load_data(self):
        """
        Function which loads all 40 .csv (5 different leagues with 8 years) files into one data frame.
        Returns a data frame of all leagues data.
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
                    df["year"] = str(year)[:9]

                    #   append the data frame to the already combined data sets
                    all_matches.append(df)

        # print out if any column mismatches appear
        if column_mismatches:
            print("Warning: There are column mismatches between the csv files!")
            for file, cols in column_mismatches.items():
                print(f"{file}: {cols}")
        else:
            print("Data loading successful.")

        if all_matches:
            # add data into the class object
            self.data = pd.concat(all_matches, ignore_index=True)
        else:
            # raise corresponding error when the loading fails
            raise FileNotFoundError("No corresponding .csv file found in directory")

        # give out the created data frame to be able to continue working with it in the notebook
        return self.data

    def preprocess_data(self, relevant_cols = None, col_names = None):
        """
        Function to clean and prepare the football data for further analysis by:
        - changing column names
        - selecting relevant columns
        - checking and handling of missing values

        Parameters
        ----------
        relevant_cols : list, optional
            List of column names to keep for analysis.
            If None, all columns are kept.
        col_names : list, optional
            list for renaming columns, e.g. ["hometeam", ...].
            Must have the same length as current dataframe columns.

        Returns
        -------
        pd.DataFrame
        Preprocessed football data.
        """
        # check if data is loaded, else raise an error
        if self.data is None:
            raise ValueError("No data loaded. Please call load_data() first.")

        # take a copy of the loaded data to preprocess
        df = self.data.copy()

        # select relevant columns (or keep all)
        if relevant_cols:
            keep = [col for col in relevant_cols if col in df.columns]
            df = df[keep]

        # rename columns if provided
        if col_names:
            expected_len = len(relevant_cols) if relevant_cols else df.shape[1]
            if len(col_names) != expected_len:
                raise ValueError("Length of col_names must match number of selected columns")
            df.columns = col_names

            # check for missing values
            na_counts = df.isna().sum()
            if na_counts.sum() > 0:
                print("Missing values detected:")
                print(na_counts[na_counts > 0])
            else:
                print("No missing values found.")

        # save and return the pre-processed df
        self.data = df
        return self.data

    def get_dataset_information(self):
        """
        Function that prints a quick overview of the football dataset:
        - shape
        - unique leagues and seasons
        - columns
        - missing values per column
        - basic statistics for numerical columns
        """

        # raise an error if no data is stored already
        if self.data is None:
            raise ValueError("No data loaded. Please call load_data() first.")

        # get the data frame
        df = self.data

        # print out the most important data frame info
        print("Dataset Overview")
        print("--------------------")
        print("Shape:", df.shape)
        print("Leagues:", df['league'].unique() if 'league' in df.columns else "No 'league' column")
        print("Seasons:", sorted(df['year'].unique()) if 'year' in df.columns else "No 'year' column")

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nMissing Values per Column:")
        print(df.isna().sum()[df.isna().sum() > 0])

        print("\nBasic Statistics (numeric columns):")
        print(df.describe())


