"""Preprocessing of model features"""

import numpy as np
import pandas as pd
from sklearn import preprocessing

# Normalize within each pitcher, since we're interested in within-pitcher
# variability. Whatever normalization parameters gathered here for pitchers in
# test set need to be saved off

def pitcher_feat_scale(pitcher_df, features, how='mean_center'):
    """Pitcher-level feature scaling; can either be normalization or
    mean-center scaling. The transformed data and the estimator object
    (for transforming the test data) are returned.
    """
    if how == 'mean_center':
        means = np.mean(pitcher_df[features], axis=0)
        scaled = pitcher_df[features] - means
        params = means
    elif how == 'standard':
        scaler = preprocessing.StandardScaler().fit(pitcher_df[features])
        params = scaler
        scaled = scaler.transform(pitcher_df[features])
    return params, scaled


def scale_pitchers(df, features, how='mean_center'):
    """Scale all pitchers in df. Either use how='mean_center' or
    how='standard'.
    """

    pitchers = df.groupby('pitcher')

    scaled_feat_cols = ['scaled_' + i for i in features]

    list_ = []
    dict_ = {}
    for name, g in pitchers:
        params, transformed = pitcher_feat_scale(g, features, how)
        # add back in with rest of data
        list_.append(pd.concat(
            [g, pd.DataFrame(transformed.as_matrix(), index=g.index.values,
                             columns=scaled_feat_cols)], axis=1)
        )

        dict_[name] = params  # collect parameters of scaling

    return pd.concat(list_), dict_


def label_stance_match(hand, stance):
    if hand == stance:
        return 'same'
    else:
        return 'opp'


def convert_velocity(x):
    """Convert from ft/s to m/h """
    return x.abs() * 0.6818







# keep track of R/L of pitchers and batters to retain that info after
# normalization. Or, re-label a L-L/R-R matchup as 'Same' and L-R/R-L as 'Opp'


# convert vy0 feet per second to mph

# remove intentional walks
