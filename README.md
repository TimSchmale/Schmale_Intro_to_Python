# Football Data Analysis

## Package Introduction

This repository provides a Python package "football_stats_analysis" for working with the following European football data set from Kaggle: https://www.kaggle.com/datasets/ferrariboy4k/top5leagues?select=top5.
The package provides functions to load, preprocess, analyze and visualize the information of the data set which consists of 40 .csv files covering all matches from the top five European leagues from 2014/15 to 2021/22.
Each file includes detailed information for home and away teams, such as:
- final scoreline
- expected goals (xG)
- expected points (xPts)
- number of yellow and red cards
- and much more

## Installation

Clone this repository and install the package locally:

```bash
git clone https://github.com/username/football_stats_analysis.git
cd football_stats_analysis
pip install -e .
```

## Usage in notebooks
After installation, you can import and use the package as follows:

```bash
from football_stats_analysis.DataHandler import DataHandler
from football_stats_analysis.StatsCalculator import StatsCalculator
from football_stats_analysis.Visualizer import Visualizer
```
## Coding Examples
### Load the dataset
```bash
dh = DataHandler()
df = dh.load_data()
```

### Calculate league table
```bash
sc = StatsCalculator(df)
sc.league_table('epl', '2021-2022')
```

### Visualize seasonal progression
```bash
progression = sc.league_progression('epl', '2021-2022')
vis = Visualizer()
vis.progression = progression
vis.visualize_progression()
```

## Licence
This repository is licensed under the MIT License. See LICENSE.txt for details.


