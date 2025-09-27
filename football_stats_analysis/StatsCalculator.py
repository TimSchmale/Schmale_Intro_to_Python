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
        # raise error if no data is passed
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
        Calculate the progression of team standings over a season in a cleaner way.
        """
        df = self.data[(self.data['league'] == league) & (self.data['year'] == season)].copy()
        if df.empty:
            available_leagues = self.data['league'].unique()
            available_seasons = self.data['year'].unique()
            raise ValueError(
                f"No matches found for league '{league}' and season '{season}'.\n"
                f"Available leagues: {sorted(available_leagues)}\n"
                f"Available seasons: {sorted(available_seasons)}"
            )

        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        teams = pd.unique(df[['HomeTeam', 'AwayTeam']].values.ravel())

        # Initialize progression container
        progression = []

        # Loop through matchdays (chronologisch nach Datum)
        for i, match in df.iterrows():
            # Update standings per match
            home, away = match['HomeTeam'], match['AwayTeam']
            gf_home, gf_away = match['FTHG'], match['FTAG']

            # create or update points for both teams
            for team, scored, conceded in [(home, gf_home, gf_away), (away, gf_away, gf_home)]:
                last = progression[-1] if progression and progression[-1]['Team'] == team else None
                points = last['Points'] if last else 0
                gf = last['GF'] if last else 0
                ga = last['GA'] if last else 0

                # update points
                if team == home and gf_home > gf_away:
                    points += 3
                elif team == away and gf_away > gf_home:
                    points += 3
                elif gf_home == gf_away:
                    points += 1

                # update goals
                gf += scored
                ga += conceded
                gd = gf - ga

                progression.append({
                    'Team': team,
                    'Matchday': len([p for p in progression if p['Team'] == team]) + 1,
                    'Points': points,
                    'GF': gf,
                    'GA': ga,
                    'GD': gd,
                    'Date': match['Date']
                })

        # Create DataFrame
        prog_df = pd.DataFrame(progression)

        # Compute ranks per matchday
        prog_df['Rank'] = prog_df.groupby('Matchday').apply(
            lambda x: x.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False])
            .assign(Rank=lambda d: range(1, len(d) + 1))
        ).reset_index(drop=True)['Rank']

        return prog_df

    def league_comparison(self) -> pd.DataFrame:
        """
        Create a summary table with key information about all leagues in the dataset.

        Returns
        -------
        pd.DataFrame
            Table with columns [League, Season, Matches, Teams, Goals, AvgGoalsPerMatch].
        """
        # raise an error if no data is available
        if self.data is None or self.data.empty:
            raise ValueError("No data available.")

        # create an overview table of descriptive statistics
        overview = (
            self.data.groupby(['league'])
            .agg(
                Seasons=('year', 'nunique'),
                Matches=('Date', 'count'),
                DifferentTeams=('HomeTeam', lambda x: len(set(x) | set(self.data.loc[x.index, 'AwayTeam']))),
                HomeGoals=('FTHG', 'mean'),
                AwayGoals=('FTAG', 'mean'),
                HomeXGoals=('HxG', 'mean'),
                AwayXGoals=('AxG', 'mean'),
                HomeXPoints=('HxPTS', 'mean'),
                AwayXPoints=('AxPTS', 'mean'),
                HomeFouls=('HF', 'mean'),
                AwayFouls=('AF', 'mean'),
                HomeYellowCards=('HY', 'mean'),
                AwayYellowCards=('AY', 'mean'),
                HomeRedCards=('HR', 'mean'),
                AwayRedCards=('AR', 'mean'),
                HomeAvgAge=('HomeAvgAge', 'mean'),
                AwayAvgAge=('AwayAvgAge', 'mean'),
                HomeMarketValue=('HomeMV', 'mean'),
                AwayMarketValue=('AwayMV', 'mean')
            )
            .reset_index()
        )

        # transpose and round
        overview_t = overview.set_index("league").T.round(2)

        return overview_t
