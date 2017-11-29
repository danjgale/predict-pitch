"""Preprocessing module"""

import pandas as pd
import numpy as np
import json
import re
import sqlite3


class PitchDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = sqlite3.connect('../data/pitches.sqlite3')

    def query(self, query, **kwargs):
        return pd.read_sql(query, self._db_connection, **kwargs)

    def close(self):
        self._db_connection.close()

    def __del__(self):
        self._db_connection.close()


def generate_table(db):
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
    return tuple(map(int, re.findall(r'\d', x)))


def parse_trajectories(x):
    return np.array(json.loads(x))


def get_location(x, time=180, from_plate=True):
    """Get pitch location at specified time"""
    ix = int(time/10)
    if from_plate:
        # index from end of trajectory (i.e. home plate)
        return parse_trajectories(x)[:, -ix, :]
    else:
        return parse_trajectories(x)[:, ix, :]

if __name__ == '__main__':

    db = PitchDB()
    main_df = generate_table(db)
