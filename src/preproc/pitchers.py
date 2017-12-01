"""Generate pitcher stats for analysis"""

import sys
import pandas as pd
import numpy as np

sys.path.append('../utils')
from PitchDB import PitchDB


def OBA(x):
    """Opponent batting average"""
    return np.around(x['H'] / x['AB'], decimals=3)

def OOBP(x):
    """Opponent on-base percentage"""

    return ((x['H'] + x['BB'] + x['HBP']) /
            (x['AB'] + x['BB'] + x['HBP'] + x['SF']))

if __name__ == '__main__':

    db = PitchDB()
    df = db.query('select * from pitchers')
    db.close()

    df['OBA'] = OBA(df)
    df['OOBP'] = OOBP(df)

    # set criteria for what pitchers to include
    criteria = 'BF >= 150'
    selected = df.query(criteria)
    selected.to_csv('../../data/pitchers.csv')
