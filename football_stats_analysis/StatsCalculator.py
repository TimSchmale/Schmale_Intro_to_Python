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
        Function to calculate the progression of team standings throughout a season for a given league.

        Parameters
        ----------
        league : str
            League identifier (e.g., 'epl')
        season : str
            Season identifier (e.g., '2021-2022')

        Returns
        -------
        pd.DataFrame
            DataFrame with columns [Date, Matchday, Team, Points, GF, GA, GD, Rank]
            showing the progression of each team over the duration of the season.
        """
        # apply the filter for league and season to restrict the data frame
        df = self.data[(self.data['league'] == league) & (self.data['year'] == season)]

        if df.empty:
            available_leagues = self.data['league'].unique()
            available_seasons = self.data['year'].unique()
            raise ValueError(
                f"No matches found for league '{league}' and season '{season}'.\n"
                f"Available leagues: {sorted(available_leagues)}\n"
                f"Available seasons: {sorted(available_seasons)}"
            )

        # sort df by date to enable the following matchday calculations
        df = df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        # get all teams
        teams = pd.unique(df[['HomeTeam', 'AwayTeam']].values.ravel())

        # initialize the standings and progression calculation elements
        # progression will combine all table snapshots after each matchday in one data frame
        standings = {team: {'Points': 0, 'GF': 0, 'GA': 0, 'GD': 0} for team in teams}
        progression = []

        # iterate through all matches of the selected season and league
        for _, match in df.iterrows():
            home = match['HomeTeam']
            away = match['AwayTeam']
            gf_home = match['FTHG']
            gf_away = match['FTAG']

            # update the points
            if gf_home > gf_away:
                standings[home]['Points'] += 3
            elif gf_home < gf_away:
                standings[away]['Points'] += 3
            else:
                standings[home]['Points'] += 1
                standings[away]['Points'] += 1

            # calculate goals and goal difference
            standings[home]['GF'] += gf_home
            standings[home]['GA'] += gf_away
            standings[home]['GD'] = standings[home]['GF'] - standings[home]['GA']

            standings[away]['GF'] += gf_away
            standings[away]['GA'] += gf_home
            standings[away]['GD'] = standings[away]['GF'] - standings[away]['GA']

            # create the tabel after the matchday. sort it by points to get the overview completely
            table = (
                pd.DataFrame.from_dict(standings, orient='index')
                .assign(Team=lambda x: x.index)
                .sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False])
                .reset_index(drop=True)
            )
            # create the rank
            table['Rank'] = table.index + 1

            # save the snapshot of the calculated table in the progressions
            for team in [home, away]:
                team_games_played = len([p for p in progression if p['Team'] == team])
                row = table.loc[table['Team'] == team].iloc[0]
                progression.append({
                    'Team': team,
                    'Matchday': team_games_played + 1,
                    'Points': row['Points'],
                    'GF': row['GF'],
                    'GA': row['GA'],
                    'GD': row['GD'],
                    'Rank': row['Rank'],
                    'Date': match['Date']
                })

        return pd.DataFrame(progression)

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
