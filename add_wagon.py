import json
import db

def add_wagon_type(wagon_type, name, capacity, profit, cargo):
    db.open()
    cur = db.conn.cursor()
    sql = """
        insert into wagon_types (type, name, capacity, profit, cargo)
        values (?, ?, ?, ?, ?)
        """
    cur.execute(sql, (wagon_type,name, capacity, profit, cargo))
    last_id = cur.lastrowid
    db.commit()
    db.close()
    return last_id

def get_wagon_type_id(name):
    db.open()
    cur = db.conn.cursor()
    wagon_id = None
    sql = 'select id from wagon_types where name = ?'
    cur.execute(sql, (name, ))
    res = cur.fetchone()
    if res is not None:
        wagon_id = res[0]
    db.close()
    return wagon_id

def add_wagon(name, wagon_type = None, capacity = None, profit = None, cargo = None):
    sql = '''
        insert into wagons (wagon_type_id)
        values (?)
    '''
    wagon_id = get_wagon_type_id(name)
    if wagon_id is None:
        wagon_id = add_wagon_type(wagon_type, name, capacity, profit, cargo)
    db.open()
    cur = db.conn.cursor()
    cur.execute(sql, (wagon_id, ))
    last_id = cur.lastrowid
    db.commit()
    db.close()
    return last_id

def add_wagon_json(wagon_dict):
    count = wagon_dict.get("count", 1)
    ids = []
    for i in range(count):
        wagon_type = wagon_dict.get("type")
        name = wagon_dict.get("name")
        capacity = wagon_dict.get("capacity")
        profit = wagon_dict.get("profit")
        cargo = wagon_dict.get("cargo")
        ids.append(add_wagon(name, wagon_type, capacity, profit, cargo))
    return ids

def load_wagons_file(file_name):
    with open(file_name, 'r') as f:
        content = f.read()
        js = json.loads(content)
        for i in range(len(js)):
            this_entry = js[i]
            add_wagon_json(this_entry)

if __name__ == '__main__':
    # add_passenger_wagon('Grasshopper 1st', 200, 200)
    load_wagons_file('wagons1.json')
