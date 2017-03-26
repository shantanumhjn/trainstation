import db
import json
from math import ceil

wagon_metadata = {}
locomotive_metadata = {}

def load_wagons():
    cur = db.conn.cursor()
    sql = 'select id, type, name, capacity, profit, cargo from wagon_types'
    cur.execute(sql)
    for res in cur.fetchall():
        wagon_info = {}
        wagon_info['type'] = res[1]
        wagon_info['name'] = res[2]
        wagon_info['capacity'] = res[3]
        wagon_info['profit'] = res[4]
        wagon_info['cargo'] = res[5]
        wagon_metadata[res[0]] = wagon_info

def load_locomotives():
    cur = db.conn.cursor()
    sql = 'select id, name, type, power, bonus_on, bonus from locomotive_types'
    cur.execute(sql)
    for res in cur.fetchall():
        info = {}
        info['name'] = res[1]
        info['type'] = res[2]
        info['power'] = res[3]
        info['bonus_on'] = res[4]
        info['bonus'] = res[5]
        locomotive_metadata[res[0]] = info

def load_metadata():
    db.open()
    load_wagons()
    load_locomotives()
    db.close()

def populate_trains_info(trains):
    all_trains = []
    for kee, val in trains.items():
        loco = {}
        loco = locomotive_metadata.get(kee[1]).copy()
        loco['id'] = kee[0]
        wagons = []
        wagon_ids = {}
        for w in val:
            wagon_ids[w[1]] = wagon_ids.get(w[1], 0) + 1
        for wid, num in wagon_ids.items():
            this_wagon = wagon_metadata[wid].copy()
            this_wagon['count'] = num
            wagons.append(this_wagon)
        # print loco['name'], wagons
        train = {}
        train['locomotive'] = loco
        train['wagons'] = wagons
        all_trains.append(train)
    return all_trains

def get_trains():
    db.open()
    cur = db.conn.cursor()
    trains_dict = {}
    sql = '''
        select l.id, l.locomotive_type_id, w.id, w.wagon_type_id
          from wagons w,
               locomotives l
         where w.locomotive_id = l.id
         order by l.id, w.id
    '''
    cur.execute(sql)
    all_res = cur.fetchall()
    for res in all_res:
        loco = (res[0], res[1])
        new_wagon = (res[2], res[3])
        wagons = trains_dict.get(loco, [])
        wagons.append(new_wagon)
        trains_dict[loco] = wagons
    db.close()
    return populate_trains_info(trains_dict)

def print_trains(trains):
    output = ""
    for train in trains:
        format_template = "{{:<{}}}"
        loco = train['locomotive']
        loco_name = str(loco['name']) + '(' + str(loco.get('id', 0)) + ')'
        loco_str_size = max(len(loco_name), len(str(loco['type'])), len(str(loco['power']))) + 5
        w_names = []
        w_types = []
        w_capacity = []
        w_sizes = []
        w_count = 0
        for wagon in train['wagons']:
            w_count += wagon.get('count', 1)
            w_names.append(str(wagon['name']) + ' x ' + str(wagon.get('count', 1)))
            w_types.append(str(wagon['type']))
            cargo = wagon.get('cargo')
            capacity = wagon.get('capacity')
            profit = wagon.get('profit')
            if cargo is not None:
                w_capacity.append(str(cargo))
            else:
                capacity = str(capacity) + ' (' + str(int(ceil(capacity*(1+(profit/100.0))))) + ')'
                w_capacity.append(capacity)
            w_sizes.append(max(len(w_names[len(w_names)-1]), len(w_types[len(w_types)-1]), len(w_capacity[len(w_capacity)-1])) + 3)
        format_template *= len(w_names) + 1
        format_template = format_template.format(loco_str_size, *w_sizes)

        output += format_template.format(loco_name, *w_names) + '\n'
        output += format_template.format(loco['type'], *w_types) + '\n'
        output += format_template.format(str(w_count) + '/' + str(loco['power']), *w_capacity) + '\n\n'
    print output

if __name__ == '__main__':
    load_metadata()
    trains = get_trains()
    # print json.dumps(trains, indent = 2)
    print_trains(trains)
