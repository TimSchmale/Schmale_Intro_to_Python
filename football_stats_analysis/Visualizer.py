import pandas as pd
import matplotlib.pyplot as plt
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
        if progression is None or progression.empty:
            raise ValueError("progression must not be empty. Please provide a valid DataFrame.")
        self.progression = progression

        if summary is None or summary.empty:
            raise ValueError("summary must not be empty. Please provide a valid DataFrame.")
        self.summary = summary

    def visualize_progression(self) -> None:
        """
        Visualize league progression as line plots for team rankings and points
        based on the precomputed progression table in self.progression.
        """
        df_prog = self.progression.sort_values('Matchday')

        fig, axes = plt.subplots(1, 2, figsize=(18, 7))

        # create the first plot based on the rankings
        for team, team_df in df_prog.groupby('Team'):
            axes[0].plot(team_df['Matchday'], team_df['Rank'], marker='o', label=team)
        axes[0].invert_yaxis()  # 1st place on top
        axes[0].set_xlabel('Matchday')
        axes[0].set_ylabel('Rank')
        axes[0].set_title('Team Rankings Over the Season')
        axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[0].grid(True, alpha=0.3)

        # create the second plot based on the points
        for team, team_df in df_prog.groupby('Team'):
            axes[1].plot(team_df['Matchday'], team_df['Points'], marker='o', label=team)
        axes[1].set_xlabel('Matchday')
        axes[1].set_ylabel('Points')
        axes[1].set_title('Points Progression Over the Season')
        axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def visualize_summary(self) -> None:
        """
        Visualize home vs away points and goals for all leagues as side-by-side bar charts.
        """
        df = self.summary  # sollte overview_t liefern

        leagues = df.columns
        n = len(leagues)
        x = np.arange(n)  # Positions for bars
        width = 0.35  # Breite der Balken

        fig, axes = plt.subplots(1, 2, figsize=(18, 7))

        # create plot one for the points
        home_points = df.loc['HomeXPoints']
        away_points = df.loc['AwayXPoints']
        axes[0].bar(x - width / 2, home_points, width, label='Home Points', color='skyblue')
        axes[0].bar(x + width / 2, away_points, width, label='Away Points', color='salmon')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(leagues, rotation=45, ha='right')
        axes[0].set_ylabel('Average Points')
        axes[0].set_title('Home vs Away Points per League')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        # create goal plot
        home_goals = df.loc['HomeGoals']
        away_goals = df.loc['AwayGoals']
        axes[1].bar(x - width / 2, home_goals, width, label='Home Goals', color='skyblue')
        axes[1].bar(x + width / 2, away_goals, width, label='Away Goals', color='salmon')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(leagues, rotation=45, ha='right')
        axes[1].set_ylabel('Average Goals')
        axes[1].set_title('Home vs Away Goals per League')
        axes[1].legend()
        axes[1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.show()
