"""Preprocessing module"""

import pandas as pd
import numpy as np
import json
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


# def query_main_table():
#     sql = (




#     )

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

    q1 = (
        'select batter_name, pitcher_name, gameday_link, num '
        'from atbat'
    )

    atbat = db.query(q1)

    q2 = (
        'select count, pitch_type, gameday_link, num, event_num, play_guid '
        'from pitch'
    )

    pitch = db.query(q2)

    q3 = (
        'select trajectories, gameday_link, event_num, play_guid '
        'from snapshots'
    )

    snapshots = db.query(q3)

    df = pitch.merge(snapshots, on=('gameday_link', 'event_num', 'play_guid'))
    df2 = df.merge(atbat, on=('gameday_link', 'num'))
