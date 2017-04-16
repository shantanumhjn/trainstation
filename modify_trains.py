import db
import add_wagon

def disassemble(loco_id):
    db.open()
    cur = db.conn.cursor()
    sql = '''
        update wagons
           set locomotive_id = null
         where locomotive_id = ?
    '''
    cur.execute(sql, (loco_id,))
    sql = '''
        update locomotives
           set operation = ?
         where id = ?
    '''
    cur.execute(sql, ("unused", loco_id))
    db.commit()
    db.close()

def remove_wagons(loco_id, wagons):
    for wagon in wagons:
        wagon_type_id = add_wagon.get_wagon_type_id(str(wagon["name"]))
        if wagon_type_id is None:
            print "could not find wagon:", str(wagon["name"])
            continue
        sql = '''
            select id
              from wagons
             where locomotive_id = ?
               and wagon_type_id = ?
             limit ?
        '''
        db.open()
        cur = db.conn.cursor()
        cur.execute(sql, (loco_id, wagon_type_id, wagon.get("count", 1)))
        wagon_ids = []
        for res in cur.fetchall():
            wagon_ids.append((loco_id, res[0]))
        print "removing", len(wagon_ids), str(wagon["name"]), "wagons"
        sql = '''
            update wagons
               set locomotive_id = null
             where locomotive_id = ?
               and id = ?
        '''
        cur.executemany(sql, wagon_ids)
        db.commit()
        db.close()

def add_wagons(loco_id, wagons):
    for wagon in wagons:
        wagon_type_id = add_wagon.get_wagon_type_id(str(wagon["name"]))
        if wagon_type_id is None:
            print "could not find wagon:", str(wagon["name"])
            continue
        sql = '''
            select id
              from wagons
             where locomotive_id is null
               and wagon_type_id = ?
             limit ?
        '''
        db.open()
        cur = db.conn.cursor()
        cur.execute(sql, (wagon_type_id, wagon.get("count", 1)))
        wagon_ids = []
        for res in cur.fetchall():
            wagon_ids.append((loco_id, res[0]))
        print "adding", len(wagon_ids), str(wagon["name"]), "wagons"
        sql = '''
            update wagons
               set locomotive_id = ?
             where locomotive_id is null
               and id = ?
        '''
        cur.executemany(sql, wagon_ids)
        db.commit()
        db.close()

if __name__ == "__main__":
    # disassemble(1)
    remove_wagons(1, [{"name": "Inox", "count": 1}])
    add_wagons(1, [{"name": "Inox", "count": 1}])
