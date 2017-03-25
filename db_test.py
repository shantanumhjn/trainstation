import db

print dir(db)
db.open()
print type(db.conn)
db.close()
print type(db.conn)
