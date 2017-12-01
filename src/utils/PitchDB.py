"""Database configuration object for project.

Note: I'm aware it's generally not good practice to put database configurations
in version control. But since we don't have usernames/passwords and this is
just a local sqlite database, this shouldn't be an issue. It is likely that
future versions of this project, in which the database will be used for other
projects (and thus likely migrated to a PostgreSQL database), configuration
will be done separate from version control. -DG
"""

import sqlite3
import pandas as pd


class PitchDB(object):

    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = sqlite3.connect('../../data/pitches.sqlite3')

    def query(self, query, **kwargs):
        return pd.read_sql(query, self._db_connection, **kwargs)

    def create(self, data, name, if_exists='replace', index=False, **kwargs):
        data.to_sql(name, con=self._db_connection, if_exists=if_exists,
                    index=index, **kwargs)

    def close(self):
        self._db_connection.close()

    def __del__(self):
        self._db_connection.close()
