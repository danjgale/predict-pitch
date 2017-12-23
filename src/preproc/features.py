"""Preprocessing of model features"""

import sys
import numpy as np
import pandas as pd
from scipy.stats import circmean
from scipy.spatial.distance import euclidean
import pickle

sys.path.append('../')
from utils.PitchDB import PitchDB

# Normalize within each pitcher, since we're interested in within-pitcher
# variability. Whatever normalization parameters gathered here for pitchers in
# test set need to be saved off


def compute_init_displacement(x):
    """Get distance between 0-position and 225ms position"""
    return euclidean(
        np.array([x['x0'], x['z0']]), np.array([x['tx_225'], x['tz_225']])
    )


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
        return 1
    else:
        return 0


def side_encoder(x):
    if x == 'R':
        return 1
    else:
        return 0


def convert_velocity(x):
    """Convert from ft/s to m/h """
    return x.abs() * 0.6818


def compute_angular_mean(x):
    # calculate in radians and convert back to deg
    return np.rad2deg(circmean(np.radians(x)))


def bin_data(x, bins, labels):
    percentiles = np.percentile(x, bins)
    return pd.cut(x, percentiles, labels=labels)


def strike_percent(x):
    return np.around((sum(x['is_strike']) / x.shape[0]) * 100, 2)


if __name__ == '__main__':

    db = PitchDB()
    df = db.query('select * from dataset')

    # drop unwanted data
    df = df[~df['play_guid'].str.contains('_2017_')]
    df = df[df['pitch_type'] != 'IN']
    df = df.dropna(subset=['tx_225', 'tz_225',
                           'tx_175', 'tz_175', 'spin_rate'])

    # compute initial displacement (from 50ft to 225ms after release)
    df['disp'] = df.apply(lambda x: compute_init_displacement(x), axis=1)

    # scale positional features within pitchers
    scale_feats = ['tx_225', 'tz_225', 'tx_175',
                   'tz_175', 'x0', 'z0', 'disp']
    df, means = scale_pitchers(df, scale_feats)


    # save off scaled_params
    with open('../../data/pitcher_means.p', 'wb') as f:
        pickle.dump(means, f)

    # velocity conversion
    df['mph'] = convert_velocity(df['vy0'])

    # preprocess spin data
    df['spin_means_by_pitcher'] = (
        df
        .groupby(('pitcher', 'pitch_type'))['spin_dir']
        .transform(compute_angular_mean)
    )
    df['spin_rate_rating'] = bin_data(
        df.spin_rate, [0, 25, 50, 75, 100], [0, 1, 2, 3]
    )
    df['spin_rate_rating'] = bin_data(
        df.spin_rate, [0, 25, 50, 75, 100], [0, 1, 2, 3]
    )

    # preprocess stance / handedness data
    stance_funct = np.vectorize(
        label_stance_match, otypes=[int], cache=False
    )
    df['is_same_matchup'] = stance_funct(df['p_throws'], df['stand'])

    side_funct = np.vectorize(
        side_encoder, otypes=[int], cache=False
    )
    df['is_pitcher_RH'] = side_funct(df['p_throws'])
    df['is_batter_R'] = side_funct(df['stand'])

    # finalize dataframe for modelling. Note that an excess of features are
    # included and can be dropped just prior to modelling to test out how
    # different features might affect model performance

    train = df[['is_strike', 'scaled_tx_225', 'scaled_tz_225', 'scaled_disp',
        'scaled_x0', 'scaled_z0', 'mph', 'balls', 'strikes', 'o',
        'is_same_matchup', 'is_pitcher_RH', 'is_batter_R',
        'spin_means_by_pitcher', 'spin_rate_rating']]

    train.to_csv('../../data/training.csv')



