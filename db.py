import sqlite3

conn = None
db_name = 'trainstation.db'
def open():
    global conn
    if conn is None:
        conn = sqlite3.connect(db_name)
        conn.execute('pragma foreign_keys = ON')

def close():
    global conn
    conn.close()
    conn = None

def commit():
    global conn
    conn.commit()

if __name__ == '__main__':
    open()
    close()
