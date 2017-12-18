"""Preprocessing module"""

import pandas as pd
import numpy as np
import json
import sys

sys.path.append('../utils')
from PitchDB import PitchDB


def generate_table(db):
    """Queries to pull in appropriate data and join for main table"""
    q1 = (
        'select gameday_link, num, pitcher, pitcher_name, batter, batter_name, '
        'b, s, o, p_throws, stand '
        'from atbat'
    )
    q2 = (
        'select num, event_num, play_guid, count, type, pitch_type, gameday_link, '
        'sz_top, sz_bot, px, pz, spin_rate, spin_dir, vx0, vy0, vz0, x0, y0, z0 '
        'from pitch'
    )
    q3 = (
        'select trajectories, gameday_link, event_num, play_guid '
        'from snapshots'
    )
    df = (
        db.query(q2)
          .merge(db.query(q3), on=('gameday_link', 'event_num', 'play_guid'))
          .merge(db.query(q1), on=('gameday_link', 'num'))
    )
    return df

def compute_zone_height(x, median=True, add_radius=True):
    """Get central tendency of zone limits for each batter.

    There can be variability of the strike zone height for each batter.
    Therefore, to make things consistent, this takes either the mean or median
    of the top and bottom of a player's strike zone. The ball radius can be
    accounted for as well.
    """

    if median:
        grouped = x.groupby('batter').median()[['sz_top', 'sz_bot']]
    else:
        grouped = x.groupby('batter').mean()[['sz_top', 'sz_bot']]

    if add_radius:
        ball_radius = 1.57 / 12
        grouped['sz_top'] = grouped['sz_top'] + ball_radius
        grouped['sz_bot'] = grouped['sz_bot'] - ball_radius

    grouped.rename(
        columns={'sz_top': 'adj_sz_top', 'sz_bot': 'adj_sz_bot', },
        inplace=True
    )

    grouped.reset_index(level=0, inplace=True)

    return grouped


def call_pitch(x, z, zone_bounds):
    """Determine if pitch is a strike or a ball based on ball position as
    it crosses homeplate. Returns 1 if it is a strike.

    Get the x and z position of the ball at home plate and set as either a
    ball or strike regardless of whether or not the batter swung. Zone bounds
    entered in as a list: [top, bottom]. Note that x
    """

    strike_zone_half = 8.5
    ball_diameter = 1.57
    zone_width = (strike_zone_half + ball_diameter) / 12 # convert to ft

    if (abs(x) < zone_width) & (z < zone_bounds[0]) & (z > zone_bounds[1]):
        return 1
    else:
        return 0


def parse_count(x):
    """Create separate columns for balls and strikes in the count"""
    series = x.str.split('-', expand=True)
    series.columns = ['balls', 'strikes']
    return series


def parse_trajectories(x):
    """Conversion of trajectory data from json to an array"""
    return np.array(json.loads(x))


def compute_release_time(vy0, actual=55):
    """Compute how far the ball has travelled between the actual release point
    (default is 55ft as per consensus) and the initial point recorded by
    pitchfx. X is
    """

    dist = 50 - actual
    ms_per_foot = 1000 / vy0

    return ms_per_foot * dist


def get_location(x, time=180, from_plate=False):
    """Get pitch location at specified time; generate an x, y, z location
    array
    """
    ix = int(time/10)
    try:
        if from_plate:
            # index from end of trajectory (i.e. home plate)
            return parse_trajectories(x)[:, -ix, :]
        else:
            return parse_trajectories(x)[:, ix, :]
    except IndexError:
        print('Warning: Insufficient path. Shape {}'.format(parse_trajectories(x).shape))
        return np.nan


def expand_location(x, colnames=['tx', 'ty', 'tz']):
    """Create x, y, z columns from location array"""
    x = x.apply(np.ravel)
    x = x.apply(pd.Series)
    x.columns = colnames
    return x

# def main():

if __name__ == '__main__':
    # main()
    db = PitchDB()
    df = generate_table(db)

    print('Parsing counts...')
    counts = parse_count(df['count'])

    print('Computing adjusted strike zones...')
    zone_height = compute_zone_height(df)
    df = df.merge(zone_height, on='batter')

    df['time_from_release'] = compute_release_time(df['vy0'])
    mean_time_from_release = np.around(df['time_from_release'].mean(), -1)
    print(
        'Rounded average distance from consensus '
        'release point of 55ft: {}ms'.format(mean_time_from_release)
    )

    print("Computing strikes...")
    is_strike = df.apply(
        lambda x: call_pitch(x['px'], x['pz'], [
                             x['adj_sz_top'], x['adj_sz_bot']]),
        axis=1
    )
    is_strike.name = 'is_strike'

    print('Computing location at 140ms from y0; total t approx. 175ms')
    loc_175 = df['trajectories'].apply(lambda x: get_location(x, time=140))

    print('Computing location at 190ms from y0; total t approx. 225ms')
    loc_225 = df['trajectories'].apply(lambda x: get_location(x, time=190))

    df.drop('trajectories', axis=1, inplace=True)

    df = pd.concat(
        [df, expand_location(loc_175, ['tx_175', 'ty_175', 'tz_175']),
         expand_location(loc_225, ['tx_225', 'ty_225', 'tz_225']),
         is_strike, counts], axis=1)

    db.create(df, 'dataset')
    db.close()

