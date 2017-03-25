import db
import json

def add_locomotive_type(name, l_type, power):
    sql = '''
        insert into locomotive_types (name, type, power)
        values (?, ?, ?)
    '''
    db.open()
    cur = db.conn.cursor()
    cur.execute(sql, (name, l_type, power))
    last_id = cur.lastrowid
    db.commit()
    db.close()
    return last_id

def get_locomotive_type_id(name):
    l_id = None
    sql = 'select id from locomotive_types where name = ?'
    db.open()
    cur = db.conn.cursor()
    cur.execute(sql, (name, ))
    res = cur.fetchone()
    if res is not None:
        l_id = res[0]
    db.close()
    return l_id

def add_locomotive(name, l_type = None, power = None):
    sql = '''
        insert into locomotives (locomotive_type_id)
        values (?)
    '''
    l_id = get_locomotive_type_id(name)
    if l_id is None:
        l_id = add_locomotive_type(name, l_type, power)
    db.open()
    cur = db.conn.cursor()
    cur.execute(sql, (l_id, ))
    last_id = cur.lastrowid
    db.commit()
    db.close()
    return last_id

def add_locomotives_json(js):
    count = js.get('count', 1)
    ids = []
    for i in range(count):
        name = js.get('name')
        l_type = js.get('type')
        power = js.get('power')
        ids.append(add_locomotive(name, l_type, power))
    return ids

def load_locomotives_file(file_name):
    with open(file_name) as f:
        content = f.read()
        js = json.loads(content)
        for i in range(len(js)):
            add_locomotives_json(js[i])

if __name__ == '__main__':
    load_locomotives_file('locomotives.json')
