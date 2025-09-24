import os

import pandas as pd

class StatsCalculator:
    """
    Class to calculate key football statistics such as team summaries, league tables, and comparisons between teams.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Function to initialize the StatsCalculator class object using a preprocessed football dataset.

        Parameters
        ----------
        data : pd.DataFrame
            The dataset returned by DataHandler.
        """
        # raise error if noe da is passed
        if data is None or data.empty:
            raise ValueError("Data must not be empty. Please provide a valid DataFrame.")
        self.data = data

    def league_table(self, league: str, season: str) -> pd.DataFrame:
        """
        Function to calculate the final league table for a given league and season.

        Parameters
        ----------
        league : str
            League identifier (e.g., 'epl' or 'la_liga')
        season : str
            Season identifier (e.g., '2021-2022' or '2018-2019')

        Returns
        -------
        pd.DataFrame
            Final league table sorted by points, and secondly by goal difference.
        """
        # reduce the given data set to the selected league and year
        df = self.data[(self.data['league'] == league) & (self.data['year'] == season)]

        # error handling in case there is a mismatch between the input and the content in the corresponding columns
        if df.empty:
            available_leagues = self.data['league'].unique()
            available_seasons = self.data['year'].unique()

            # include the potential choices in the error message to improve usability
            raise ValueError(
                f"No matches found for league '{league}' and season '{season}'.\n"
                f"Available leagues: {sorted(available_leagues)}\n"
                f"Available seasons: {sorted(available_seasons)}"
            )

        # Initialize the standings
        standings = {}

        # iterate over all matches of the league and season to calculate the standings
        for _, match in df.iterrows():
            home, away = match['HomeTeam'], match['AwayTeam']
            hg, ag = match['FTHG'], match['FTAG']

            # Ensure both teams exist in standings
            for team in [home, away]:
                if team not in standings:
                    standings[team] = {"Points": 0, "Played": 0, "Wins": 0,
                                       "Draws": 0, "Losses": 0, "GF": 0, "GA": 0}

            # Update matches played for both teams
            standings[home]["Played"] += 1
            standings[away]["Played"] += 1

            # Update goals for/against for both teams
            standings[home]["GF"] += hg
            standings[home]["GA"] += ag
            standings[away]["GF"] += ag
            standings[away]["GA"] += hg

            # Update results
            if hg > ag:  # Home win
                standings[home]["Points"] += 3
                standings[home]["Wins"] += 1
                standings[away]["Losses"] += 1
            elif hg < ag:  # Away win
                standings[away]["Points"] += 3
                standings[away]["Wins"] += 1
                standings[home]["Losses"] += 1
            else:  # Draw
                standings[home]["Points"] += 1
                standings[away]["Points"] += 1
                standings[home]["Draws"] += 1
                standings[away]["Draws"] += 1

        # Convert result to DataFrame
        table = pd.DataFrame.from_dict(standings, orient="index")
        table["GD"] = table["GF"] - table["GA"]

        # Sort by Points, Goal Difference, Goals For
        table = table.sort_values(by=["Points", "GD", "GF"], ascending=[False, False, False])

        return table.reset_index().rename(columns={"index": "Team"})

    def league_progression(self, league: str, season: str) -> pd.DataFrame:
        """
        Function to calculate the progression of team rankings throughout a season for a given league.

        Parameters
        ----------
        league : str
            League identifier (e.g., 'bundesliga')
        season : str
            Season identifier (e.g., '2021-2022')

        Returns
        -------
        pd.DataFrame
            DataFrame with columns [Date, Matchday, Team, Points, GD, Rank]
            showing the rank of each team after every matchday.
        """
        # initialize a data frame that is reduced to selected league and column
        df = self.data[(self.data['league'] == league) & (self.data['year'] == season)]

        # check if the input is correct and go into error handling if not
        if df.empty:
            available_leagues = self.data['league'].unique()
            available_seasons = self.data['year'].unique()

            # raise an error if the season or league is incorrectly selected and give out the potential inputs for increased usability
            raise ValueError(
                f"No matches found for league '{league}' and season '{season}'.\n"
                f"Available leagues: {sorted(available_leagues)}\n"
                f"Available seasons: {sorted(available_seasons)}"
            )

        # ensure Date is datetime
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        #
        standings = {}
        progression = []

        for _, match in df.iterrows():
            date = match["Date"]
            home, away = match['HomeTeam'], match['AwayTeam']
            hg, ag = match['FTHG'], match['FTAG']

            # Initialize teams if not present
            for team in [home, away]:
                if team not in standings:
                    standings[team] = {"Points": 0, "Played": 0, "Wins": 0,
                                       "Draws": 0, "Losses": 0, "GF": 0, "GA": 0}

            # Update matches played
            standings[home]["Played"] += 1
            standings[away]["Played"] += 1

            # Update goals
            standings[home]["GF"] += hg
            standings[home]["GA"] += ag
            standings[away]["GF"] += ag
            standings[away]["GA"] += hg

            # Update results
            if hg > ag:
                standings[home]["Points"] += 3
                standings[home]["Wins"] += 1
                standings[away]["Losses"] += 1
            elif hg < ag:
                standings[away]["Points"] += 3
                standings[away]["Wins"] += 1
                standings[home]["Losses"] += 1
            else:
                standings[home]["Points"] += 1
                standings[away]["Points"] += 1
                standings[home]["Draws"] += 1
                standings[away]["Draws"] += 1

            # Create current standing to save the snapshot
            table = pd.DataFrame.from_dict(standings, orient="index")
            table["GD"] = table["GF"] - table["GA"]
            table = table.sort_values(by=["Points", "GD", "GF"], ascending=[False, False, False])
            table["Rank"] = range(1, len(table) + 1)

            # Save snapshot
            for team, row in table.iterrows():
                progression.append({
                    "Date": date,
                    "Team": team,
                    "Points": row["Points"],
                    "GD": row["GD"],
                    "Rank": row["Rank"]
                })

        # get a final data frame
        progression_df = pd.DataFrame(progression)

        # determine the matchdays
        progression_df = progression_df.sort_values(["Date", "Team"])
        progression_df["Matchday"] = progression_df.groupby("Team").cumcount() + 1

        return progression_df

