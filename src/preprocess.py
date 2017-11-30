"""Preprocessing module"""

import pandas as pd
import numpy as np
import json
import re
import sqlite3
import numba


def generate_table(db):
    """Queries to pull in appropriate data and join for main table"""
    q1 = (
        'select gameday_link, num, pitcher, pitcher_name, batter, batter_name, '
        'b, s, o, p_throws, stand '
        'from atbat'
    )
    q2 = (
        'select num, event_num, play_guid, count, type, pitch_type, gameday_link, '
        'sz_top, sz_bot, px, pz, spin_rate, spin_dir, vx0, vy0, vz0 '
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


def call_pitch(x, z, zone_bounds):
    """Determine if pitch is a strike or a ball based on ball position as
    it crosses homeplate.

    Get the x and z position of the ball at home plate and set as either a
    ball or strike regardless of whether or not the batter swung. Zone bounds
    entered in as a list: [top, bottom]
    """
    if (abs(x) < 8.5) & (z < zone_bounds[0]) & (z > zone_bounds[1]):
        return 's'
    else:
        return 'b'

def parse_count(x):
    """Create separate columns for balls and strikes in the count"""
    series = x.str.split('-', expand=True)
    series.columns = ['balls', 'strike']
    return series


def parse_trajectories(x):
    """Conversion of trajectory data from json to an array"""
    return np.array(json.loads(x))


def get_location(x, time=180, from_plate=True):
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


def expand_location(x):
    """Create x, y, z columns from location array"""
    x = x.apply(np.ravel)
    x = x.apply(pd.Series)
    x.columns = ['tx', 'ty', 'tz']
    return x


if __name__ == '__main__':

    db = PitchDB()
    df = generate_table(db)

    counts = parse_count(df['count'])
    df = pd.concat([df, counts], axis=1)
    loc = df['trajectories'].apply(lambda x: get_location(x))
    df = pd.concat([df, expand_location(loc)], axis=1)

    db.create(df, 'features')
    db.close()

