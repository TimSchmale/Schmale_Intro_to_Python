import os

import pandas as pd

class StatsCalculator:
    """
    Class to calculate key football statistics such as team summaries, league tables, and comparisons between teams.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the class object a preprocessed football dataset.

        Parameters
        ----------
        data : pd.DataFrame
            The dataset returned by DataHandler.
        """
        if data is None or data.empty:
            raise ValueError("Data must not be empty. Please provide a valid DataFrame.")
        self.data = data

    def league_table(self, league: str, season: str) -> pd.DataFrame:
        """
        Calculate the final league table for a given league and season.

        Parameters
        ----------
        league : str
            League identifier (e.g., 'EPL' or 'LaLiga')
        season : str
            Season identifier (e.g., '2015' or '2018')

        Returns
        -------
        pd.DataFrame
            Final league table sorted by points, then goal difference.
        """
        df = self.data[(self.data['league'] == league) & (self.data['year'] == season)]

        if df.empty:
            available_leagues = self.data['league'].unique()
            available_seasons = self.data['year'].unique()

            raise ValueError(
                f"No matches found for league '{league}' and season '{season}'.\n"
                f"Available leagues: {sorted(available_leagues)}\n"
                f"Available seasons: {sorted(available_seasons)}"
            )

        # Initialize standings
        standings = {}

        for _, match in df.iterrows():
            home, away = match['HomeTeam'], match['AwayTeam']
            hg, ag = match['FTHG'], match['FTAG']

            # Ensure both teams exist in standings
            for team in [home, away]:
                if team not in standings:
                    standings[team] = {"Points": 0, "Played": 0, "Wins": 0,
                                       "Draws": 0, "Losses": 0, "GF": 0, "GA": 0}

            # Update matches played
            standings[home]["Played"] += 1
            standings[away]["Played"] += 1

            # Update goals for/against
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

        # Convert to DataFrame
        table = pd.DataFrame.from_dict(standings, orient="index")
        table["GD"] = table["GF"] - table["GA"]

        # Sort by Points, Goal Difference, Goals For
        table = table.sort_values(by=["Points", "GD", "GF"], ascending=[False, False, False])

        return table.reset_index().rename(columns={"index": "Team"})
