import add_wagon
import add_locomotive
import json
import db

def add_train(loco_id, wagon_ids):
    payload = []
    for wids in wagon_ids:
        for wid in wids:
            payload.append((loco_id, wid))
    sql = 'update wagons set locomotive_id = ? where id = ?'
    db.open()
    cur = db.conn.cursor()
    cur.executemany(sql, payload)
    db.commit()
    db.close()

def add_train_json(js):
    loco = js['locomotive']
    loco_id = add_locomotive.add_locomotives_json(loco)
    wagon_ids = []
    for wagon in js['wagons']:
        wagon_ids.append(add_wagon.add_wagon_json(wagon))
    # print 'wagon ids:', wagon_ids
    add_train(loco_id[0], wagon_ids)

def load_train_file(file_name):
    with open(file_name) as f:
        content = f.read()
        js = json.loads(content)
        for entry in js:
            add_train_json(entry)

if __name__ == '__main__':
    load_train_file('data/trains.json')
