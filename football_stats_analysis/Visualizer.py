import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

class Visualizer:
    """
    Class to handle visualization and comparison of football statistics such as
    team progression, league summaries, and team comparisons.
    """

    def __init__(self, progression: pd.DataFrame, summary: pd.DataFrame) -> None:
        """
        Initialize the Visualizer class with progression and summary data.

        Parameters
        ----------
        progression : pd.DataFrame
            DataFrame containing the team progression over matchdays.
        summary : pd.DataFrame
            DataFrame containing summary statistics for leagues.
        """
        # raise an error for empty inputs
        if progression is None or progression.empty:
            raise ValueError("Progression must not be empty. Please provide a valid DataFrame.")
        self.progression = progression

        if summary is None or summary.empty:
            raise ValueError("Summary must not be empty. Please provide a valid DataFrame.")
        self.summary = summary

    def visualize_progression(self) -> None:
        # raise an error for empty progression
        if self.progression is None or self.progression.empty:
            raise ValueError("progression must not be empty. Please provide a valid DataFrame.")

        df_prog = self.progression.sort_values('Matchday')

        # in need of more colours thane the 10 standard ones
        teams = df_prog['Team'].unique()
        n_teams = len(teams)
        colors = cm.get_cmap('tab20', n_teams)

        # initialize the subplots
        fig, axes = plt.subplots(1, 2, figsize=(18, 7))

        # Rankings plot
        for i, team in enumerate(teams):
            team_df = df_prog[df_prog['Team'] == team]
            axes[0].plot(team_df['Matchday'], team_df['Rank'], marker='o',
                         label=team, color=colors(i))
        axes[0].invert_yaxis()
        axes[0].set_xlabel('Matchday')
        axes[0].set_ylabel('Rank')
        axes[0].set_title('Team Rankings Over the Season')
        axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[0].grid(True, alpha=0.3)

        # Points plot
        for i, team in enumerate(teams):
            team_df = df_prog[df_prog['Team'] == team]
            axes[1].plot(team_df['Matchday'], team_df['Points'], marker='o',
                         label=team, color=colors(i))
        axes[1].set_xlabel('Matchday')
        axes[1].set_ylabel('Points')
        axes[1].set_title('Points Progression Over the Season')
        axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1].grid(True, alpha=0.3)

        # give out the plot
        plt.tight_layout()
        plt.show()

    def visualize_summary(self) -> None:
        """
        Visualize home vs away points, goals, xPoints, xGoals, and cards for all leagues.
        """

        # raise an error if summary not correctly filled
        if self.summary is None or self.summary.empty:
            raise ValueError("Summary must not be empty. Please provide a valid DataFrame.")

        df = self.summary
        leagues = df.columns
        n = len(leagues)
        x = np.arange(n)
        width = 0.35

        # initialize 3x2 subplots
        fig, axes = plt.subplots(3, 2, figsize=(18, 15))
        axes = axes.flatten()

        # Plot 1: Points
        axes[0].bar(x - width / 2, df.loc['HomeXPoints'], width, label='Home Points', color='skyblue')
        axes[0].bar(x + width / 2, df.loc['AwayXPoints'], width, label='Away Points', color='salmon')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(leagues, rotation=45, ha='right')
        axes[0].set_ylabel('Average Points')
        axes[0].set_title('Home vs Away Points per League')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        # Plot 2: Goals
        axes[1].bar(x - width / 2, df.loc['HomeGoals'], width, label='Home Goals', color='skyblue')
        axes[1].bar(x + width / 2, df.loc['AwayGoals'], width, label='Away Goals', color='salmon')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(leagues, rotation=45, ha='right')
        axes[1].set_ylabel('Average Goals')
        axes[1].set_title('Home vs Away Goals per League')
        axes[1].legend()
        axes[1].grid(axis='y', alpha=0.3)

        # Plot 3: Expected Points
        axes[2].bar(x - width / 2, df.loc['HomeXPointsExpected'], width, label='Home XPoints', color='skyblue')
        axes[2].bar(x + width / 2, df.loc['AwayXPointsExpected'], width, label='Away XPoints', color='salmon')
        axes[2].set_xticks(x)
        axes[2].set_xticklabels(leagues, rotation=45, ha='right')
        axes[2].set_ylabel('Average XPoints')
        axes[2].set_title('Home vs Away Expected Points per League')
        axes[2].legend()
        axes[2].grid(axis='y', alpha=0.3)

        # Plot 4: Expected Goals
        axes[3].bar(x - width / 2, df.loc['HomeXGoals'], width, label='Home XGoals', color='skyblue')
        axes[3].bar(x + width / 2, df.loc['AwayXGoals'], width, label='Away XGoals', color='salmon')
        axes[3].set_xticks(x)
        axes[3].set_xticklabels(leagues, rotation=45, ha='right')
        axes[3].set_ylabel('Average XGoals')
        axes[3].set_title('Home vs Away Expected Goals per League')
        axes[3].legend()
        axes[3].grid(axis='y', alpha=0.3)

        # Plot 5: Red Cards
        axes[4].bar(x - width / 2, df.loc['HomeRedCards'], width, label='Home Red Cards', color='skyblue')
        axes[4].bar(x + width / 2, df.loc['AwayRedCards'], width, label='Away Red Cards', color='salmon')
        axes[4].set_xticks(x)
        axes[4].set_xticklabels(leagues, rotation=45, ha='right')
        axes[4].set_ylabel('Average Red Cards')
        axes[4].set_title('Home vs Away Red Cards per League')
        axes[4].legend()
        axes[4].grid(axis='y', alpha=0.3)

        # Plot 6: Yellow Cards
        axes[5].bar(x - width / 2, df.loc['HomeYellowCards'], width, label='Home Yellow Cards', color='skyblue')
        axes[5].bar(x + width / 2, df.loc['AwayYellowCards'], width, label='Away Yellow Cards', color='salmon')
        axes[5].set_xticks(x)
        axes[5].set_xticklabels(leagues, rotation=45, ha='right')
        axes[5].set_ylabel('Average Yellow Cards')
        axes[5].set_title('Home vs Away Yellow Cards per League')
        axes[5].legend()
        axes[5].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.show()

