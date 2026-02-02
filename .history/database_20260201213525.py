import sqlite3

def get_db():
    conn = sqlite3.connect('srs_vocab.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
