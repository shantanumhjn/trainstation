import db

db.open()
cur = db.conn.cursor()

tables = 'trains, train_types, wagons, wagon_types, locomotives, locomotive_types'
table_list = tables.split(',')

for table in table_list:
    cur.execute("delete from " + table)

cur.execute("vacuum");
cur.close()
db.close()
