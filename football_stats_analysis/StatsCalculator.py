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

        # Get index column starting with 1 instead of 0
        table = (
            table.reset_index()
            .rename(columns={"index": "Team"})
            .reset_index(drop=True)
        )

        table.insert(0, "Rank", range(1, len(table) + 1))

        return table.reset_index().rename(columns={"index": "Team"})

    def league_progression(self, league: str, season: str) -> pd.DataFrame:
        """
        Calculate team standings progression over a season in a team-centered approach.
        """
        # get a data frame copy
        df = self.data[(self.data['league'] == league) & (self.data['year'] == season)].copy()

        # raise an error if league or year are not given
        if df.empty:
            available_leagues = self.data['league'].unique()
            available_seasons = self.data['year'].unique()
            raise ValueError(
                f"No matches found for league '{league}' and season '{season}'.\n"
                f"Available leagues: {sorted(available_leagues)}\n"
                f"Available seasons: {sorted(available_seasons)}"
            )

        # make sure date format is correct and get all teams
        df['Date'] = pd.to_datetime(df['Date'])
        teams = pd.unique(df[['HomeTeam', 'AwayTeam']].values.ravel())

        # initialize the progression
        progression = []

        # iterate over teams to calculate their individual season progression
        for team in teams:
            team_matches = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].sort_values('Date')
            points = 0
            gf = 0
            ga = 0

            # iterate over all games for selected team. This enables an easy matchday calculation independent of the
            # dates which build one league matchday
            for matchday, (_, match) in enumerate(team_matches.iterrows(), 1):
                if match['HomeTeam'] == team:
                    scored, conceded = match['FTHG'], match['FTAG']
                else:
                    scored, conceded = match['FTAG'], match['FTHG']

                # only update the selected team, ignore the opponent
                if scored > conceded:
                    points += 3
                elif scored == conceded:
                    points += 1

                gf += scored
                ga += conceded
                gd = gf - ga

                # update the teams progression
                progression.append({
                    'Team': team,
                    'Matchday': matchday,
                    'Points': points,
                    'GF': gf,
                    'GA': ga,
                    'GD': gd,
                    'Date': match['Date']
                })

        # build a data frame
        prog_df = pd.DataFrame(progression)

        # calculate the rankings per matchday after all team progressions (points) have been calculated
        ranks = []
        for md, group in prog_df.groupby('Matchday'):
            ranked = group.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False]).copy()
            ranked['Rank'] = range(1, len(ranked) + 1)
            ranks.append(ranked)

        prog_df = pd.concat(ranks).sort_values(['Matchday', 'Rank']).reset_index(drop=True)
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
                AwayRedCards=('AR', 'mean')
            )
            .reset_index()
        )

        # transpose and round
        overview_t = overview.set_index("league").T.round(2)

        return overview_t
