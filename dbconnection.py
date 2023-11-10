import sqlite3


class DBConnection:
    def __init__(self, database_file="time_tracker.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        connection.row_factory = sqlite3.Row
        return connection